# bot.py
import os
import re
import subprocess
import requests
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN missing in environment variables")

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Bot is running successfully!"

# URL check regex
URL_PATTERN = re.compile(r'(https?://[^\s]+)')

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "👋 *Welcome to the YouTube Info Bot!*\n\n"
        "Send me any video link (YouTube, Instagram, TikTok, etc.)\n"
        "and I'll fetch the title, size info, and give you a redirect link.\n\n"
        "_(Note: This bot doesn’t download — only shows safe info)_",
        parse_mode="Markdown"
    )

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Just send a YouTube or any video URL to get its information 🔍"
    )

def get_video_info(url):
    """Fetches video info using oEmbed API"""
    try:
        response = requests.get(f"https://www.youtube.com/oembed?url={url}&format=json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "title": data.get("title", "Unknown title"),
                "author": data.get("author_name", ""),
                "thumbnail": data.get("thumbnail_url", "")
            }
        else:
            return None
    except Exception:
        return None

def handle_message(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    url_match = URL_PATTERN.search(text)
    if not url_match:
        update.message.reply_text("❗ Please send a valid video link.")
        return

    url = url_match.group(1)
    info = get_video_info(url)

    if info:
        caption = f"🎬 *{info['title']}*\n👤 {info['author']}"
        buttons = [[InlineKeyboardButton("🔗 Open on YouTube", url=url)]]
        if info["thumbnail"]:
            update.message.reply_photo(photo=info["thumbnail"], caption=caption,
                                       reply_markup=InlineKeyboardMarkup(buttons),
                                       parse_mode="Markdown")
        else:
            update.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")
    else:
        update.message.reply_text("⚠️ Unable to fetch info from that link. Try another one!")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    print("✅ Bot started successfully.")
    updater.idle()

if __name__ == "__main__":
    import threading
    threading.Thread(target=main).start()
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)