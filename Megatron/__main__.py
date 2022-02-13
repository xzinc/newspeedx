import asyncio
import logging
from .vars import Var
from aiohttp import web
from pyrogram import idle
from Megatron import utils
from Megatron import bot_info
from Megatron.server import web_server
from Megatron.bot.clients import initialize_clients


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

loop = asyncio.get_event_loop()


async def start_services():
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
