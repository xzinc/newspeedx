from os import getcwd
from pyromod import listen

from pyrogram import Client
from pyrogram.session import Session

# Fix for "msg_id is too low" error
# Set a large time offset (30 seconds in the future)
Session.time_offset = 30

from ..vars import Var

StreamBot = Client(
  session_name=Var.SESSION_NAME,
    api_id=Var.API_ID,
    api_hash=Var.API_HASH,
    workdir="Megatron",
    plugins={"root": "Megatron/bot/plugins"},
    bot_token=Var.BOT_TOKEN,
    sleep_threshold=Var.SLEEP_THRESHOLD,
    workers=Var.WORKERS,
)

multi_clients = {}
work_loads = {}
