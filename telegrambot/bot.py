# telegrambot/bot.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)
from telegram.ext import filters

from .models import DataCenter
from .services import update_vps_bandwidth
from asgiref.sync import sync_to_async

# Step states
SELECT_DC, ENTER_VPSID, ENTER_BANDWIDTH, CONFIRM_BANDWIDTH = range(4)

# Whitelisted user IDs
ALLOWED_USERS = [185097996]  # Replace with actual Telegram user IDs

# Temporary session data
user_data_sessions = {}

@sync_to_async
def get_data_centers():
    return list(DataCenter.objects.all())

@sync_to_async
def call_update_vps_bandwidth(dc_id, vpsid, bandwidth):
    return update_vps_bandwidth(dc_id, vpsid, bandwidth)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        await update.message.reply_text("🚫 Access Denied.")
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton("➕ Add Bandwidth", callback_data='add_bandwidth')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome! 👋 Choose an option:", reply_markup=reply_markup)
    return SELECT_DC

async def add_bandwidth_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    dcs = await get_data_centers()
    buttons = [[InlineKeyboardButton(dc.name, callback_data=f'dc_{dc.id}')] for dc in dcs]
    reply_markup = InlineKeyboardMarkup(buttons)

    await query.edit_message_text("Please choose a Data Center:", reply_markup=reply_markup)
    return ENTER_VPSID

async def select_datacenter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    dc_id = int(query.data.split('_')[1])
    user_id = update.effective_user.id
    user_data_sessions[user_id] = {'dc_id': dc_id}

    await query.edit_message_text("Please enter the VPS ID:")
    return ENTER_BANDWIDTH

async def receive_vpsid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_data_sessions:
        await update.message.reply_text("Session expired. Please start again.")
        return ConversationHandler.END

    user_data_sessions[user_id]['vpsid'] = update.message.text
    await update.message.reply_text("Now enter the new Bandwidth (e.g. 100 for 100GB):")
    return CONFIRM_BANDWIDTH

async def receive_bandwidth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_data_sessions:
        await update.message.reply_text("Session expired. Please start again.")
        return ConversationHandler.END

    session = user_data_sessions[user_id]
    dc_id = session['dc_id']
    vpsid = session['vpsid']
    bandwidth = update.message.text

    await update.message.reply_text("⏳ Updating bandwidth...")

    result = await call_update_vps_bandwidth(dc_id, vpsid, bandwidth)

    if result and not result.get('error'):
        await update.message.reply_text(f"✅ Bandwidth updated for VPS {vpsid}!")
    else:
        await update.message.reply_text(f"❌ Failed: {result.get('error')}")

    user_data_sessions.pop(user_id, None)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Operation cancelled.")
    return ConversationHandler.END
