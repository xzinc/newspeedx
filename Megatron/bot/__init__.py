import logging

# Import Pyrogram and related modules
from pyrogram import Client

# For Pyrogram 2.x, we need to import pyromod differently
# We're using a try/except block to handle different versions of pyromod
# and to continue even if pyromod is not available
try:
    # First try the Pyrogram 2.x import style
    try:
        # This import style is for pyromod with Pyrogram 2.x
        # pylint: disable=import-error
        # type: ignore
        from pyromod.listen import Client as ListenClient
        # Monkey patch the Client class
        Client = ListenClient
        logging.info("Using pyromod for Pyrogram 2.x")
    except ImportError:
        # Fall back to Pyrogram 1.x import style
        # pylint: disable=import-error
        # type: ignore
        from pyromod import listen
        logging.info("Using pyromod for Pyrogram 1.x")
except Exception as e:
    # If all else fails, try to continue without pyromod
    logging.warning(f"pyromod not found, some features may not work: {e}")

# Import Session for time offset fix
from pyrogram.session import Session

from ..vars import Var

# Fix for "msg_id is too low" error by setting a time offset
# This is critical for the bot to work properly

# Set a very large default time offset (300 seconds in the future)
# This ensures that msg_id will always be high enough
Session.time_offset = 300
logging.info("Set default Pyrogram session time offset to 300 seconds")

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

# Initialize the bot with parameters compatible with Pyrogram 2.0.106
StreamBot = Client(
    name=Var.SESSION_NAME,  # Changed from session_name to name for Pyrogram 2.x
    api_id=Var.API_ID,
    api_hash=Var.API_HASH,
    bot_token=Var.BOT_TOKEN,
    workdir="Megatron",
    plugins={"root": "Megatron/bot/plugins"},
    sleep_threshold=Var.SLEEP_THRESHOLD
)

# Dictionary to store multiple bot clients for load balancing
# Format: {client_id: Client instance}
multi_clients = {}

# Dictionary to track work load of each client
# Format: {client_id: work_load_count}
work_loads = {}

# Bot information container
class BotInfo:
    """Container for bot information."""
    username = ""
    first_name = ""
    dc_id = 0
    bots = {}

# Initialize bot info container
bot_info = BotInfo()
