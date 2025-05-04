import re
import time
import math
import logging
import secrets
import mimetypes  # Used for guessing MIME types
from aiohttp import web
from aiohttp.http_exceptions import BadStatusLine

from Megatron.bot import multi_clients, work_loads
from Megatron.server.exceptions import FIleNotFound, InvalidHash
from Megatron import Var, utils, StartTime, __version__, bot_info


routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(_):
    return web.json_response(
        {
            "server_status": "running",
            "uptime": utils.get_readable_time(time.time() - StartTime),
            "telegram_bot": "@" + bot_info.username,
            "connected_bots": len(multi_clients),
            "loads": dict(
                ("bot" + str(c + 1), l)
                for c, (_, l) in enumerate(
                    sorted(work_loads.items(), key=lambda x: x[1], reverse=True)
                )
            ),
            "version": __version__,
        }
    )


@routes.get(r"/{path:\S+}", allow_head=True)
async def stream_handler(request: web.Request):
    """
    Handle streaming requests.
    This function parses the URL path and extracts the message ID and secure hash.
    It then calls media_streamer to stream the file.

    Args:
        request: The aiohttp request object

    Returns:
        An aiohttp response object

    Raises:
        web.HTTPForbidden: If the hash is invalid
        web.HTTPNotFound: If the file is not found
        web.HTTPInternalServerError: If there's an error streaming the file
    """
    try:
        # Get the path from the request
        path = request.match_info["path"]
        logging.info(f"Received streaming request for path: {path}")

        # Try to match the short URL format first (hash + message_id)
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            message_id = int(match.group(2))
            logging.info(f"Parsed short URL format: hash={secure_hash}, message_id={message_id}")
        else:
            # Try to match the long URL format (message_id/filename?hash=hash)
            message_id_match = re.search(r"(\d+)(?:\/\S+)?", path)
            if not message_id_match:
                logging.error(f"Failed to parse message ID from path: {path}")
                raise web.HTTPBadRequest(text="Invalid URL format")

            message_id = int(message_id_match.group(1))
            secure_hash = request.rel_url.query.get("hash")

            if not secure_hash:
                logging.error(f"No hash provided in query parameters for path: {path}")
                raise web.HTTPBadRequest(text="Hash parameter is required")

            logging.info(f"Parsed long URL format: message_id={message_id}, hash={secure_hash}")

        # Stream the media
        return await media_streamer(request, message_id, secure_hash)

    except InvalidHash as e:
        logging.error(f"Invalid hash: {e.message}")
        raise web.HTTPForbidden(text=e.message)

    except FIleNotFound as e:
        logging.error(f"File not found: {e.message}")
        raise web.HTTPNotFound(text=e.message)

    except (AttributeError, BadStatusLine, ConnectionResetError) as e:
        logging.error(f"Connection error: {str(e)}")
        raise web.HTTPInternalServerError(text=f"Connection error: {str(e)}")

    except Exception as e:
        logging.critical(f"Unexpected error in stream_handler: {str(e)}")
        logging.critical(e.with_traceback(None))
        raise web.HTTPInternalServerError(text=f"Internal server error: {str(e)}")

class_cache = {}

