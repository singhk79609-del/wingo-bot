import time
import threading
import os
import requests
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

bot = telebot.TeleBot(TOKEN)

total_wins = 1421
current_streak = 2

def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = KeyboardButton("Get Prediction")
    btn3 = KeyboardButton("📢 Official Channel")
    btn4 = KeyboardButton("🔗 Register Link")
    keyboard.add(btn1, btn3, btn4)
    return keyboard

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "🤖 **MAAN WIN PREDICTION BOT CONNECTED**\nClick 'Get Prediction' to generate and post signals.",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: message.text == "📢 Official Channel")
def official_channel_handler(message):
    msg = (
        "📢 **Join Our Official Telegram Channel**\n\n"
        "Latest updates aur daily signals ke liye channel join karein:\n"
        f"🔗 CHANNEL LINK: {OFFICIAL_CHANNEL_URL}"
    )
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "🔗 Register Link")
def register_link_handler(message):
    msg = (
        "📝 **Registration Process**\n\n"
        "Apna account successfully create karne ke liye niche diye gaye link par click karein:\n"
        f"🔗 REGISTER LINK: {REGISTER_LINK_URL}"
    )
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

# --- MANUAL "GET PREDICTION" BUTTON HANDLER ---
@bot.message_handler(func=lambda message: message.text == "Get Prediction")
def handle_get_prediction(message):
    global total_wins, current_streak
    
    history = fetch_wingo_data()
    if not history:
        bot.send_message(message.chat.id, "❌ API se data fetch karne mein error aayi. Dobara try karein.")
        return
        
    latest_draw = history[0]
    current_period = str(latest_draw['issueNumber'])
    next_period_num = str(int(current_period) + 1)
    short_next_period = next_period_num[-4:]
    
    nums = [int(x['number']) for x in history[:10]]
    big_count = sum(1 for n in nums if n >= 5)
    trend = "GREEN" if big_count >= 5 else "RED"
    size_trend = "SMALL" if big_count >= 5 else "BIG"
    pred_number_str = "4 / 0" if size_trend == "SMALL" else "6 / 7"
    
    prediction_text = (
        f"═══════════════════════════\n"
        f"     🎯 POWERED BY MAAN WIN\n"
        f"═══════════════════════════\n"
        f"           🎰 𝗪𝗜𝗡𝗚𝗢 𝟭 𝗠𝗜𝗡𝗨𝗧𝗘🎰\n\n"
        f"🗿 𝗣𝗘𝗥𝗜𝗢𝗗: {short_next_period}\n"
        f"🎲 𝗣𝗥𝗘𝗗𝗜𝗖𝗧𝗜𝗢𝗡: {trend} ({size_trend})\n"
        f"🎯 𝗡𝗨𝗠𝗕𝗘𝗥: {pred_number_str}\n\n"
        f"⚠  𝟳 𝗟𝗘𝗩𝗘𝗟 𝗠𝗘𝗡𝗧𝗘𝗡 𝗔𝗟𝗟 𝗧𝗜𝗠𝗘  ⚠️ \n\n"
        f"🔗 **REGISTER LINK:** {REGISTER_LINK_URL}\n\n"
        f"═══════════════════════════\n"
        f" ☠️ 𝗣𝗢𝗪𝗘𝗥 𝗢𝗙 : @maanwin123_bot\n"
        f"═══════════════════════════"
    )
    
    img_path = generate_prediction_image(short_next_period, size_trend, pred_number_str, total_wins, current_streak)
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔗 REGISTER HERE", url=REGISTER_LINK_URL))
    
    try:
        with open(img_path, 'rb') as photo:
            bot.send_photo(TARGET_CHANNEL, photo, caption=prediction_text, reply_markup=markup, parse_mode="Markdown")
        bot.reply_to(message, "✅ Prediction successfully sent to channel!")
    except Exception as err:
        bot.reply_to(message, f"❌ Send Error: {err}")

# --- DIRECT ADMIN BROADCAST (Without /broadcast command for Admin) ---
@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_USER_ID and message.text not in ["Get Prediction", "📢 Official Channel", "🔗 Register Link"])
def direct_admin_broadcast(message):
    try:
        if message.text:
            bot.send_message(TARGET_CHANNEL, message.text, parse_mode="Markdown")
            bot.reply_to(message, "✅ Sent to channel!")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

@bot.message_handler(content_types=['photo'], func=lambda message: message.from_user.id == ADMIN_USER_ID)
def direct_admin_photo_broadcast(message):
    try:
        photo_id = message.photo[-1].file_id
        caption = message.caption if message.caption else ""
        bot.send_photo(TARGET_CHANNEL, photo_id, caption=caption, parse_mode="Markdown")
        bot.reply_to(message, "✅ Photo sent to channel!")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

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

def fetch_wingo_data():
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        url = f"https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json?t={int(time.time()*1000)}"
        res = requests.get(url, headers=headers, timeout=8)
        if res.status_code == 200:
            data = res.json()
            if 'data' in data and 'list' in data['data']:
                return data['data']['list']
    except Exception as e:
        print(f"API Error: {e}")
    return None

if __name__ == "__main__":
    bot.infinity_polling()
