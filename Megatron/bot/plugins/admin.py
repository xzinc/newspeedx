import os
import time
import string
import random
import asyncio
import aiofiles  # Used for broadcast logging
import datetime
import traceback
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
from Megatron.bot import StreamBot
from Megatron.vars import Var
from Megatron.utils.broadcast_helper import send_msg
from Megatron.utils.database import Database
from pyrogram import enums




db = Database(Var.DATABASE_URL, Var.SESSION_NAME)

broadcast_ids = {}


@StreamBot.on_message(filters.command("status") & filters.private & filters.user(Var.OWNER_ID))
async def sts(_: Client, m: Message):
    total_users = await db.total_users_count()
    await m.reply_text(text=f"**Total Users in Database:** `{total_users}`\n**Force Subscribe:** `{'Enabled' if Var.FORCE_SUB_ENABLED else 'Disabled'}`", parse_mode=enums.ParseMode.MARKDOWN, quote=True)


@StreamBot.on_message(filters.command("togglefsub") & filters.private & filters.user(Var.OWNER_ID))
async def toggle_fsub(bot: Client, m: Message):
    """Toggle force subscribe on/off"""
    import os

    # Get current status
    current_status = os.environ.get("FORCE_SUB_ENABLED", "True").lower() == "true"

    # Toggle status
    new_status = not current_status

    # Update environment variable
    os.environ["FORCE_SUB_ENABLED"] = str(new_status)

    # Update Var
    Var.FORCE_SUB_ENABLED = new_status

    # Send confirmation
    await m.reply_text(
        text=f"**Force Subscribe has been {'enabled' if new_status else 'disabled'}**\n\nUsers {'will' if new_status else 'will not'} be required to join the updates channel to use the bot.",
        parse_mode=enums.ParseMode.MARKDOWN,
        quote=True
    )

    # Log the change
    await bot.send_message(
        chat_id=Var.BIN_CHANNEL,
        text=f"#FORCE_SUBSCRIBE\n**Status:** `{'Enabled' if new_status else 'Disabled'}`\n**Changed by:** {m.from_user.mention}",
        parse_mode=enums.ParseMode.MARKDOWN
    )


@StreamBot.on_message(filters.command("unban") & filters.private & filters.user(Var.OWNER_ID))
async def unban_user(bot: Client, m: Message):
    """Unban a user from the updates channel"""
    # Check if a user ID was provided
    if len(m.command) != 2:
        await m.reply_text(
            text="**Usage:** `/unban user_id`\n\nPlease provide a user ID to unban.",
            parse_mode=enums.ParseMode.MARKDOWN,
            quote=True
        )
        return

    # Get the user ID
    try:
        user_id = int(m.command[1])
    except ValueError:
        await m.reply_text(
            text="**Error:** User ID must be a number.",
            parse_mode=enums.ParseMode.MARKDOWN,
            quote=True
        )
        return

    # Check if updates channel is set
    if not Var.UPDATES_CHANNEL:
        await m.reply_text(
            text="**Error:** No updates channel is set.",
            parse_mode=enums.ParseMode.MARKDOWN,
            quote=True
        )
        return

    # Unban the user
    try:
        # Remove the only_if_banned parameter which is not supported in your Pyrogram version
        await bot.unban_chat_member(
            chat_id=int(Var.UPDATES_CHANNEL),
            user_id=user_id
        )

        # Send confirmation
        await m.reply_text(
            text=f"**User with ID `{user_id}` has been unbanned from the updates channel.**",
            parse_mode=enums.ParseMode.MARKDOWN,
            quote=True
        )

        # Log the unban
        await bot.send_message(
            chat_id=Var.BIN_CHANNEL,
            text=f"#UNBAN\n**User ID:** `{user_id}`\n**Unbanned by:** {m.from_user.mention}",
            parse_mode=enums.ParseMode.MARKDOWN
        )
    except Exception as e:
        await m.reply_text(
            text=f"**Error unbanning user:** `{str(e)}`",
            parse_mode=enums.ParseMode.MARKDOWN,
            quote=True
        )


@StreamBot.on_message(filters.private & filters.command("broadcast") & filters.user(Var.OWNER_ID) & filters.reply)
async def open_broadcast_handler(bot, message):
    await broadcast_handler(c=bot, m=message)


async def send_msg(user_id, message):
    try:
        if Var.BROADCAST_AS_COPY is False:
            await message.forward(chat_id=user_id)
        elif Var.BROADCAST_AS_COPY is True:
            await message.copy(chat_id=user_id)
        return 200, None
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return send_msg(user_id, message)
    except InputUserDeactivated:
        return 400, f"{user_id} : deactivated\n"
    except UserIsBlocked:
        return 400, f"{user_id} : blocked the bot\n"
    except PeerIdInvalid:
        return 400, f"{user_id} : user id invalid\n"
    except Exception as e:
        return 500, f"{user_id} : {traceback.format_exc()}\n"


async def broadcast_handler(_, m):
    all_users = await db.get_all_users()
    broadcast_msg = m.reply_to_message
    while True:
        broadcast_id = ''.join([random.choice(string.ascii_letters) for _ in range(3)])
        if not broadcast_ids.get(broadcast_id):
            break
    out = await m.reply_text(
        text=f"Broadcast Started! You will be notified with log file when all the users are notified."
    )
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    failed = 0
    success = 0
    broadcast_ids[broadcast_id] = dict(
        total=total_users,
        current=done,
        failed=failed,
        success=success
    )
    async with aiofiles.open('broadcast.txt', 'w') as broadcast_log_file:
        async for user in all_users:
            sts, msg = await send_msg(
                user_id=int(user['id']),
                message=broadcast_msg
            )
            if msg is not None:
                await broadcast_log_file.write(msg)
            if sts == 200:
                success += 1
            else:
                failed += 1
            if sts == 400:
                await db.delete_user(user['id'])
            done += 1
            if broadcast_ids.get(broadcast_id) is None:
                break
            else:
                broadcast_ids[broadcast_id].update(
                    dict(
                        current=done,
                        failed=failed,
                        success=success
                    )
                )
    if broadcast_ids.get(broadcast_id):
        broadcast_ids.pop(broadcast_id)
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await asyncio.sleep(3)
    await out.delete()
    if failed == 0:
        await m.reply_text(
            text=f"broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.",
            quote=True
        )
    else:
        await m.reply_document(
            document='broadcast.txt',
            caption=f"broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.",
            quote=True
        )
    os.remove('broadcast.txt')
