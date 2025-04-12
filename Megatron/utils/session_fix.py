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
    This function monkey patches the Pyrogram Session class to fix the "msg_id is too low" error.
    """
    try:
        # Import the Session class from Pyrogram
        from pyrogram.session import Session
        
        # Store the original get_session_id method
        original_get_session_id = Session.get_session_id
        
        # Define a new get_session_id method with a large time offset
        def patched_get_session_id(self) -> int:
            """
            Get the current session ID.
            This method adds a large time offset to ensure the msg_id is high enough.
            """
            # Add a large time offset (120 seconds) to the current time
            # This ensures that the msg_id will always be high enough
            current_time = int(time.time()) + 120
            
            # Use the same formula as the original method
            new_session_id = current_time << 32
            
            logging.info(f"Generated session ID with 120-second time offset: {new_session_id}")
            return new_session_id
        
        # Replace the original method with our patched version
        Session.get_session_id = patched_get_session_id
        
        # Set a large time offset directly on the Session class
        Session.time_offset = 120
        
        logging.info("Successfully applied session fix to Pyrogram")
        return True
    except Exception as e:
        logging.error(f"Failed to apply session fix to Pyrogram: {e}")
        return False
