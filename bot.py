import os
import re
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

active_trade = None

def extract_zone(text):
    match = re.search(r"(\d+\.?\d*)\s*-\s*(\d+\.?\d*)", text)
    if match:
        return (float(match.group(1)) + float(match.group(2))) / 2
    return None

def extract_numbers(text):
    return [float(x) for x in re.findall(r"\d+\.?\d*", text)]

def extract_targets(text):
    # handles: TP1, Targets, 🥇TP1 etc.
    nums = re.findall(r"(?:TP\d*|TARGETS?)\D*(\d+\.?\d*)", text)
    if nums:
        return [float(x) for x in nums]

    # fallback: after "TARGETS"
    if "TARGET" in text:
        return extract_numbers(text)

    return []

def extract_sl(text):
    match = re.search(r"SL[^0-9]*([\d.]+)", text)
    if match:
        return float(match.group(1))
    return None

def calc_pips(entry, price):
    return (price - entry) * 10000  # simplified gold calc

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global active_trade

    text = update.message.text.upper()

    # ---------------- NEW TRADE ----------------
    if "BUY" in text or "SELL" in text:
        direction = "BUY" if "BUY" in text else "SELL"

        entry = extract_zone(text)
        if not entry:
            nums = extract_numbers(text)
            entry = nums[0] if nums else None

        active_trade = {
            "direction": direction,
            "entry": entry,
            "tp": extract_targets(text),
            "sl": extract_sl(text)
        }

        await update.message.reply_text(
            f"TRADE STORED ✅\n{direction}\nEntry: {entry}\nTPs: {active_trade['tp']}\nSL: {active_trade['sl']}"
        )
        return

    # ---------------- TP HIT ----------------
    if "TP" in text and "HIT" in text:
        if not active_trade:
            await update.message.reply_text("No active trade")
            return

        nums = extract_numbers(text)
        price = nums[-1] if nums else None

        if not price:
            await update.message.reply_text("Send TP HIT with price")
            return

        entry = active_trade["entry"]
        pips = calc_pips(entry, price)

        await update.message.reply_text(
            f"🎯 TP HIT\nEntry: {entry}\nPrice: {price}\nProfit: +{pips:.1f} pips"
        )
        return

app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

app.run_polling()