import os
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

trades = []

daily_trades = []
weekly_trades = []

def extract_price(text):
    import re
    nums = re.findall(r"\d+\.?\d*", text)
    return [float(n) for n in nums]

def calc_pips(entry, exit_price, direction):
    return (exit_price - entry) * 10000 if direction == "BUY" else (entry - exit_price) * 10000

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.upper()
    chat_id = update.message.chat_id

    # ---------------- SIGNAL DETECTION ----------------
    if "BUY" in text or "SELL" in text:
        direction = "BUY" if "BUY" in text else "SELL"
        prices = extract_price(text)

        if prices:
            entry = prices[0]

            trade = {
                "direction": direction,
                "entry": entry,
                "time": datetime.now()
            }

            trades.append(trade)
            daily_trades.append(trade)
            weekly_trades.append(trade)

            await update.message.reply_text(f"TRADE STORED ✅\n{direction} @ {entry}")

    # ---------------- DAILY SUMMARY ----------------
    elif text == "DAILY":
        total = len(daily_trades)
        await update.message.reply_text(f"📊 DAILY SUMMARY\nTrades: {total}")

    # ---------------- WEEKLY SUMMARY ----------------
    elif text == "WEEKLY":
        total = len(weekly_trades)
        await update.message.reply_text(f"📅 WEEKLY SUMMARY\nTrades: {total}")

app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

app.run_polling()