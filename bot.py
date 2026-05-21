import os
from telegram.ext import Application, MessageHandler, filters

TOKEN = os.getenv("BOT_TOKEN")

async def handle_message(update, context):
    await update.message.reply_text("Bot is running ✅")

app = Application.builder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT, handle_message))

print("Bot running...")
app.run_polling()