from pyrogram import Client

from Megatron.utils import TokenParser
from . import multi_clients, work_loads, StreamBot
from ..vars import Var

async def initialize_clients():
    multi_clients[0] = StreamBot
    work_loads[0] = 0
    all_tokens = TokenParser().parse_from_env()
    if not all_tokens:
        print("No additional clients found, using default client")
        return
    for client_id, token in all_tokens.items():
        instance = Client(
            session_name=":memory:",
            api_id=Var.API_ID,
            api_hash=Var.API_HASH,
            bot_token=token,
            sleep_threshold=Var.SLEEP_THRESHOLD,
            no_updates=True,
        )
        try:
            multi_clients[client_id] = await instance.start()
        except Exception as e:
            print(f"Failed starting Client - {client_id}; Error: {e}")
            continue
        work_loads[client_id] = 0
        print(f"Started - Client {client_id}")
    if len(multi_clients) != 1:
        Var.MULTI_CLIENT = True
        print("Multi-Client Mode Enabled")
    else:
        print("No additional clients were initialized, using default client")
