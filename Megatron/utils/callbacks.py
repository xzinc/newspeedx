from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant

from Megatron.bot import StreamBot
from Megatron.vars import Var

@StreamBot.on_callback_query()
async def button(bot, cmd: CallbackQuery):
  cb_data = cmd.data
  if "refreshmeh" in cb_data:
    if Var.UPDATES_CHANNEL:
      invite_link = await bot.create_chat_invite_link(int(Var.UPDATES_CHANNEL))
      try:
        user = await bot.get_chat_member(int(Var.UPDATES_CHANNEL), cmd.message.chat.id)
        if user.status == "kicked":
          await cmd.message.edit(
            text="**✨ You are Banned due not to pay attention to the rules. Contact [Support Group](https://t.me/joinchat/riq-psSksFtiMDU8) for further information if interested.\n\n✨ شما به علت عدم رعایت قوانین بن شده اید. جهت اطلاع بیشتر در صورت تمایل می توانید با [گروه پشتیبانی](https://t.me/joinchat/riq-psSksFtiMDU8) در ارتباط باشید.",
            parse_mode="md",
            disable_web_page_preview=True
          )
          return
      except UserNotParticipant:
        await cmd.message.edit(
          text="**✨ You still haven't joined the updates channel. Only channel subscribers can use the bot.**\n\nAfter joining tap refresh button❗️**\n",
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
          parse_mode="md"
        )
        return
      except Exception:
        await cmd.message.edit(
          text="Something went Wrong. Contact [Support Group](https://t.me/joinchat/riq-psSksFtiMDU8).",
          parse_mode="md",
          disable_web_page_preview=True
        )
        return
    await cmd.message.edit(
      text=f"""Hey Dear {cmd.from_user.mention(style="md")} 🙋🏻‍♂️\nI'm Telegram File to Link Generator Bot.\n\nSend me any file & get the fast direct download link!\n\n""",
      parse_mode="md",
      reply_markup=InlineKeyboardMarkup(
        [
          [InlineKeyboardButton('✵ Updates Channel ✵', url='https://t.me/+FcsqT7u8gt1mMTdh'), InlineKeyboardButton('✵ Rules✵', url='https://t.me/highspeed_movies/7')],
          [InlineKeyboardButton('✵ Donate! ✵', url='https://t.me/putsextrovert/7')]
        ]
      ),
      disable_web_page_preview=True
    )
  elif cb_data.startswith("ban_"):
    if Var.UPDATES_CHANNEL is None:
      await cmd.answer("You didn't Set any Updates Channel", show_alert=True)
      return
    try:
      user_id = cb_data.split("_", 1)[1]
      await bot.ban_chat_member(chat_id=Var.UPDATES_CHANNEL, user_id=int(user_id))
      await cmd.answer("User Banned from Updates Channel", show_alert=True)
    except Exception as e:
      await cmd.answer(f"Can't Ban Him!\n\nError: {e}", show_alert=True)
