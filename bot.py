import os
import logging
import tempfile
import requests
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Bot token from @BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Star-style progress bar
def get_progress_bar(percent: int) -> str:
    c_full = int(percent / 10)
    return f"[{'★' * c_full}{'✩' * (10 - c_full)}] {percent}%"

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to **Gofile Uploader Bot**!\n\n"
        "📤 Just send me any file and I’ll upload it to Gofile.io for you.\n"
        "You'll get a permanent sharable link.\n\n"
        "⚡ Fast, Free, and Simple.\n\n"
        "👨‍💻 Bot by: @l_abani",
        parse_mode="Markdown"
    )

# Handle uploaded files
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    file = msg.document or msg.video or msg.audio or (msg.photo[-1] if msg.photo else None)

    if not file:
        await msg.reply_text("❌ Unsupported file type.")
        return

    tg_file = await file.get_file()
    filename = getattr(file, 'file_name', f"{file.file_unique_id}.bin")
    await msg.reply_text("⬇️ Downloading your file from Telegram...")

    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            await tg_file.download_to_drive(tmp_file.name)
            tmp_path = tmp_file.name

        await msg.reply_text("☁️ Uploading your file to Gofile...")

        # Simulate upload progress
        progress_msg = await msg.reply_text(get_progress_bar(0))
        for percent in range(10, 101, 10):
            await progress_msg.edit_text(get_progress_bar(percent))
            await asyncio.sleep(0.25)

        # Get best Gofile server
        server_resp = requests.get("https://api.gofile.io/getServer").json()
        server = server_resp["data"]["server"]

        # Upload
        with open(tmp_path, 'rb') as f:
            response = requests.post(
                f"https://{server}.gofile.io/uploadFile",
                files={"file": (filename, f)}
            )

        data = response.json()
        if data["status"] == "ok":
            link = data["data"]["downloadPage"]
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("✅ Open File Link", url=link)
            ]])
            await msg.reply_text(
                f"✅ *File uploaded successfully!*\n\n"
                f"🔗 *Link:* {link}\n\n"
                f"Bot by @l_abani",
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        else:
            await msg.reply_text("❌ Failed to upload to Gofile.")

    except Exception as e:
        logger.error(str(e))
        await msg.reply_text("⚠️ Something went wrong. Please try again later.")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# Error handler
async def error_handler(update, context):
    logger.error(f"Error: {context.error}")

# Bot setup
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.Video.ALL | filters.Audio.ALL | filters.PHOTO, handle_file))
    app.add_error_handler(error_handler)

    print("🤖 Bot is running 24/7...")
    app.run_polling()
