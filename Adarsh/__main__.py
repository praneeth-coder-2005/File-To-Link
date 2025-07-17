# (c) adarsh-goel

# ---- Time Sync Fix (💡 Must run before Pyrogram) ----
import time
import os

try:
    import ntplib
    c = ntplib.NTPClient()
    r = c.request('pool.ntp.org', version=3)
    offset = r.tx_time - time.time()
    _original_time = time.time
    time.time = lambda: _original_time() + offset
    os.environ['TZ'] = 'UTC'
    print(f"[✅] Time synced with offset: {offset:.2f} seconds")
except Exception as e:
    print(f"[⚠️] NTP time sync failed: {e}")
# ----------------------------------------------------

# Standard imports
import sys
import glob
import asyncio
import logging
import importlib
from pathlib import Path
from pyrogram import idle

# Bot code imports (safe after time patch)
from .bot import StreamBot
from .vars import Var
from aiohttp import web
from .server import web_server
from .utils.keepalive import ping_server
from Adarsh.bot.clients import initialize_clients

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

# Discover plugins
ppath = "Adarsh/bot/plugins/*.py"
files = glob.glob(ppath)

# ✅ Start bot (after time patch)
StreamBot.start()
loop = asyncio.get_event_loop()


async def start_services():
    print('\n------------------- Initalizing Telegram Bot -------------------')
    bot_info = await StreamBot.get_me()
    StreamBot.username = bot_info.username
    print("------------------------------ DONE ------------------------------\n")

    print("---------------------- Initializing Clients ----------------------")
    await initialize_clients()
    print("------------------------------ DONE ------------------------------\n")

    print('--------------------------- Importing ---------------------------')
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"Adarsh/bot/plugins/{plugin_name}.py")
            import_path = ".plugins.{}".format(plugin_name)
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules["Adarsh.bot.plugins." + plugin_name] = load
            print("Imported => " + plugin_name)

    if Var.ON_HEROKU:
        print("------------------ Starting Keep Alive Service ------------------\n")
        asyncio.create_task(ping_server())

    print('-------------------- Initalizing Web Server -------------------------')
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = ".railway.app" if Var.ON_HEROKU else Var.BIND_ADRESS
    await web.TCPSite(app, bind_address, Var.PORT).start()
    print('----------------------------- DONE ---------------------------------------------------------------------\n')

    print('---------------------------------------------------------------------------------------------------------')
    print('---------------------------------------------------------------------------------------------------------')
    print(' follow me for more such exciting bots! https://github.com/aadhi000')
    print('---------------------------------------------------------------------------------------------------------\n')

    print('----------------------- Service Started -----------------------------------------------------------------')
    print(f'                        bot =>> {(await StreamBot.get_me()).first_name}')
    print(f'                        server ip =>> {bind_address}:{Var.PORT}')
    print(f'                        Owner =>> {Var.OWNER_USERNAME}')
    if Var.ON_HEROKU:
        print(f'                        app running on =>> {Var.FQDN}')
    print('---------------------------------------------------------------------------------------------------------')
    print('Give a star to my repo https://github.com/adarsh-goel/filestreambot-pro  also follow me for new bots')
    print('---------------------------------------------------------------------------------------------------------')

    await idle()


if __name__ == '__main__':
    try:
        loop.run_until_complete(start_services())
    except KeyboardInterrupt:
        logging.info('----------------------- Service Stopped -----------------------')
