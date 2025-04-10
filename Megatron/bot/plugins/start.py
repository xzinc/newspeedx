from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import UserNotParticipant

from Megatron.bot import StreamBot
from Megatron.vars import Var
from Megatron.utils.human_readable import humanbytes
from Megatron.utils.database import Database
from Megatron.handlers.fsub import force_subscribe

db = Database(Var.DATABASE_URL, Var.SESSION_NAME)


@StreamBot.on_message(filters.command('start') & filters.private & ~filters.edited)
async def start(b, m : Message):
    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id)
        await b.send_message(
            Var.BIN_CHANNEL,
            f"#NEW_USER: \n\nNew User [{m.from_user.first_name}](tg://user?id={m.from_user.id}) Started the bot."
        )
    firstname = m.from_user.first_name
    usr_cmd = m.text.split("_")[-1]
    if usr_cmd == "/start":
        if Var.UPDATES_CHANNEL:
            fsub = await force_subscribe(b, m)
            if fsub == 400:
                return
        await m.reply(
            text=f"""Hey Dear {m.from_user.mention(style="md")} 🙋🏻‍♂️\nI'm Telegram File to Link Generator Bot.\n\nSend me any file & get the fast direct download link!\n\n⚠ **Don't forget to Join Channel first!**\n\n""",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton('✵ Updates Channel ✵', url='https://t.me/+uW4Saio7cmYwNjk1'), InlineKeyboardButton('😊 Donate 😊', url='https://t.me/TG_FatherBoT?start=donate')],
                    [InlineKeyboardButton('🧧 Contact ADmin 🧧', url='https://t.me/TG_FatherBoT')]
                ]
            ),
            disable_web_page_preview=True
        )
    else:
        if Var.UPDATES_CHANNEL:
            fsub = await force_subscribe(b, m)
            if fsub == 400:
                return
        u = await b.get_chat_member(int(Var.UPDATES_CHANNEL), m.from_user.id)
        if u.status == "kicked" or u.status == "banned":
            await b.send_message(
                chat_id=m.from_user.id,
                text="✨ You're Banned due not to pay attention to the [rules](https://t.me/+uW4Saio7cmYwNjk1). Contact [Support ](https://t.me/TG_FatherBoT) if you think you've banned wrongly.\n\n✨",
                parse_mode="markdown",
                disable_web_page_preview=True
            )

@StreamBot.on_message(filters.command('help') & filters.private & ~filters.edited)
async def help_handler(bot, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)
        await bot.send_message(
            Var.BIN_CHANNEL,
            f"#NEW_USER #joins #join_log: \n\nNew User [{message.from_user.first_name}](tg://user?id={message.from_user.id}) Started !!"
        )
    if Var.UPDATES_CHANNEL:
        fsub = await force_subscribe(bot, message)
        if fsub == 400:
            return
    await message.reply_text(
        text="✨ Send me any file, I'll give you its direct download link\n\nAlso I'm supported in channels. Add me to channel as admin to make me workable\n\n✨",
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("✵ MAin Channel ✵", url="https://t.me/+uW4Saio7cmYwNjk1"), InlineKeyboardButton("✵ NetWork ✵", url="https://t.me/highpeed_movies")],
                [InlineKeyboardButton("✵ Developer ✵", url="https://t.me/TG_FatherBoT")]
            ]
        )
    )
