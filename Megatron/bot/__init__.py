import os
import logging
import time
from typing import Dict, Any

from pyromod import listen
from pyrogram import Client
from pyrogram.session import Session

from ..vars import Var

# Fix for "msg_id is too low" error by setting a time offset
# This is critical for the bot to work properly

# Set a large default time offset (30 seconds in the future)
# This ensures that msg_id will always be high enough
Session.time_offset = 30
logging.info("Set default Pyrogram session time offset to 30 seconds")

# Try to get a more accurate time offset if possible
try:
    # Try to get the time offset from the main module
    from .. import time_offset
    # Set the time offset for all Pyrogram sessions
    if time_offset > 0:
        Session.time_offset = time_offset
        logging.info(f"Updated Pyrogram session time offset to {time_offset} seconds from main module")
except ImportError:
    # If time_offset is not available, try to get it from NTP
    try:
        import ntplib
        ntp_client = ntplib.NTPClient()
        response = ntp_client.request('pool.ntp.org', version=3)
        # Only update if the NTP offset is positive (future time)
        if response.offset > 0:
            Session.time_offset = response.offset
            logging.info(f"Updated Pyrogram session time offset to {response.offset} seconds from NTP")
    except Exception as e:
        logging.warning(f"Could not get more accurate time offset from NTP: {e}")
        logging.info("Continuing with default time offset of 30 seconds")

StreamBot = Client(
    session_name=Var.SESSION_NAME,
    api_id=Var.API_ID,
    api_hash=Var.API_HASH,
    bot_token=Var.BOT_TOKEN,
    workdir="Megatron",
    plugins={"root": "Megatron/bot/plugins"},
    sleep_threshold=Var.SLEEP_THRESHOLD,
    workers=Var.WORKERS
)

# Dictionary to store multiple bot clients for load balancing
# Format: {client_id: Client instance}
multi_clients: Dict[int, Client] = {}

# Dictionary to track work load of each client
# Format: {client_id: work_load_count}
work_loads: Dict[int, int] = {}

# Bot information container
class BotInfo:
    """Container for bot information."""
    username: str = ""
    first_name: str = ""
    dc_id: int = 0
    bots: Dict[int, Dict[str, Any]] = {}

# Initialize bot info container
bot_info = BotInfo()
