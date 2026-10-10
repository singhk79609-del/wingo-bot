import time
import threading
import os
import random
import datetime
import json
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from PIL import Image, ImageDraw, ImageFont
from http.server import HTTPServer, BaseHTTPRequestHandler

# --------- HEALTH CHECK FOR RENDER ---------
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# ---------------- CONFIG ----------------
TOKEN = os.getenv("BOT_TOKEN")

OFFICIAL_CHANNEL_URL = "https://t.me/rajagamesnumbersurshot"
REGISTER_LINK_URL = "https://maanwin24.com/register?inviteCode=AEATD8N&from=web"
TARGET_CHANNEL = "@fakegoogle12345"  

# Aapki Permanent Admin ID
ADMIN_USER_ID = 7095994825
USERS_FILE = "users.json"

bot = telebot.TeleBot(TOKEN)

total_wins = 1421
current_streak = 2

# --- USER STORAGE FUNCTIONS ---
def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_user(user_id):
    users = load_users()
    if user_id not in users:
        users.add(user_id)
        with open(USERS_FILE, "w") as f:
            json.dump(list(users), f)

def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = KeyboardButton("Get Prediction")
    btn3 = KeyboardButton("📢 Official Channel")
    btn4 = KeyboardButton("🔗 Register Link")
    keyboard.add(btn1, btn3, btn4)
    return keyboard

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    save_user(message.chat.id)
    bot.send_message(
        message.chat.id,
        "🤖 <b>MAAN WIN PREDICTION BOT CONNECTED</b>\nClick 'Get Prediction' to generate and post signals.",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

@bot.message_handler(func=lambda message: message.text == "📢 Official Channel")
def official_channel_handler(message):
    save_user(message.chat.id)
    msg = (
        "📢 <b>Join Our Official Telegram Channel</b>\n\n"
        "Latest updates aur daily signals ke liye channel join karein:\n"
        f"🔗 CHANNEL LINK: {OFFICIAL_CHANNEL_URL}"
    )
    bot.send_message(message.chat.id, msg, parse_mode="HTML")

@bot.message_handler(func=lambda message: message.text == "🔗 Register Link")
def register_link_handler(message):
    save_user(message.chat.id)
    msg = (
        "📝 <b>Registration Process</b>\n\n"
        "Apna account successfully create karne ke liye niche diye gaye link par click karein:\n"
        f"🔗 REGISTER LINK: {REGISTER_LINK_URL}"
    )
    bot.send_message(message.chat.id, msg, parse_mode="HTML")

# --- MANUAL "GET PREDICTION" BUTTON HANDLER ---
@bot.message_handler(func=lambda message: message.text == "Get Prediction")
def handle_get_prediction(message):
    save_user(message.chat.id)
    global total_wins, current_streak
    
    # Exact UTC time-based period calculation
    now_utc = datetime.datetime.utcnow()
    date_str = now_utc.strftime("%Y%m%d")
    total_minutes = (now_utc.hour * 60) + now_utc.minute + 1
    seq_str = f"{total_minutes:04d}"
    
    next_period_num = f"{date_str}10001{seq_str}"
    short_next_period = next_period_num[-4:]
    
    trends = ["GREEN", "RED"]
    sizes = ["BIG", "SMALL"]
    
    trend = random.choice(trends)
    size_trend = random.choice(sizes)
    
    if size_trend == "SMALL":
        pred_number_str = random.choice(["1 / 3", "0 / 2", "4 / 1"])
    else:
        pred_number_str = random.choice(["6 / 8", "5 / 7", "9 / 6"])
    
    prediction_text = (
        f"═══════════════════════════\n"
        f"     🎯 <b>POWERED BY MAAN WIN</b>\n"
        f"═══════════════════════════\n"
        f"           🎰 <b>𝗪𝗜𝗡𝗚𝗢 𝟭 𝗠𝗜𝗡𝗨𝗧𝗘</b>🎰\n\n"
        f"🗿 <b>𝗣𝗘𝗥𝗜𝗢𝗗:</b> {short_next_period}\n"
        f"🎲 <b>𝗣𝗥𝗘𝗗𝗜𝗖𝗧𝗜𝗢𝗡:</b> {trend} ({size_trend})\n"
        f"🎯 <b>𝗡𝗨𝗠𝗕𝗘𝗥:</b> {pred_number_str}\n\n"
        f"⚠️  <b>𝟳 𝗟𝗘𝗩𝗘𝗟 𝗠𝗘𝗡𝗧𝗘𝗡 𝗔𝗟𝗟 𝗧𝗜𝗠𝗘</b>  ⚠️\n\n"
        f"🔗 <b>REGISTER LINK:</b> {REGISTER_LINK_URL}\n\n"
        f"═══════════════════════════\n"
        f" ☠️ <b>𝗣𝗢𝗪𝗘𝗥 𝗢𝗙 :</b> @maanwin123_bot\n"
        f"═══════════════════════════"
    )
    
    img_path = generate_prediction_image(short_next_period, size_trend, pred_number_str, total_wins, current_streak)
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔗 REGISTER HERE", url=REGISTER_LINK_URL))
    
    try:
        with open(img_path, 'rb') as photo:
            bot.send_photo(TARGET_CHANNEL, photo, caption=prediction_text, reply_markup=markup, parse_mode="HTML")
        bot.reply_to(message, "✅ Prediction successfully sent to channel!")
    except Exception as err:
        bot.reply_to(message, f"❌ Send Error: {err}")

# --- DIRECT ADMIN BROADCAST TO BOT USERS ONLY ---
@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_USER_ID and message.text not in ["Get Prediction", "📢 Official Channel", "🔗 Register Link"])
def direct_admin_broadcast(message):
    users = load_users()
    if not users:
        bot.reply_to(message, "⚠️ Abhi tak koi user bot me add nahi hua hai!")
        return

    success_count = 0
    fail_count = 0

    for u_id in users:
        try:
            bot.send_message(u_id, message.text)
            success_count += 1
            time.sleep(0.05)
        except Exception:
            fail_count += 1

    bot.reply_to(message, f"📢 <b>Broadcast Finished!</b>\n✅ Sent to: {success_count} users\n❌ Failed: {fail_count} users", parse_mode="HTML")

