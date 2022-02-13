import asyncio

from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from Megatron.vars import Var
from Megatron.utils.callbacks import *

async def force_subscribe(bot, cmd):
    try:
        invite_link = await bot.create_chat_invite_link(int(Var.UPDATES_CHANNEL))
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return 400
    try:
        user = await bot.get_chat_member(int(Var.UPDATES_CHANNEL), cmd.from_user.id)
        if user.status == "kicked":
            await bot.send_message(
                chat_id=cmd.from_user.id,
                text="✨ You are Banned due not to pay attention to the [rules](https://t.me/FutureTechnologyOfficial/1257). Contact [Support Group](https://t.me/joinchat/riq-psSksFtiMDU8) if you think you've banned wrongly.\n\n✨ شما به علت عدم رعایت [قوانین](https://t.me/FutureTechnologyOfficial/1257) بن شده اید. اگر فکر میکنید بن شدن شما اشتباه بوده و قوانین را رعایت کرده اید می توانید با [گروه پشتیبانی](https://t.me/joinchat/riq-psSksFtiMDU8) در ارتباط باشید.",
                parse_mode="markdown",
                disable_web_page_preview=True
            )
            return 400
    except UserNotParticipant:
        await bot.send_message(
            chat_id=cmd.from_user.id,
            text="**✨ Please join updates channel to use me. Only channel subscribers can use the bot.**\n\nAfter joining tap refresh button.\n\n**✨لطفا در چنل عضو شوید. تنها اعضای چنل می توانند از بات استفاده کنند.**\n\nپس از عضویت بر روی دکمه refresh کلیک کنید.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("✵ Join Updates Channel ✵", url=invite_link.invite_link)
                    ],
                    [
                        InlineKeyboardButton("🔄 Refresh 🔄", callback_data="refreshmeh")
                    ]
                ]
            ),
            parse_mode="markdown"
        )
        return 400
    except Exception:
        await bot.send_message(
            chat_id=cmd.from_user.id,
            text="Something went Wrong. Contact [Support Group](https://t.me/joinchat/riq-psSksFtiMDU8).",
            parse_mode="markdown",
            disable_web_page_preview=True
        )
        return 400
