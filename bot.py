import os
from pyrogram import Client, filters

app = Client(
    "railwaybot",
    api_id=int(os.environ["API_ID"]),
    api_hash=os.environ["API_HASH"],
    bot_token=os.environ["BOT_TOKEN"]
)

@app.on_message(filters.private)
async def start(client, message):
    await message.reply("✅ Bot alive hai. Basic setup OK.")

print("Bot starting...")
app.run()