async def media_streamer(request: web.Request, message_id: int, secure_hash: str):
    """
    Stream a media file from Telegram.
    This function handles the actual streaming of the file.

    Args:
        request: The aiohttp request object
        message_id: The message ID to stream from
        secure_hash: The secure hash to verify

    Returns:
        An aiohttp response object

    Raises:
        InvalidHash: If the hash is invalid
        FIleNotFound: If the file is not found
    """
    try:
        # Get the range header
        range_header = request.headers.get("Range", 0)
        logging.info(f"Streaming message {message_id} with hash {secure_hash}, range: {range_header}")

        # Select the client with the lowest workload
        index = min(work_loads, key=work_loads.get)
        faster_client = multi_clients[index]

        if Var.MULTI_CLIENT:
            logging.info(f"Client {index} is now serving {request.remote}")

        # Get or create a ByteStreamer object
        if faster_client in class_cache:
            tg_connect = class_cache[faster_client]
            logging.debug(f"Using cached ByteStreamer object for client {index}")
        else:
            logging.debug(f"Creating new ByteStreamer object for client {index}")
            tg_connect = utils.ByteStreamer(faster_client)
            class_cache[faster_client] = tg_connect

        # Get the file properties
        logging.debug(f"Getting file properties for message {message_id}")
        file_id = await tg_connect.get_file_properties(message_id)
        logging.debug(f"Got file properties for message {message_id}")

        # Verify the hash
        if not hasattr(file_id, 'unique_id') or not file_id.unique_id:
            logging.error(f"File ID has no unique_id attribute for message {message_id}")
            raise InvalidHash

        file_hash = file_id.unique_id[:6]
        if file_hash != secure_hash:
            logging.error(f"Invalid hash for message {message_id}: expected {file_hash}, got {secure_hash}")
            raise InvalidHash

        logging.info(f"Hash verified for message {message_id}")

        # Get the file size
        file_size = getattr(file_id, 'file_size', 0)
        if not file_size:
            logging.warning(f"File size is 0 for message {message_id}")

        # Parse the range header
        if range_header:
            try:
                from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
                from_bytes = int(from_bytes)
                until_bytes = int(until_bytes) if until_bytes else file_size - 1
                logging.debug(f"Parsed range header: from={from_bytes}, until={until_bytes}")
            except Exception as e:
                logging.error(f"Failed to parse range header: {e}")
                from_bytes = 0
                until_bytes = file_size - 1
        else:
            from_bytes = request.http_range.start or 0
            until_bytes = request.http_range.stop or file_size - 1
            logging.debug(f"Using http_range: from={from_bytes}, until={until_bytes}")

        # Calculate streaming parameters
        req_length = until_bytes - from_bytes
        new_chunk_size = await utils.chunk_size(req_length)
        offset = await utils.offset_fix(from_bytes, new_chunk_size)
        first_part_cut = from_bytes - offset
        last_part_cut = (until_bytes % new_chunk_size) + 1
        part_count = math.ceil(req_length / new_chunk_size)

        logging.debug(f"Streaming parameters: chunk_size={new_chunk_size}, offset={offset}, first_part_cut={first_part_cut}, last_part_cut={last_part_cut}, part_count={part_count}")

        # Get the file generator
        body = tg_connect.yield_file(
            file_id, index, offset, first_part_cut, last_part_cut, part_count, new_chunk_size
        )

        # Determine the MIME type and file name
        mime_type = getattr(file_id, 'mime_type', None) or "application/octet-stream"
        file_name = getattr(file_id, 'file_name', None) or f"{secrets.token_hex(2)}.unknown"

        # Determine the content disposition
        disposition = "attachment"
        if mime_type and ("video/" in mime_type or "audio/" in mime_type):
            disposition = "inline"

        logging.info(f"Streaming file: name={file_name}, mime_type={mime_type}, disposition={disposition}")

        # Create the response
        return_resp = web.Response(
            status=206 if range_header else 200,
            body=body,
            headers={
                "Content-Type": f"{mime_type}",
                "Range": f"bytes={from_bytes}-{until_bytes}",
                "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
                "Content-Disposition": f'{disposition}; filename="{file_name}"',
                "Accept-Ranges": "bytes",
            },
        )

        # Add Content-Length header for non-range requests
        if return_resp.status == 200:
            return_resp.headers.add("Content-Length", str(file_size))

        logging.info(f"Streaming response created for message {message_id}")
        return return_resp

    except InvalidHash:
        logging.error(f"Invalid hash for message {message_id}")
        raise

    except FIleNotFound:
        logging.error(f"File not found for message {message_id}")
        raise

    except Exception as e:
        logging.error(f"Error in media_streamer for message {message_id}: {e}")
        raise web.HTTPInternalServerError(text=f"Error streaming file: {str(e)}")
