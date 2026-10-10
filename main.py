import os
import random
import threading
import hashlib
from datetime import datetime
import pytz
import telebot
from telebot import types
from flask import Flask
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# Admin Telegram ID
ADMIN_ID = 7095994825

# Broadcast List
all_users = set()

# Clear Webhook
try:
    bot.remove_webhook(drop_pending_updates=True)
except Exception as e:
    print("Webhook clear error:", e)

# Flask Web Server
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
    total_minutes = now.hour * 60 + now.minute
    game_serial = total_minutes - 329
    period_no = f"{date_str}1000{game_serial:04d}"
    return period_no

def get_deterministic_prediction(period_str):
    hash_object = hashlib.sha256(period_str.encode())
    hash_hex = hash_object.hexdigest()
    primary_num = int(hash_hex, 16) % 10  
    
    # Logic for BIG (5-9) and SMALL (0-4)
    if primary_num in [5, 6, 7, 8, 9]:
        size = "BIG"
        possible_other = [n for n in [5, 6, 7, 8, 9] if n != primary_num]
        secondary_num = random.choice(possible_other)
    else:
        size = "SMALL"
        possible_other = [n for n in [0, 1, 2, 3, 4] if n != primary_num]
        secondary_num = random.choice(possible_other)
        
    number_display = f"{primary_num} / {secondary_num}"
    return period_str, size, number_display

def create_prediction_image(period, size, number_str):
    # Create prediction banner image on the fly
    img = Image.new('RGB', (800, 400), color=(15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    # Outer Border
    draw.rectangle([(10, 10), (790, 390)], outline=(255, 215, 0), width=4)
    
    # Text Content
    draw.text((220, 30), "maan.win 1 Min Bot", fill=(255, 215, 0))
    draw.text((50, 100), f"PERIOD : {period}", fill=(255, 255, 255))
    
    # Big / Small Color
    color = (0, 255, 127) if size == "BIG" else (255, 69, 0)
    draw.text((50, 170), f"PREDICTION : {size}", fill=color)
    draw.text((50, 240), f"NUMBERS : {number_str}", fill=(255, 255, 255))
    draw.text((180, 330), "⚠️ MAINTAIN 7 LEVEL FUNDS ⚠️", fill=(255, 215, 0))
    
    # Save image to memory buffer
    bio = BytesIO()
    bio.name = 'prediction.png'
    img.save(bio, 'PNG')
    bio.seek(0)
    return bio

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
    all_users.add(message.chat.id)
    bot.reply_to(
        message, 
        "Welcome to Wingo 1-Min Prediction Bot! 🎰\nNiche diye gaye buttons ka use karein:", 
        reply_markup=main_keyboard()
    )

@bot.message_handler(func=lambda message: True)
def track_all_users(message):
    all_users.add(message.chat.id)

@bot.message_handler(commands=['broadcast'])
def handle_broadcast(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "Aap is command ko use nahi kar sakte!")
        return
        
    text_to_send = message.text.replace('/broadcast', '').strip()
    if not text_to_send:
        bot.reply_to(message, "Kripya broadcast message likhein. Jaise: /broadcast Hello everyone")
        return
        
    success = 0
    failed = 0
    for chat_id in all_users:
        try:
            bot.send_message(chat_id, text_to_send)
            success += 1
        except Exception as e:
            failed += 1
            
    bot.reply_to(message, f"Broadcast complete!\nSuccess: {success}\nFailed: {failed}")

@bot.message_handler(func=lambda message: message.text == "🎯 Get Prediction")
def handle_prediction(message):
    all_users.add(message.chat.id)
    period, size, number_display = get_deterministic_prediction(get_current_period())
    
    # Short period ID extraction (e.g., last 4 digits)
    short_period = period[-4:] if len(period) >= 4 else period

    formatted_text = (
        "═══════════════════════════\n"
        "     🎯 POWERED BY ANMOL SINGH\n"
        "═══════════════════════════\n"
        "           🎰 𝗪𝗜𝗡𝗚𝗢 𝟭 𝗠𝗜𝗡𝗨𝗧𝗘🎰\n\n"
        f"🗿 𝗣𝗘𝗥𝗜𝗢𝗗: {short_period}\n"
        f"🎲 𝗣𝗥𝗘𝗗𝗜𝗖𝗧𝗜𝗢𝗡: {size}\n"
        f"🎯 𝗡𝗨𝗠𝗕𝗘𝗥: {number_display}\n\n"
        "⚠  𝟳 𝗟𝗘𝗩𝗘𝗟 𝗠𝗘𝗡𝗧𝗘𝗡 𝗔𝗟𝗟 𝗧𝗜𝗠𝗘  ⚠️ \n\n"
        "═══════════════════════════\n"
        " ☠️ 𝗣𝗢𝗪𝗘𝗥 𝗢𝗙 𝗛𝗔𝗖𝗞: POWERED BY ANMOL SINGH\n"
        "═══════════════════════════"
    )
    
    try:
        # Generate & Send Photo with Caption
        img_buffer = create_prediction_image(short_period, size, number_display)
        bot.send_photo(
            message.chat.id, 
            photo=img_buffer, 
            caption=formatted_text, 
            reply_markup=main_keyboard()
        )
    except Exception as e:
        print("Image send error:", e)
        # Fallback to Text if image generation fails
        bot.send_message(message.chat.id, formatted_text, reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: message.text == "📝 Registration Process")
def handle_register(message):
    all_users.add(message.chat.id)
    reg_text = (
        "📝 **Registration Process**\n\n"
        "Apna account successfully create karne ke liye niche diye gaye link par click karein:\n"
        "🔗 **REGISTER LINK:** https://maanwin24.com/register?inviteCode=AEATD8N&from=web"
    )
    bot.send_message(message.chat.id, reg_text, parse_mode="Markdown", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: message.text == "📢 Official Channel")
def handle_channel(message):
    all_users.add(message.chat.id)
    channel_text = (
        "📢 **Join Our Official Telegram Channel**\n\n"
        "Latest updates aur daily signals ke liye channel join karein:\n"
        "🔗 **CHANNEL LINK:** https://t.me/rajagamesnumbersurshot"
    )
    bot.send_message(message.chat.id, channel_text, parse_mode="Markdown", reply_markup=main_keyboard())

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    bot.infinity_polling(skip_pending=True)
