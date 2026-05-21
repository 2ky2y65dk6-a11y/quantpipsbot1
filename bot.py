import os
import re
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

# store trades in memory (we improve later with database)
trades = []

def extract_price_range(text):
    match = re.search(r"(\d+\.?\d*)\s*-\s*(\d+\.?\d*)", text)
    if match:
        return float(match.group(1)), float(match.group(2))
    return None, None

def extract_prices(text):
    return re.findall(r"\d+\.?\d*", text)

def calc_pips(entry, exit_price, direction):
    if direction == "BUY":
        return (exit_price - entry) * 10000
    else:
        return (entry - exit_price) * 10000

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.upper()

    # detect BUY or SELL signal
    if "BUY" in text or "SELL" in text:
        direction = "BUY" if "BUY" in text else "SELL"

        # extract entry zone (e.g. 4522.50 - 4518.50)
        high, low = extract_price_range(text)

        if high and low:
            entry = (high + low) / 2  # middle of zone
        else:
            prices = extract_prices(text)
            entry = float(prices[0]) if prices else None

        if entry:
            trades.append((direction, entry))
            await update.message.reply_text(
                f"{direction} recorded\nEntry: {entry:.2f}"
            )
        else:
            await update.message.reply_text("No valid entry found")

    # close trade manually
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
            await update.message.reply_text("Use: CLOSE 4525")

app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

app.run_polling()