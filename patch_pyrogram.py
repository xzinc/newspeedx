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
        # Set a very large time offset in the environment
        os.environ['PYROGRAM_TIME_OFFSET'] = '120'

        # Try to patch the Session class directly
        from pyrogram.session import Session

        # Set a very large time offset (120 seconds in the future)
        # This ensures that msg_id will always be high enough
        Session.time_offset = 120
        logging.info("Set Pyrogram Session.time_offset to 120 seconds")

        # Try to find and patch the session.py file as a backup
        try:
            import pyrogram
            pyrogram_path = os.path.dirname(pyrogram.__file__)
            session_path = os.path.join(pyrogram_path, "session", "session.py")

            if os.path.exists(session_path):
                logging.info(f"Found Pyrogram session.py at {session_path}")

                # Read the session.py file
                with open(session_path, "r") as f:
                    content = f.read()

                # Check if the file has already been patched
                if "# PATCHED FOR MSG_ID TOO LOW" in content:
                    logging.info("Pyrogram session.py is already patched")
                else:
                    # Find the line with "time_offset = 0"
                    if "time_offset = 0" in content:
                        # Replace it with a large positive offset
                        patched_content = content.replace(
                            "time_offset = 0",
                            "time_offset = 120  # PATCHED FOR MSG_ID TOO LOW"
                        )

                        # Write the patched file
                        with open(session_path, "w") as f:
                            f.write(patched_content)

                        logging.info("Successfully patched Pyrogram session.py")
                    else:
                        logging.warning("Could not find 'time_offset = 0' in session.py")
        except Exception as e:
            logging.warning(f"Error patching session.py file: {e}")
            logging.info("Continuing with direct Session.time_offset patch")

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
