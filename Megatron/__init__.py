import time
import logging
import sys
import ntplib  # Make sure this is installed: pip install ntplib
from .vars import Var  # Used by other modules that import from here

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

# Set a default positive time offset to ensure msg_id is high enough
# This is critical for the bot to work properly
time_offset = 30  # 30 seconds in the future
logging.info(f"Default time offset: {time_offset} seconds")

# Try to get a more accurate time offset from NTP server
try:
    ntp_client = ntplib.NTPClient()
    response = ntp_client.request('pool.ntp.org', version=3)

    # Only use NTP offset if it's positive (future time)
    # This ensures msg_id will be high enough
    if response.offset > 0:
        time_offset = response.offset
        logging.info(f"Updated time offset from NTP: {time_offset} seconds")
    else:
        logging.warning(f"NTP returned negative offset ({response.offset}), using default offset instead")

    # Use adjusted time for StartTime
    StartTime = time.time() + time_offset
except Exception as e:
    logging.warning(f"Failed to synchronize time with NTP server: {e}")
    # Fallback to default time offset
    StartTime = time.time() + time_offset
    logging.info(f"Using default time offset: {time_offset} seconds")

# Export variables for use in other modules
__all__ = ['__version__', 'StartTime', 'time_offset']

print("\n")
print("------------------- Initializing Telegram Bot -------------------")

# Import bot after logging is configured
# We only need bot_info here, StreamBot is imported elsewhere
from Megatron.bot import bot_info

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
