import time
from .vars import Var
from Megatron.bot.clients import StreamBot

print("\n")
print("------------------- Initializing Telegram Bot -------------------")

StreamBot.start()
bot_info = StreamBot.get_me()
__version__ = 2.2
StartTime = time.time()
