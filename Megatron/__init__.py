import time
import logging
import sys
import ntplib
from datetime import datetime, timezone
from .vars import Var

# Configure logging
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
from Megatron.bot.clients import StreamBot

# Initialize bot with error handling
StreamBot.start()
bot_info = StreamBot.get_me()
