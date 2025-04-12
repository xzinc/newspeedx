from requests import post

# Import directly from pyrogram
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant

from Megatron.vars import Var
from Megatron.bot import StreamBot

@StreamBot.on_message(filters.command("nim") & filters.private)
async def nimdownloader(c: Client, m: Message):
    if Var.UPDATES_CHANNEL is not None:
        try:
            user = await c.get_chat_member(Var.UPDATES_CHANNEL, m.chat.id)
            if user.status == "kicked":
                await c.send_message(
                    chat_id=m.chat.id,
                    text="Sorry, You are Banned to use me. Contact me [Admin](https://t.me/filmyxbot).",
                    parse_mode="md",
                    disable_web_page_preview=True
                )
                return
        except UserNotParticipant:
            await c.send_message(
                chat_id=m.chat.id,
                text="**Please join updates channel to use me**\nOnly channel subscribers can use the bot\nAfter joining tap help button\n\n✨.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("✵ Join Updates Channel ✵", url=f"https://t.me/{Var.UPDATES_CHANNEL}")
                        ]
                    ]
                ),
                parse_mode="md"
            )
            return
        except Exception:
            await c.send_message(
                chat_id=m.chat.id,
                text="Something went Wrong. Contact my [Support Group](https://t.me/joinchat/riq-psSksFtiMDU8).",
                parse_mode="md",
                disable_web_page_preview=True)
            return
    chat = m.chat
    # Send a message asking for the URL
    await StreamBot.send_message(chat.id, "⚠️This part is only for Iranian users⚠️\n\n**Please enter the URL:**")

    # Define a message handler to wait for the response
    @StreamBot.on_message(filters.chat(chat.id) & filters.text & ~filters.command, group=1000)
    async def url_handler(_, message):
        # Remove the handler after getting the response
        StreamBot.remove_handler(url_handler, group=1000)

        # Process the URL
        txt = message.text.strip()
        if not txt or txt.startswith("/") or "http" not in txt.lower():
            await StreamBot.send_message(chat.id, "Invalid URL. Please try again with /nim command.")
            return

        try:
            url = "https://www.digitalbam.ir/DirectLinkDownloader/Download"
            data = {"downloadUri": txt}
            request = post(url, data).json()["fileUrl"]

            log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)
            await log_msg.reply_text(text=f"Requested by [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n**User ID:** `{m.from_user.id}`\n**Requested Link:** {txt}\n**Download Link:**\n✨ {request}", disable_web_page_preview=True, parse_mode="md", quote=True)

            msg = "**لینک نیم بهای شما ایجاد شد 😄**\n\n⚜️ **لینک درخواستی شما** : [لینک]({})\n\n⚜️ **لینک نیم بهای شما :**\n✨ سرور نیم بها : [لینک]({})\n\n✨ @FiletoLinkTelegramBot ✨"
            await m.reply_text(
                text=msg.format(txt, request),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✵ Download Now ✵", url=request)]]),
                quote=True
            )
        except Exception:
            await StreamBot.send_message(chat.id, "**اروری رخ داده است. لطفا بعد 1 دقیقه مجددا امتحان نمایید. در صورت رخداد مجدد مشکل را در چنل پشتیبانی بیان نمایید. با تشکر 🌺**")

    # We don't need to continue with the rest of the function
    return