@bot.message_handler(content_types=['photo'], func=lambda message: message.from_user.id == ADMIN_USER_ID)
def direct_admin_photo_broadcast(message):
    users = load_users()
    if not users:
        bot.reply_to(message, "⚠️ Abhi tak koi user bot me add nahi hua hai!")
        return

    photo_id = message.photo[-1].file_id
    caption = message.caption if message.caption else ""

    success_count = 0
    fail_count = 0

    for u_id in users:
        try:
            bot.send_photo(u_id, photo_id, caption=caption)
            success_count += 1
            time.sleep(0.05)
        except Exception:
            fail_count += 1

    bot.reply_to(message, f"📢 <b>Photo Broadcast Finished!</b>\n✅ Sent to: {success_count} users\n❌ Failed: {fail_count} users", parse_mode="HTML")

def generate_prediction_image(period, trend, number_str, wins, streak):
    img_width, img_height = 800, 900
    image = Image.new("RGB", (img_width, img_height), color=(10, 5, 15))
    draw = ImageDraw.Draw(image)
    try:
        font_large = ImageFont.truetype("arial.ttf", 45)
        font_med = ImageFont.truetype("arial.ttf", 30)
    except:
        font_large = font_med = ImageFont.load_default()

    draw.rectangle([40, 40, 760, 140], fill=(30, 10, 25), outline=(255, 100, 150), width=3)
    draw.text((70, 60), "WinGo 1 Min AI PREDICTION", fill=(255, 255, 255), font=font_large)
    
    draw.rectangle([40, 160, 380, 240], fill=(20, 40, 25), outline=(0, 255, 100), width=2)
    draw.text((60, 185), f"🏆 WIN  {wins}", fill=(0, 255, 100), font=font_med)
    
    draw.rectangle([420, 160, 760, 240], fill=(40, 30, 10), outline=(255, 165, 0), width=2)
    draw.text((440, 185), f"🔥 STREAK  {streak}", fill=(255, 165, 0), font=font_med)

    draw.rectangle([40, 280, 760, 500], fill=(50, 15, 25), outline=(255, 50, 100), width=4)
    draw.text((220, 330), f"{trend}", fill=(255, 50, 100), font=font_large)
    draw.text((240, 410), f"PERIOD: {period}", fill=(255, 255, 255), font=font_med)

    draw.rectangle([40, 540, 760, 680], fill=(20, 20, 35), outline=(100, 150, 255), width=3)
    draw.text((70, 580), f"TARGET NUMBER: {number_str}", fill=(255, 255, 255), font=font_med)

    file_path = "dynamic_prediction.png"
    image.save(file_path)
    return file_path

if __name__ == "__main__":
    bot.infinity_polling()
