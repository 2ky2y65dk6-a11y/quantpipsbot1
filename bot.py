import os
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

trades = []

def calc_pips(entry, exit_price, direction):
    if direction == "BUY":
        return (exit_price - entry) * 10000
    else:
        return (entry - exit_price) * 10000

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.upper()

    if text.startswith("BUY") or text.startswith("SELL"):
        try:
            direction, price = text.split()
            price = float(price)
            trades.append((direction, price))
            await update.message.reply_text(f"{direction} opened at {price}")
        except:
            await update.message.reply_text("Use: BUY 1.1000 or SELL 1.1000")

    elif text.startswith("CLOSE"):
        try:
            exit_price = float(text.split()[1])

            if not trades:
                await update.message.reply_text("No open trades")
                return

            direction, entry = trades.pop(0)
            pips = calc_pips(entry, exit_price, direction)

            await update.message.reply_text(f"Pips: {pips:.1f}")

        except:
            await update.message.reply_text("Use: CLOSE 1.1050")

app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

app.run_polling()