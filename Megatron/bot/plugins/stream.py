import asyncio
import logging
from urllib.parse import quote_plus

from pyrogram import filters, Client
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from Megatron.bot import StreamBot
from Megatron.utils import get_hash, get_name
from Megatron.utils.database import Database
from Megatron.handlers.fsub import force_subscribe
from Megatron.vars import Var
from Megatron.utils.human_readable import humanbytes

db = Database(Var.DATABASE_URL, Var.SESSION_NAME)


def detect_type(m: Message):
    if m.document:
        return m.document
    elif m.video:
        return m.video
    elif m.photo:
        return m.photo
    elif m.audio:
        return m.audio
    else:
        return

@StreamBot.on_message(
    filters.private
    & (
        filters.document
        | filters.video
        | filters.audio
        | filters.animation
        | filters.voice
        | filters.video_note
        | filters.photo
        | filters.sticker
    ),
    group=4,
)
async def media_receive_handler(c: Client, m: Message):
    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id)
        await c.send_message(
            Var.BIN_CHANNEL,
            f"#NEW_USER: \n\nNew User [{m.from_user.first_name}](tg://user?id={m.from_user.id}) Started the bot."
        )
    if Var.UPDATES_CHANNEL:
        fsub = await force_subscribe(c, m)
        if fsub == 400:
            return
    try:
        file_size = None
        if m.video:
            file_size = f"{humanbytes(m.video.file_size)}"
        elif m.document:
            file_size = f"{humanbytes(m.document.file_size)}"
        elif m.audio:
            file_size = f"{humanbytes(m.audio.file_size)}"
        elif m.photo:
            file_size = f"{humanbytes(m.photo.file_size)}"
        file_name = None
        if m.video:
            file_name = f"{m.video.file_name}"
        elif m.document:
            file_name = f"{m.document.file_name}"
        elif m.audio:
            file_name = f"{m.audio.file_name}"
        elif m.photo:
            file_name = f"{m.photo.file_id}"
        file = detect_type(m)
        file_name = ''
        if file and hasattr(file, 'file_name'):
            file_name = file.file_name

        # Forward the message to the bin channel
        log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)

        # Check if log_msg is valid and has message_id
        if log_msg and hasattr(log_msg, 'message_id'):
            # Generate the stream and short links
            stream_link = f"{Var.URL}{log_msg.message_id}/{quote_plus(get_name(m))}?hash={get_hash(log_msg)}"
            short_link = f"{Var.URL}{get_hash(log_msg)}{log_msg.message_id}"

            logging.info(f"Generated link: {stream_link} for {m.from_user.first_name}")

            # Prepare the message text
            msg_text = f"Your Link Generated!😄\n\n📂 **File Name:** `{file_name}`\n\n**✨ File Size:** `{file_size}`\n\n📥 **Download/Stream Link:** `{stream_link}`\n\n📥 **Short Link:** `{short_link}`"

            # Send notification to the bin channel
            await c.send_message(
                chat_id=Var.BIN_CHANNEL,
                text=f"Requested by [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n**User ID:** `{m.from_user.id}`\n**Download Link:** {stream_link}\n**Short Link:** {short_link}",
                disable_web_page_preview=True,
                reply_to_message_id=log_msg.message_id,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("࿋ Ban User ࿋", callback_data=f"ban_{m.from_user.id}")]])
            )

            # Reply to the user with the links
            await m.reply_text(
                text=msg_text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("࿋ Direct/Stream Link ࿋", url=stream_link)],
                        [InlineKeyboardButton("࿋ Short Link ࿋", url=short_link)],
                    ],
                ),
                quote=True,
                parse_mode="Markdown"
            )
        else:
            # Handle case where log_msg is invalid
            logging.error("Forward failed: log_msg is invalid or has no message_id attribute")
            await m.reply_text(
                "Sorry, something went wrong while generating your link. Please try again later.",
                quote=True
            )
            await c.send_message(
                chat_id=Var.BIN_CHANNEL,
                text=f"#ERROR_FORWARD: Failed to forward message from {m.from_user.first_name} (ID: {m.from_user.id}). The forwarded message was invalid.",
                disable_web_page_preview=True,
                parse_mode="Markdown"
            )
    except FloodWait as e:
        print(f"Sleeping for {str(e.x)}s")
        await asyncio.sleep(e.x)
        await c.send_message(chat_id=Var.BIN_CHANNEL, text=f"Got FloodWait of {str(e.x)}s from [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n\n**User ID:** `{str(m.from_user.id)}`", disable_web_page_preview=True, parse_mode="Markdown")


@StreamBot.on_message(filters.channel & (filters.document | filters.video | filters.photo) & ~filters.edited & ~filters.forwarded, group=-1)
async def channel_receive_handler(bot, broadcast):
    if int(broadcast.chat.id) in Var.BANNED_CHANNELS:
        await bot.leave_chat(broadcast.chat.id)
        return
    try:
        # Forward the message to the bin channel
        log_msg = await broadcast.forward(chat_id=Var.BIN_CHANNEL)

        # Check if log_msg is valid and has message_id
        if log_msg and hasattr(log_msg, 'message_id'):
            # Generate the stream link
            stream_link = f"{Var.URL}{log_msg.message_id}/{quote_plus(get_name(broadcast))}?hash={get_hash(log_msg)}"

            # Reply to the forwarded message with info
            await log_msg.reply_text(
                text=f"**Channel Name:** `{broadcast.chat.title}`\n**Channel ID:** `{broadcast.chat.id}`\n**Link:** {stream_link}",
                quote=True,
                parse_mode="Markdown"
            )

            # Edit the original message with the download link
            await bot.edit_message_reply_markup(
                chat_id=broadcast.chat.id,
                message_id=broadcast.message_id,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("📥 Direct Download Link ࿋", url=f"{stream_link}")]
                    ]
                )
            )
        else:
            # Handle case where log_msg is invalid
            logging.error("Forward failed: log_msg is invalid or has no message_id attribute")
            await bot.send_message(
                chat_id=Var.BIN_CHANNEL,
                text=f"#ERROR_FORWARD: Failed to forward message from {broadcast.chat.title} (ID: {broadcast.chat.id}). The forwarded message was invalid.",
                disable_web_page_preview=True,
                parse_mode="Markdown"
            )
    except FloodWait as w:
        logging.warning(f"Sleeping for {str(w.x)}s due to FloodWait")
        await asyncio.sleep(w.x)
        await bot.send_message(
            chat_id=Var.BIN_CHANNEL,
            text=f"Got FloodWait of {str(w.x)}s from {broadcast.chat.title}\n\n**Channel ID:** `{str(broadcast.chat.id)}`",
            disable_web_page_preview=True,
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.error(f"Error in channel_receive_handler: {e}")
        await bot.send_message(
            chat_id=Var.BIN_CHANNEL,
            text=f"#ERROR_TRACEBACK: `{e}`",
            disable_web_page_preview=True,
            parse_mode="Markdown"
        )
