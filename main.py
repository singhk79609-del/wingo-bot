import os
import random
import threading
import hashlib
import sqlite3
from datetime import datetime

import pytz
import telebot
from telebot import types
from flask import Flask


TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# Aapki Admin Telegram ID (Broadcast ke liye)
ADMIN_ID = 7095994825


# ==========================================================
# ALL USERS
# ==========================================================

# Current running bot ke users
all_users = set()

# User database
DB_FILE = "users.db"


def init_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY
        )
    """)

    conn.commit()
    conn.close()


def save_user(chat_id):
    # Memory me save
    all_users.add(chat_id)

    # Database me save
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT OR IGNORE INTO users (chat_id) VALUES (?)",
            (chat_id,)
        )

        conn.commit()
        conn.close()

    except Exception as e:
        print("Database save error:", e)


def load_users():
    users = set()

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("SELECT chat_id FROM users")
        rows = cursor.fetchall()

        conn.close()

        for row in rows:
            users.add(row[0])

    except Exception as e:
        print("Database load error:", e)

    return users


def get_all_users():
    # Memory + database users
    users = set(all_users)

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("SELECT chat_id FROM users")
        rows = cursor.fetchall()

        conn.close()

        for row in rows:
            users.add(row[0])

    except Exception as e:
        print("Database read error:", e)

    return users


# Database initialize
init_database()

# Existing database users memory me load karo
all_users.update(load_users())


# ==========================================================
# WEBHOOK CLEAR
# ==========================================================

try:
    bot.remove_webhook(drop_pending_updates=True)
except Exception as e:
    print("Webhook clear error:", e)


# ==========================================================
# FLASK WEB SERVER
# ==========================================================

app = Flask(__name__)


@app.route('/')
def home():
    return "Wingo 24/7 Prediction Bot is Running!"


def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


# ==========================================================
# IST TIME ZONE
# ==========================================================

ist = pytz.timezone('Asia/Kolkata')


# ==========================================================
# PERIOD
# ==========================================================

def get_current_period():
    now = datetime.now(ist)
    date_str = now.strftime("%Y%m%d")

    # Din ke total minutes calculate karna
    total_minutes = now.hour * 60 + now.minute

    # Real Wingo game sequence ke sath match karne ke liye offset (-329)
    game_serial = total_minutes - 329

    # Standard Period Format
    period_no = f"{date_str}1000{game_serial:04d}"

    return period_no


# ==========================================================
# PREDICTION
# ==========================================================

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


# ==========================================================
# MAIN KEYBOARD
# ==========================================================

def main_keyboard():
    markup = types.ReplyKeyboardMarkup(
        row_width=2,
        resize_keyboard=True
    )

    btn1 = types.KeyboardButton("🎯 Get Prediction")
    btn2 = types.KeyboardButton("📝 Registration Process")
    btn3 = types.KeyboardButton("📢 Official Channel")

    markup.add(btn1)
    markup.add(btn2, btn3)

    return markup


# ==========================================================
# START
# ==========================================================

@bot.message_handler(commands=['start'])
def send_welcome(message):

    # User save
    save_user(message.chat.id)

    bot.reply_to(
        message,
        "Welcome to Wingo 1-Min Prediction Bot! 🎰\n"
        "Niche diye gaye buttons ka use karein:",
        reply_markup=main_keyboard()
    )


# ==========================================================
# TEXT BROADCAST
# ==========================================================

@bot.message_handler(commands=['broadcast'])
def handle_broadcast(message):

    # Sirf Admin
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(
            message,
            "Aap is command ko use nahi kar sakte!"
        )
        return

    text_to_send = message.text.replace(
        '/broadcast',
        '',
        1
    ).strip()

    if not text_to_send:
        bot.reply_to(
            message,
            "Kripya broadcast message likhein.\n\n"
            "Example:\n"
            "/broadcast Hello everyone"
        )
        return

    users = get_all_users()

    success = 0
    failed = 0

    for chat_id in users:
        try:
            bot.send_message(
                chat_id,
                text_to_send
            )

            success += 1

        except Exception as e:
            failed += 1

            print(
                f"Text broadcast failed for {chat_id}: {e}"
            )

    bot.reply_to(
        message,
        f"Broadcast complete!\n"
        f"Success: {success}\n"
        f"Failed: {failed}"
    )


# ==========================================================
# IMAGE + TEXT BROADCAST
# ==========================================================

@bot.message_handler(content_types=['photo'])
def handle_photo_broadcast(message):

    # Sirf Admin photo broadcast kar sakta hai
    if message.from_user.id != ADMIN_ID:
        save_user(message.chat.id)
        return

    # Photo ke saath likha hua caption
    caption = message.caption or ""

    # Highest quality photo
    photo_id = message.photo[-1].file_id

    users = get_all_users()

    success = 0
    failed = 0

    for chat_id in users:

        try:
            bot.send_photo(
                chat_id,
                photo_id,
                caption=caption
            )

            success += 1

        except Exception as e:
            failed += 1

            print(
                f"Image broadcast failed for {chat_id}: {e}"
            )

    bot.reply_to(
        message,
        f"Image Broadcast complete!\n"
        f"Success: {success}\n"
        f"Failed: {failed}"
    )


# ==========================================================
# GET PREDICTION
# ==========================================================

@bot.message_handler(
    func=lambda message: message.text == "🎯 Get Prediction"
)
def handle_prediction(message):

    save_user(message.chat.id)

    period, size = get_deterministic_prediction(
        get_current_period()
    )

    text = (
        f"📊 **WINGO 1 MIN SMART PREDICTION** 📊\n\n"
        f"🔹 **PERIOD NUMBER:** `{period}`\n"
        f"🔹 **PREDICTED RESULT:** {size}\n"
        f"🔹 **PATTERN STATUS:** Active Trend Follower\n\n"
        f"💰 **PLAY WITH 7 LEVEL FUND**\n"
        f"⚠️ **PLAY AT YOUR OWN RISK**"
    )

    bot.send_message(
        message.chat.id,
        text,
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )


# ==========================================================
# REGISTRATION PROCESS
# ==========================================================

@bot.message_handler(
    func=lambda message: message.text == "📝 Registration Process"
)
def handle_register(message):

    save_user(message.chat.id)

    reg_text = (
        "📝 **Registration Process**\n\n"
        "Apna account successfully create karne ke liye "
        "niche diye gaye link par click karein:\n"
        "🔗 **REGISTER LINK:** "
        "https://www.82winoo.com/#/register?"
        "invitationCode=782544845183"
    )

    bot.send_message(
        message.chat.id,
        reg_text,
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )


# ==========================================================
# OFFICIAL CHANNEL
# ==========================================================

@bot.message_handler(
    func=lambda message: message.text == "📢 Official Channel"
)
def handle_channel(message):

    save_user(message.chat.id)

    channel_text = (
        "📢 **Join Our Official Telegram Channel**\n\n"
        "Latest updates aur daily signals ke liye "
        "channel join karein:\n"
        "🔗 **CHANNEL LINK:** "
        "https://t.me/rajagamesnumbersurshot"
    )

    bot.send_message(
        message.chat.id,
        channel_text,
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )


# ==========================================================
# OTHER USER MESSAGES
# ==========================================================

@bot.message_handler(func=lambda message: True)
def track_all_users(message):

    # Jo bhi user bot ko message bheje, save hoga
    save_user(message.chat.id)


# ==========================================================
# START BOT
# ==========================================================

if __name__ == '__main__':

    threading.Thread(
        target=run_flask
    ).start()

    bot.infinity_polling(
        skip_pending=True
    )
