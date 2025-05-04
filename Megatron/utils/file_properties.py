from typing import Any, Optional

from pyrogram import Client
from pyrogram.types import Message
from pyrogram.file_id import FileId
from pyrogram.raw.types.messages import Messages

from Megatron.server.exceptions import FIleNotFound


async def parse_file_id(message: "Message") -> Optional[FileId]:
    media = get_media_from_message(message)
    if media:
        return FileId.decode(media.file_id)

async def parse_file_unique_id(message: "Messages") -> Optional[str]:
    media = get_media_from_message(message)
    if media:
        return media.file_unique_id

async def get_file_ids(client: Client, chat_id: int, message_id: int) -> Optional[FileId]:
    """
    Get file IDs and properties from a message.
    This is used to generate download links and stream files.

    Args:
        client: The Pyrogram client
        chat_id: The chat ID where the message is located
        message_id: The message ID to get file IDs from

    Returns:
        FileId object with additional properties

    Raises:
        FIleNotFound: If the message is empty or doesn't contain media
    """
    try:
        # Get the message from the chat
        message = await client.get_messages(chat_id, message_id)

        # Check if the message exists and contains media
        if message.empty:
            import logging
            logging.error(f"Message {message_id} in chat {chat_id} is empty")
            raise FIleNotFound

        # Get the media from the message
        media = get_media_from_message(message)
        if not media:
            import logging
            logging.error(f"Message {message_id} in chat {chat_id} doesn't contain media")
            raise FIleNotFound

        # Parse the file IDs
        file_unique_id = await parse_file_unique_id(message)
        file_id = await parse_file_id(message)

        if not file_id:
            import logging
            logging.error(f"Failed to parse file ID for message {message_id} in chat {chat_id}")
            raise FIleNotFound

        # Add additional properties to the FileId object
        setattr(file_id, "file_size", getattr(media, "file_size", 0))
        setattr(file_id, "mime_type", getattr(media, "mime_type", ""))
        setattr(file_id, "file_name", getattr(media, "file_name", ""))
        setattr(file_id, "unique_id", file_unique_id or "")

        import logging
        logging.info(f"Successfully got file IDs for message {message_id} in chat {chat_id}")
        return file_id

    except Exception as e:
        import logging
        logging.error(f"Error in get_file_ids: {e}")
        raise FIleNotFound

def get_media_from_message(message: "Message") -> Any:
    media_types = (
        "audio",
        "document",
        "photo",
        "sticker",
        "animation",
        "video",
        "voice",
        "video_note",
    )
    for attr in media_types:
        media = getattr(message, attr, None)
        if media:
            return media


def get_hash(media_msg: Message) -> str:
    """
    Get a unique hash for a media message.
    This is used to create a secure link that can only be accessed by someone who knows the hash.
    """
    try:
        media = get_media_from_message(media_msg)
        if media:
            unique_id = getattr(media, "file_unique_id", "")
            if unique_id:
                return unique_id[:6]
            else:
                # Fallback to a hash of the message ID if no file_unique_id
                import hashlib
                return hashlib.md5(str(media_msg.id).encode()).hexdigest()[:6]
        else:
            # Fallback to a hash of the message ID if no media
            import hashlib
            return hashlib.md5(str(media_msg.id).encode()).hexdigest()[:6]
    except Exception as e:
        # Log the error and return a fallback hash
        import logging
        logging.error(f"Error in get_hash: {e}")
        import hashlib
        return hashlib.md5(str(getattr(media_msg, 'message_id', 0)).encode()).hexdigest()[:6]

def get_name(media_msg: Message) -> str:
    """
    Get the file name from a media message.
    This is used in the download URL.
    """
    try:
        media = get_media_from_message(media_msg)
        if media:
            file_name = getattr(media, "file_name", "")
            if file_name:
                return file_name
            else:
                # Fallback to a generic name based on media type
                for attr in ["audio", "document", "photo", "video", "animation", "voice", "video_note", "sticker"]:
                    if hasattr(media_msg, attr):
                        return f"{attr}_{media_msg.id}"
                return f"file_{media_msg.id}"
        else:
            # Fallback to a generic name
            return f"file_{media_msg.id}"
    except Exception as e:
        # Log the error and return a fallback name
        import logging
        logging.error(f"Error in get_name: {e}")
        return f"file_{getattr(media_msg, 'message_id', 0)}"
