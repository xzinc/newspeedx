import asyncio
import logging
import sys
import os

# Set a very large time offset directly in the environment
os.environ['PYROGRAM_TIME_OFFSET'] = '300'

# Apply the session fix before importing Pyrogram
from Megatron.utils.session_fix import apply_session_fix
apply_session_fix()

# Now import Pyrogram and other modules
from .vars import Var
from aiohttp import web
from pyrogram import idle
from pyrogram.session import Session

# Set a very large time offset directly
# This is critical to fix the "msg_id is too low" error
Session.time_offset = 300
logging.info(f"Set Session.time_offset to 300 seconds directly in __main__.py")

from Megatron import utils
from Megatron import bot_info
from Megatron.server import web_server
from Megatron.bot.clients import initialize_clients
# StreamBot is imported in initialize_clients
# from Megatron.bot import StreamBot
from Megatron.utils.database import Database

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

# Reduce logging noise from libraries
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)
logging.getLogger("motor").setLevel(logging.WARNING)

loop = asyncio.get_event_loop()


async def start_services():
    print("----------------------------- DONE -----------------------------")
    print()

    # Initialize database
    print("-------------------- Initializing Database --------------------")
    try:
        # Initialize database once
        db = Database.get_instance(Var.DATABASE_URL, Var.SESSION_NAME)
        if db is not None:
            # Check if col attribute exists and is not None
            if hasattr(db, 'col') and db.col is not None:
                await db.create_index()
                logging.info("Database initialized successfully with indexes")
            else:
                logging.warning("Database initialized but collection is not available")
        else:
            logging.warning("Failed to initialize database")
    except Exception as e:
        logging.error(f"Error initializing database: {e}")
        logging.warning("Continuing with limited database functionality")
    print("----------------------------- DONE -----------------------------")
    print()

    print(
        "----------------------------- Initializing Clients -----------------------------"
    )
    await initialize_clients()
    print("----------------------------- DONE -----------------------------")
    if Var.ON_HEROKU:
        print("------------------ Starting Keep Alive Service ------------------")
        print()
        asyncio.create_task(utils.ping_server())
    print("-------------------- Initalizing Web Server --------------------")
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0" if Var.ON_HEROKU else Var.BIND_ADDRESS
    await web.TCPSite(app, bind_address, Var.PORT).start()
    print("----------------------------- DONE -----------------------------")
    print()
    print("----------------------- Service Started -----------------------")
    print("                        bot =>> {}".format(bot_info.first_name))
    if bot_info.dc_id:
        print("                        DC ID =>> {}".format(str(bot_info.dc_id)))
    print("                        server ip =>> {}".format(bind_address, Var.PORT))
    if Var.ON_HEROKU:
        print("                        app running on =>> {}".format(Var.FQDN))
    print("---------------------------------------------------------------")
    await idle()


if __name__ == "__main__":
    try:
        loop.run_until_complete(start_services())
    except KeyboardInterrupt:
        logging.info("----------------------- Service Stopped -----------------------")
