#!/usr/bin/env python3
"""
Patch for Pyrogram to fix the 'msg_id is too low' error.
This script directly modifies the Pyrogram session.py file.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def patch_pyrogram():
    """
    Patch Pyrogram's session.py to fix the 'msg_id is too low' error.
    """
    try:
        # Find the Pyrogram session.py file
        import pyrogram
        pyrogram_path = os.path.dirname(pyrogram.__file__)
        session_path = os.path.join(pyrogram_path, "session", "session.py")
        
        if not os.path.exists(session_path):
            logging.error(f"Could not find Pyrogram session.py at {session_path}")
            return False
        
        logging.info(f"Found Pyrogram session.py at {session_path}")
        
        # Read the session.py file
        with open(session_path, "r") as f:
            content = f.read()
        
        # Check if the file has already been patched
        if "# PATCHED FOR MSG_ID TOO LOW" in content:
            logging.info("Pyrogram session.py is already patched")
            return True
        
        # Find the line with "time_offset = 0"
        if "time_offset = 0" in content:
            # Replace it with a large positive offset
            patched_content = content.replace(
                "time_offset = 0",
                "time_offset = 60  # PATCHED FOR MSG_ID TOO LOW"
            )
            
            # Write the patched file
            with open(session_path, "w") as f:
                f.write(patched_content)
            
            logging.info("Successfully patched Pyrogram session.py")
            return True
        else:
            logging.warning("Could not find 'time_offset = 0' in session.py")
            
            # Try to patch the Session class directly
            from pyrogram.session import Session
            Session.time_offset = 60
            logging.info("Patched Session.time_offset directly")
            
            return True
    
    except Exception as e:
        logging.error(f"Error patching Pyrogram: {e}")
        return False

if __name__ == "__main__":
    # Run the patch
    success = patch_pyrogram()
    if success:
        logging.info("Pyrogram patch applied successfully")
        
        # Now run the bot
        import runpy
        runpy.run_module("Megatron", run_name="__main__")
    else:
        logging.error("Failed to apply Pyrogram patch")
        sys.exit(1)
