import os
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)

# ---------------- ENV ----------------
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

SOURCE_CHAT_ID = int(os.getenv("SOURCE_CHAT_ID"))  # private channel/group id
DELETE_TIME = 300  # 5 minutes

# ---------------- BOT ----------------
bot = Client(
    "link-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ---------------- START ----------------
@bot.on_message(filters.command("start"))
async def start_handler(client, message):
    await message.reply_text(
        "🤖 Bot running!\n\nSend /get <message_id>"
    )

# ---------------- GET POST ----------------
@bot.on_message(filters.command("get"))
async def get_post(client, message):
    try:
        if len(message.command) != 2:
            await message.reply_text("Usage: /get <message_id>")
            return

        msg_id = int(message.command[1])
        chat_id = message.chat.id

        log.info(f"CAPTURED -> {msg_id}")

        # fetch message from source
        src_msg = await client.get_messages(SOURCE_CHAT_ID, msg_id)

        # send to user
        sent = await src_msg.copy(chat_id)

        await message.reply_text(
            f"✅ Post sent!\n🗑 Auto delete in 5 minutes",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("❌ Delete Now", callback_data=f"del_{sent.id}")]]
            )
        )

        # auto delete after 5 min
        asyncio.create_task(auto_delete(chat_id, sent.id))

    except Exception as e:
        log.error(f"SEND ERROR: {e}")
        await message.reply_text("❌ Post not found or error occurred")

# ---------------- DELETE BUTTON ----------------
@bot.on_callback_query(filters.regex("^del_"))
async def delete_now(client, query):
    msg_id = int(query.data.split("_")[1])
    chat_id = query.message.chat.id

    try:
        await client.delete_messages(chat_id, msg_id)
        await query.message.edit_text("🗑 Deleted manually")
    except:
        await query.answer("Already deleted", show_alert=True)

# ---------------- AUTO DELETE ----------------
async def auto_delete(chat_id, msg_id):
    await asyncio.sleep(DELETE_TIME)
    try:
        await bot.delete_messages(chat_id, msg_id)
        log.info(f"AUTO DELETED -> {msg_id}")
    except:
        pass

# ---------------- RUN ----------------
if __name__ == "__main__":
    log.info("🚀 FINAL BOT RUNNING")
    bot.run()
