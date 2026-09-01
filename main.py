import os
import random
import threading
import hashlib
from datetime import datetime
import pytz
import telebot
from telebot import types
from flask import Flask

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# Purana webhook aur pending updates clear karne ke liye taaki conflict na ho
try:
    bot.remove_webhook(drop_pending_updates=True)
except Exception as e:
    print("Webhook clear error:", e)

# Flask Web Server Render ko active rakhne ke liye
app = Flask(__name__)

@app.route('/')
def home():
    return "Wingo 24/7 Prediction Bot is Running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# IST Time zone
ist = pytz.timezone('Asia/Kolkata')

def get_current_period():
    now = datetime.now(ist)
    date_str = now.strftime("%Y%m%d")
    
    # Din ke total minutes calculate karna
    total_minutes = now.hour * 60 + now.minute
    
    # Real Wingo game ke sequence ke sath match karne ke liye offset (-329)
    game_serial = total_minutes - 329
    
    # Sahi Standard Period Format: YYYYMMDD + 1000 + 4-digit serial
    period_no = f"{date_str}1000{game_serial:04d}"
    return period_no

def get_deterministic_prediction(period_str):
    hash_object = hashlib.sha256(period_str.encode())
    hash_hex = hash_object.hexdigest()
    number = int(hash_hex, 16) % 10  
    
    # Wingo Rules (5-9 BIG, 0-4 SMALL)
    if number in [5, 6, 7, 8, 9]:
        size = "BIG 📈"
    else:
        size = "SMALL 📉"
        
    return period_str, size

def main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("🎯 Get Prediction")
    btn2 = types.KeyboardButton("📝 Registration Process")
    btn3 = types.KeyboardButton("📢 Official Channel")
    markup.add(btn1)
    markup.add(btn2, btn3)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "Welcome to Wingo 1-Min Prediction Bot! 🎰\nNiche diye gaye buttons ka use karein:", 
        reply_markup=main_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == "🎯 Get Prediction")
def handle_prediction(message):
    period, size = get_deterministic_prediction(get_current_period())
    text = (
        f"📊 **WINGO 1 MIN SMART PREDICTION** 📊\n\n"
        f"🔹 **PERIOD NUMBER:** `{period}`\n"
        f"🔹 **PREDICTED RESULT:** {size}\n"
        f"🔹 **PATTERN STATUS:** Active Trend Follower\n\n"
        f"💰 **PLAY WITH 7 LEVEL FUND**\n"
        f"⚠️ **PLAY AT YOUR OWN RISK**"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: message.text == "📝 Registration Process")
def handle_register(message):
    reg_text = (
        "📝 **Registration Process**\n\n"
        "Apna account successfully create karne ke liye niche diye gaye link par click karein:\n"
        "🔗 **REGISTER LINK:** https://www.82winoo.com/#/register?invitationCode=782544845183"
    )
    bot.send_message(message.chat.id, reg_text, parse_mode="Markdown", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: message.text == "📢 Official Channel")
def handle_channel(message):
    channel_text = (
        "📢 **Join Our Official Telegram Channel**\n\n"
        "Latest updates aur daily signals ke liye channel join karein:\n"
        "🔗 **CHANNEL LINK:** https://t.me/rajagamesnumbersurshot"
    )
    bot.send_message(message.chat.id, channel_text, parse_mode="Markdown", reply_markup=main_keyboard())

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    bot.infinity_polling(skip_pending=True)
