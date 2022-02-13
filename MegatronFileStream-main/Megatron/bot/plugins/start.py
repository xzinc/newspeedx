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
            text=f"""Hey Dear {m.from_user.mention(style="md")} 🙋🏻‍♂️\nI'm Telegram File to Link Generator Bot.\n\nSend me any file & get the fast direct download link!\n\n⚠ **Don't forget to read the [rules](https://t.me/FutureTechnologyOfficial/1257) first!**\n\nسلام {m.from_user.mention(style="md")} عزیز 🙋🏻‍♂️\nمن بات تبدیل فایل به لینک هستم\nفایل تلگرامی خود را ارسال کنید تا لینک دانلود پر سرعت آن را دریافت نمایید\n\n**⚠  لطفا قبل از استفاده از بات [قوانین](https://t.me/FutureTechnologyOfficial/1257)را مطالعه نمایید!**\n\nهمچنین با زدن دستور /nim می‌توانید لینک های دریافتی خود را نیم بها نمایید.""",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton('✵ Updates Channel ✵', url='https://t.me/FutureTechnologyOfficial'), InlineKeyboardButton('✵ Support Group ✵', url='https://t.me/joinchat/riq-psSksFtiMDU8')],
                    [InlineKeyboardButton('✵ Developer ✵', url='https://t.me/CipherXBot')]
                ]
            ),
            disable_web_page_preview=True
        )
    else:
        if Var.UPDATES_CHANNEL:
            fsub = await force_subscribe(b, m)
            if fsub == 400:
                return

@StreamBot.on_message(filters.command('help') & filters.private & ~filters.edited)
async def help_handler(bot, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)
        await bot.send_message(
            Var.BIN_CHANNEL,
            f"#NEW_USER: \n\nNew User [{message.from_user.first_name}](tg://user?id={message.from_user.id}) Started !!"
        )
    if Var.UPDATES_CHANNEL:
        fsub = await force_subscribe(b, m)
        if fsub == 400:
            return
    await message.reply_text(
        text="✨ Send me any file, I'll give you its direct download link\n\nAlso I'm supported in channels. Add me to channel as admin to make me workable\n\n✨ فایل تلگرامی خود را برای من بفرستید تا لینک دانلود مستقیم آن را برای شما بفرستم\n\nهمچنین با ارتقای من به عنوان ادمین در چنل خود می توانید از امکانات من استفاده کنید، بدین صورت که در زمان پست فایل جدید در چنل دکمه شیشه ای دریافت لینک مستقیم فایل پست شده در زیر پست ایجاد می گردد.",
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("✵ Support Group ✵", url="https://t.me/joinchat/riq-psSksFtiMDU8"), InlineKeyboardButton("✵ Update Channel ✵", url="https://t.me/FutureTechnologyOfficial")],
                [InlineKeyboardButton("✵ Developer ✵", url="https://t.me/CipherXBot")]
            ]
        )
    )
