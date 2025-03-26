# telegrambot/run_bot.py

import os
import sys

# Add project root to Python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')  # Update 'core' if needed

import django
django.setup()

# Import bot handlers after Django setup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, filters
)
from telegrambot.bot import (
    start, add_bandwidth_click, select_datacenter,
    receive_vpsid, receive_bandwidth, cancel,
    SELECT_DC, ENTER_VPSID, ENTER_BANDWIDTH, CONFIRM_BANDWIDTH
)

# Bot token
BOT_TOKEN = '8043530468:AAF8uXP1ytEez6lJ754_V5vgGSGBbxzmU6A'  # Replace with your actual bot token

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECT_DC: [CallbackQueryHandler(add_bandwidth_click, pattern='^add_bandwidth$')],
            ENTER_VPSID: [CallbackQueryHandler(select_datacenter, pattern='^dc_')],
            ENTER_BANDWIDTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_vpsid)],
            CONFIRM_BANDWIDTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_bandwidth)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True,
    )

    app.add_handler(conv_handler)
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
