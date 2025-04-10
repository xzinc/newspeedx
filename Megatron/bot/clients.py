import time
import ntplib
import logging
from pyrogram import Client
from pyrogram.session import Session

from Megatron.utils import TokenParser
from . import multi_clients, work_loads, StreamBot
from ..vars import Var

async def initialize_clients():
    # Fix time synchronization issues
    try:
        # Try to get time from NTP server
        ntp_client = ntplib.NTPClient()
        response = ntp_client.request('pool.ntp.org', version=3)
        time_offset = response.offset

        # Set the time offset for all Pyrogram sessions
        Session.time_offset = time_offset
        logging.info(f"Set Pyrogram session time offset to {time_offset} seconds from NTP")
    except Exception as e:
        logging.warning(f"Failed to synchronize time with NTP: {e}")
        # Set a default time offset to avoid 'msg_id is too low' errors
        # This is a fallback solution - adding 10 seconds to current time
        time_offset = 10
        Session.time_offset = time_offset
        logging.info(f"Set default time offset to {time_offset} seconds")

    # Start the main bot
    try:
        await StreamBot.start()
        logging.info(f"Started main bot: {StreamBot.me.first_name}")
        multi_clients[0] = StreamBot
        work_loads[0] = 0
    except Exception as e:
        logging.error(f"Failed to start main bot: {e}")
        raise  # Re-raise the exception to stop initialization
    all_tokens = TokenParser().parse_from_env()
    if not all_tokens:
        print("No additional clients found, using default client")
        return
    for client_id, token in all_tokens.items():
        instance = Client(
            session_name=":memory:",
            api_id=Var.API_ID,
            api_hash=Var.API_HASH,
            bot_token=token,
            sleep_threshold=Var.SLEEP_THRESHOLD,
            no_updates=True,
        )
        try:
            multi_clients[client_id] = await instance.start()
        except Exception as e:
            print(f"Failed starting Client - {client_id}; Error: {e}")
            continue
        work_loads[client_id] = 0
        print(f"Started - Client {client_id}")
    if len(multi_clients) != 1:
        Var.MULTI_CLIENT = True
        print("Multi-Client Mode Enabled")
    else:
        print("No additional clients were initialized, using default client")
