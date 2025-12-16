import os
import random
import string
import asyncio

from pyrogram import Client, filters, idle
from pyrogram.types import Message

# ========= ENV =========
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
SESSION_STRING = os.environ["SESSION_STRING"]
OWNER_ID = int(os.environ["OWNER_ID"])
BOT_USERNAME = os.environ["BOT_USERNAME"]  # without @

# ========= MEMORY =========
POSTS = {}   # code -> (chat_id, message_id)

def gen_code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

# ========= CLIENTS =========
bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

userbot = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

# ========= CAPTURE CHANNEL POSTS =========
@userbot.on_message(filters.channel & ~filters.service)
async def capture(client: Client, message: Message):
    code = gen_code()
    POSTS[code] = (message.chat.id, message.id)

    link = f"https://t.me/{BOT_USERNAME}?start={code}"

    await bot.send_message(
        OWNER_ID,
        f"✅ New Post Captured\n\n"
        f"🔑 Code: `{code}`\n"
        f"🔗 {link}",
        disable_web_page_preview=True
    )

    print(f"CAPTURED -> {code}")

# ========= USER START =========
@bot.on_message(filters.private & filters.command("start"))
async def start(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text(
            "👋 Bot active hai.\n"
            "Valid link par tap karke post milegi."
        )
        return

    code = message.command[1]

    if code not in POSTS:
        await message.reply_text("❌ Invalid / expired link.")
        return

    chat_id, msg_id = POSTS[code]

    sent = await userbot.copy_message(
        chat_id=message.chat.id,
        from_chat_id=chat_id,
        message_id=msg_id
    )

    # auto delete after 5 min
    await asyncio.sleep(300)
    await sent.delete()

# ========= RUN =========
if __name__ == "__main__":
    bot.start()
    userbot.start()
    print("🚀 NEW BOT RUNNING")
    idle()
    bot.stop()
    userbot.stop()
