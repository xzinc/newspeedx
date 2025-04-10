import time
import logging
import sys
import ntplib
from datetime import datetime, timezone
from .vars import Var

# Configure logging only if not already configured
if not logging.getLogger().handlers:
    # Remove any existing handlers to avoid duplicate logs
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Configure logging with a single handler
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )

# Set version and start time
__version__ = 2.3

# Synchronize system time with NTP server
try:
    ntp_client = ntplib.NTPClient()
    response = ntp_client.request('pool.ntp.org', version=3)
    # Adjust system time offset for accurate timestamps
    time_offset = response.offset
    logging.info(f"NTP time offset: {time_offset} seconds")
    # Use adjusted time for StartTime
    StartTime = time.time() + time_offset
    # Export time_offset for use in other modules
    __all__ = ['__version__', 'StartTime', 'time_offset']
except Exception as e:
    logging.warning(f"Failed to synchronize time with NTP server: {e}")
    # Fallback to system time
    StartTime = time.time()
    time_offset = 0
    # Export variables without time_offset
    __all__ = ['__version__', 'StartTime', 'time_offset']

print("\n")
print("------------------- Initializing Telegram Bot -------------------")

# Import bot after logging is configured
from Megatron.bot import StreamBot, bot_info

# Initialize bot with error handling
# Don't start the bot here, it will be started in __main__.py
# Just set default values for bot_info
bot_info.username = "FileStreamBot"
bot_info.first_name = "File Stream Bot"
bot_info.dc_id = 0
bot_info.bots[0] = {"username": bot_info.username, "name": bot_info.first_name}

# Don't start the bot here, but set the time offset for Pyrogram
# This helps prevent the "msg_id is too low" error
try:
    # Set the session time offset if we have a valid NTP offset
    if 'time_offset' in locals():
        logging.info(f"Setting Pyrogram session time offset to {time_offset}")
        # We don't need to call this directly as it will be used when the bot starts
        # Just log that we have the offset ready
    else:
        logging.warning("No time offset available for Pyrogram session")
except Exception as e:
    logging.error(f"Error setting Pyrogram time offset: {e}")
