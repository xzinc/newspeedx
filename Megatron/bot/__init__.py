import logging
from typing import Dict, Any  # Used for type hints

# pyromod is required for the bot to work properly
from pyromod import listen  # Required for the bot to work
from pyrogram import Client
from pyrogram.session import Session

from ..vars import Var

# Fix for "msg_id is too low" error by setting a time offset
# This is critical for the bot to work properly

# Set a very large default time offset (60 seconds in the future)
# This ensures that msg_id will always be high enough
Session.time_offset = 60
logging.info("Set default Pyrogram session time offset to 60 seconds")

# Try to get the time offset from environment variable
import os
env_offset = os.environ.get('PYROGRAM_TIME_OFFSET')
if env_offset:
    try:
        env_offset = int(env_offset)
        if env_offset > 0:
            Session.time_offset = env_offset
            logging.info(f"Updated Pyrogram session time offset to {env_offset} seconds from environment variable")
    except ValueError:
        logging.warning(f"Invalid PYROGRAM_TIME_OFFSET value: {env_offset}")

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
