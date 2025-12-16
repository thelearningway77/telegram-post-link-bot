import os
import asyncio
import uuid
from pyrogram import Client, filters
from pyrogram.types import Message

# ===== ENV =====
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
SESSION_STRING = os.environ["SESSION_STRING"]

# ===== CLIENTS =====
bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

user = Client(
    "user",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

# ===== STORAGE (in-memory for now) =====
POST_MAP = {}   # code -> (chat_id, message_id)

# ===== USERBOT: LISTEN PRIVATE GROUPS =====
@user.on_message(filters.group | filters.channel)
async def capture_posts(_, msg: Message):
    # sirf text / media posts
    if not (msg.text or msg.caption or msg.media):
        return

    code = uuid.uuid4().hex[:8]
    POST_MAP[code] = (msg.chat.id, msg.id)

    print(f"Captured post {msg.chat.id}/{msg.id} -> code={code}")

# ===== BOT: USER REQUEST =====
@bot.on_message(filters.private & filters.command("get"))
async def get_post(_, message: Message):
    # /get CODE
    if len(message.command) != 2:
        await message.reply("Usage: /get CODE")
        return

    code = message.command[1]
    if code not in POST_MAP:
        await message.reply("❌ Invalid or expired code")
        return

    chat_id, msg_id = POST_MAP[code]

    # userbot se copy bhejo (forward nahi)
    sent = await user.copy_message(
        chat_id=message.chat.id,
        from_chat_id=chat_id,
        message_id=msg_id
    )

    await message.reply("⏳ This message will auto-delete in 5 minutes")

    # 5 minutes baad delete
    await asyncio.sleep(300)
    try:
        await sent.delete()
    except:
        pass

# ===== START =====
async def main():
    await user.start()
    await bot.start()
    print("🚀 Bot + Userbot running")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
