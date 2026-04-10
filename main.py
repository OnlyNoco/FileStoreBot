
import asyncio

from pyrogram import compose

from bot import Bot, web_app
from config import *


async def runner():
    bot = Bot(
        SESSION,
        WORKERS,
        DB_CHANNEL,
        FSUBS,
        TOKEN,
        ADMINS,
        MESSAGES,
        AUTO_DEL,
        DB_URI,
        DB_NAME,
        API_ID,
        API_HASH,
        PROTECT,
        DISABLE_BTN
    )

    await asyncio.gather(
        compose([bot]),
        web_app(bot)
    )


asyncio.run(runner())
