#!/usr/bin/env python3
"""
Run script for the Megatron bot.
This script applies the Pyrogram patch and then starts the bot.
"""

import os
import sys
import logging
import importlib
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def main():
    """
    Main function to run the bot.
    """
    # First, try to apply the Pyrogram patch
    try:
        from pyrogram_patch import patch_pyrogram
        patch_result = patch_pyrogram()
        logging.info(f"Pyrogram patch result: {patch_result}")
    except Exception as e:
        logging.warning(f"Could not run Pyrogram patch: {e}")
        # Set a large time offset directly in the environment
        os.environ['PYROGRAM_TIME_OFFSET'] = '60'
    
    # Set environment variables for Pyrogram
    os.environ['PYROGRAM_NO_UPDATES'] = '1'
    
    # Now run the bot
    try:
        # Try to import and run the module directly
        from Megatron import __main__ as megatron_main
        logging.info("Imported Megatron.__main__ successfully")
    except Exception as e:
        logging.error(f"Error importing Megatron.__main__: {e}")
        logging.info("Falling back to subprocess")
        
        # If that fails, run it as a subprocess
        try:
            subprocess.run([sys.executable, "-m", "Megatron"], check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Error running Megatron as subprocess: {e}")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
