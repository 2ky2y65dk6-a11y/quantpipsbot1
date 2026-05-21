import os
import re
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

active_trade = None

# ------------------ HELPERS ------------------

def extract_zone(text):
    match = re.search(r"(\d+\.?\d*)\s*-\s*(\d+\.?\d*)", text)
    if match:
        return (float(match.group(1)) + float(match.group(2))) / 2
    return None

def extract_numbers(text):
    return [float(x) for x in re.findall(r"\d+\.?\d*", text)]

def extract_tps(text):
    return [float(x) for x in re.findall(r"TP\d*\D*(\d+\.?\d*)", text)]

def extract_sl(text):
    match = re.search(r"SL[^0-9]*([\d.]+)", text)
    return float(match.group(1)) if match else None

def calc_pips(entry, price):
    # gold simplified system
    return (price - entry) * 10000


# ------------------ MAIN HANDLER ------------------

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global active_trade

    text = update.message.text.upper()

    # ================== NEW TRADE ==================
    if "BUY" in text or "SELL" in text:
        direction = "BUY" if "BUY" in text else "SELL"

        entry = extract_zone(text)
        if not entry:
            nums = extract_numbers(text)
            entry = nums[0] if nums else None

        active_trade = {
            "direction": direction,
            "entry": entry,
            "tp": extract_tps(text),
            "sl": extract_sl(text)
        }

        await update.message.reply_text(
            f"TRADE STORED ✅\n"
            f"{direction}\n"
            f"Entry: {entry}\n"
            f"TPs: {active_trade['tp']}\n"
            f"SL: {active_trade['sl']}"
        )
        return

    # ================== TP HIT (ONLY FORMAT: TP4 HIT) ==================
    if "TP" in text and "HIT" in text:

        if not active_trade:
            await update.message.reply_text("No active trade ❌")
            return

        # ONLY accept clean format TP4 HIT
        match = re.search(r"TP\s*(\d+)", text)

        if not match:
            await update.message.reply_text("Use: TP4 HIT (no numbers needed)")
            return

        tp_index = int(match.group(1)) - 1

        if tp_index < 0 or tp_index >= len(active_trade["tp"]):
            await update.message.reply_text("TP level not found in trade ❌")
            return

        tp_price = active_trade["tp"][tp_index]
        entry = active_trade["entry"]

        if entry is None:
            await update.message.reply_text("No entry found ❌")
            return

        pips = calc_pips(entry, tp_price)

        await update.message.reply_text(
            f"🎯 TP{tp_index+1} HIT\n"
            f"Entry: {entry}\n"
            f"TP Price: {tp_price}\n"
            f"Profit: +{pips:.1f} pips"
        )
        return

    # ================== DAILY / WEEKLY (basic) ==================
    if text == "DAILY":
        await update.message.reply_text("📊 DAILY REPORT\n(Upgrade coming soon)")

    if text == "WEEKLY":
        await update.message.reply_text("📅 WEEKLY REPORT\n(Upgrade coming soon)")


# ------------------ START BOT ------------------

app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

print("Bot running...")
app.run_polling()