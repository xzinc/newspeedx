from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import UserNotParticipant

from Megatron.bot import StreamBot
from Megatron.vars import Var
from Megatron.utils.database import Database
# This import is used in other parts of the code
# from Megatron.handlers.fsub import force_subscribe

db = Database(Var.DATABASE_URL, Var.SESSION_NAME)

@StreamBot.on_message(filters.command('settings') & filters.private)
async def settings_handler(bot, message: Message):
    """
    Handle the /settings command to show user settings
    """
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)
        await bot.send_message(
            Var.BIN_CHANNEL,
            f"#NEW_USER: \n\nNew User [{message.from_user.first_name}](tg://user?id={message.from_user.id}) Started the bot and used settings."
        )

    # Check for forced subscription
    if Var.UPDATES_CHANNEL:
        try:
            user = await bot.get_chat_member(int(Var.UPDATES_CHANNEL), message.from_user.id)
            if user.status == "kicked":
                await message.reply_text(
                    text="Sorry, you are banned. Contact support.",
                    parse_mode="md",
                    disable_web_page_preview=True
                )
                return
        except UserNotParticipant:
            await message.reply_text(
                text="**Please Join My Updates Channel to use this Bot!**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("Join Updates Channel", url=f"https://t.me/{Var.UPDATES_CHANNEL}")
                        ]
                    ]
                ),
                parse_mode="md"
            )
            return
        except Exception:
            await message.reply_text(
                text="Something went wrong. Contact support.",
                parse_mode="md",
                disable_web_page_preview=True
            )
            return

    # Show settings menu
    await message.reply_text(
        text="**Here are your settings:**\n\n"
             "• You can customize your experience with this bot\n"
             "• Get information about your account\n"
             "• Check your usage statistics",
        parse_mode="md",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Account Info", callback_data="account_info")],
                [InlineKeyboardButton("Usage Statistics", callback_data="usage_stats")],
                [InlineKeyboardButton("Help", url="https://t.me/TG_FatherBoT")]
            ]
        )
    )

# Add callback handlers for the settings menu
@StreamBot.on_callback_query(filters.regex('^account_info$'))
async def account_info_callback(_, callback_query):
    user_id = callback_query.from_user.id
    user_name = callback_query.from_user.first_name

    await callback_query.answer("Loading account information...")

    await callback_query.message.edit_text(
        text=f"**Account Information**\n\n"
             f"• User ID: `{user_id}`\n"
             f"• Name: {user_name}\n"
             f"• Bot Status: Active",
        parse_mode="md",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Back to Settings", callback_data="back_to_settings")]
            ]
        )
    )

@StreamBot.on_callback_query(filters.regex('^usage_stats$'))
async def usage_stats_callback(_, callback_query):
    # We would use user_id if we were fetching actual usage statistics
    # user_id = callback_query.from_user.id

    await callback_query.answer("Loading usage statistics...")

    # Here you would normally fetch actual usage statistics from the database
    # For now, we'll just show placeholder text

    await callback_query.message.edit_text(
        text="**Usage Statistics**\n\n"
             "• Files Processed: Not tracked yet\n"
             "• Bandwidth Used: Not tracked yet\n"
             "• Account Created: Not tracked yet",
        parse_mode="md",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Back to Settings", callback_data="back_to_settings")]
            ]
        )
    )

@StreamBot.on_callback_query(filters.regex('^back_to_settings$'))
async def back_to_settings_callback(_, callback_query):
    await callback_query.answer("Returning to settings...")

    await callback_query.message.edit_text(
        text="**Here are your settings:**\n\n"
             "• You can customize your experience with this bot\n"
             "• Get information about your account\n"
             "• Check your usage statistics",
        parse_mode="md",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Account Info", callback_data="account_info")],
                [InlineKeyboardButton("Usage Statistics", callback_data="usage_stats")],
                [InlineKeyboardButton("Help", url="https://t.me/TG_FatherBoT")]
            ]
        )
    )
