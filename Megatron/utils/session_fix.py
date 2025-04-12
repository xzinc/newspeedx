"""
Session fix for Pyrogram to handle time synchronization issues.
This module monkey patches the Pyrogram Session class to fix the "msg_id is too low" error.
"""

import logging
import time
from typing import Any

def apply_session_fix():
    """
    Apply the session fix to Pyrogram.
    This function sets a large time offset for Pyrogram to fix the "msg_id is too low" error.
    """
    try:
        # Import the Session class from Pyrogram
        from pyrogram.session import Session

        # For Pyrogram 2.x, we need to set the time offset differently
        try:
            # Try to set the time offset for Pyrogram 2.x
            # In Pyrogram 2.x, the time_offset is a property of the Session class
            # Set a very large time offset (300 seconds) to ensure the msg_id is high enough
            Session.time_offset = 300
            logging.info("Set time_offset to 300 seconds for Pyrogram 2.x")

            # Also try to patch the get_msg_id method if it exists
            if hasattr(Session, 'get_msg_id'):
                original_get_msg_id = Session.get_msg_id

                def patched_get_msg_id(self):
                    # Add a large time offset to the current time
                    # This ensures that the msg_id will always be high enough
                    current_time = int(time.time()) + 300
                    msg_id = (current_time * 2**32) + self.msg_id_offset
                    self.msg_id_offset += 4
                    return msg_id

                # Replace the original method with our patched version
                Session.get_msg_id = patched_get_msg_id
                logging.info("Patched get_msg_id method for Pyrogram 2.x")
        except Exception as e:
            logging.warning(f"Failed to patch Pyrogram 2.x: {e}")

            # Fall back to setting the time offset directly
            # This works for both Pyrogram 1.x and 2.x
            Session.time_offset = 300
            logging.info("Set time_offset to 300 seconds as fallback")

        # Also set the time offset in the environment variable
        # This is used by some parts of Pyrogram
        import os
        os.environ['PYROGRAM_TIME_OFFSET'] = '300'
        logging.info("Set PYROGRAM_TIME_OFFSET environment variable to 300")

        logging.info("Successfully applied session fix to Pyrogram")
        return True
    except Exception as e:
        logging.error(f"Failed to apply session fix to Pyrogram: {e}")
        return False
