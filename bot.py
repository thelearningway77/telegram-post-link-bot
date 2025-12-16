import os
import asyncio
import random
import string

from pyrogram import Client, filters, idle
from pyrogram.types import Message

# ================== ENV ==================
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
SESSION_STRING = os.environ["SESSION_STRING"]
OWNER_ID = int(os.environ["OWNER_ID"])
BOT_USERNAME = os.environ["BOT_USERNAME"]

# ================== MEMORY ==================
POST_MAP = {}   # code -> (chat_id, message_id)

# ================== HELPERS ==================
def generate_code(length=8):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))

# ================== CLIENTS ==================
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

# ================== DEBUG (VERY IMPORTANT) ==================
@userbot.on_message(filters.all)
async def debug_everything(client: Client, message: Message):
    print(
        "DEBUG UPDATE |",
        "chat_id:", message.chat.id,
        "type:", message.chat.type,
        "text:", bool(message.text),
        "media:", bool(message.media)
    )

# ================== CAPTURE POSTS ==================
@userbot.on_message(filters.channel | filters.group)
async def capture_post(client: Client, message: Message):
    try:
        # ignore empty service messages
        if not message.text and not message.media:
            return

        code = generate_code()
        POST_MAP[code] = (message.chat.id, message.id)

        link = f"https://t.me/{BOT_USERNAME}?start={code}"

        await bot.send_message(
            OWNER_ID,
            f"✅ New private post captured\n\n"
            f"🔑 Code: `{code}`\n"
            f"🔗 Link: {link}",
            disable_web_page_preview=True
        )

        print(f"CAPTURED POST -> chat:{message.chat.id} msg:{message.id} code:{code}")

    except Exception as e:
        print("CAPTURE ERROR:", e)

# ================== START HANDLER ==================
@bot.on_message(filters.private & filters.command("start"))
async def start_handler(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text(
            "👋 Bot active hai.\n\n"
            "Agar aapke paas valid link hai, us par tap karke aaiye."
        )
        return

    code = message.command[1]

    if code not in POST_MAP:
        await message.reply_text("❌ Invalid ya expired link.")
        return

    chat_id, msg_id = POST_MAP[code]

    try:
        sent = await userbot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=chat_id,
            message_id=msg_id
        )

        # auto delete after 5 minutes (optional)
        await asyncio.sleep(300)
        await sent.delete()

    except Exception as e:
        await message.reply_text("❌ Post send nahi ho paayi.")
        print("SEND ERROR:", e)

# ================== MAIN ==================
async def main():
    await bot.start()
    await userbot.start()
    print("🚀 Bot + Userbot running (FINAL)")
    await idle()
    await bot.stop()
    await userbot.stop()

if __name__ == "__main__":
    asyncio.run(main())

