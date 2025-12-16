import os
import asyncio
import uuid
from pyrogram import Client, filters
from pyrogram.types import Message

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SOURCE_CHAT_ID = int(os.getenv("SOURCE_CHAT_ID"))
OWNER_ID = int(os.getenv("OWNER_ID"))

app = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

POST_STORE = {}  # code -> message_id


@app.on_message(filters.channel & filters.chat(SOURCE_CHAT_ID))
async def save_post(_, msg: Message):
    code = uuid.uuid4().hex[:8]
    POST_STORE[code] = msg.id

    bot_username = (await app.get_me()).username
    link = f"https://t.me/{bot_username}?start={code}"

    await app.send_message(
        OWNER_ID,
        f"✅ New post saved\n\n🔗 Link:\n{link}"
    )


@app.on_message(filters.private & filters.command("start"))
async def send_post(_, msg: Message):
    if len(msg.command) < 2:
        return await msg.reply("❌ Invalid link")

    code = msg.command[1]
    if code not in POST_STORE:
        return await msg.reply("❌ Link expired or invalid")

    sent = await app.copy_message(
        chat_id=msg.chat.id,
        from_chat_id=SOURCE_CHAT_ID,
        message_id=POST_STORE[code]
    )

    await asyncio.sleep(300)  # 5 minutes
    await sent.delete()


app.run()
