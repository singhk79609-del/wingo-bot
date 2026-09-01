import os
import random
import threading
from datetime import datetime
import pytz
import telebot
from telebot import types
from flask import Flask

# 1. Environment Variable se Token read karna
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# 2. Flask Web Server (Render 24/7 Hosting ke liye)
app = Flask(__name__)

@app.route('/')
def home():
    return "Wingo 24/7 Prediction Bot is Live!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# 3. Helper Functions: Current IST Period & Prediction Algorithm
def get_current_period():
    """
    1-Minute Wingo Period Number Generator (IST Standard)
    Format: YYYYMMDD10001XXXX (Total minutes elapsed in day)
    """
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    date_str = now.strftime('%Y%m%d')
    total_minutes = (now.hour * 60) + now.minute + 1
    period_no = f"{date_str}10001{total_minutes:04d}"
    return period_no

def generate_prediction(period_str):
    """
    Prediction Algorithm: Period Number Hash ke aadhar par fixed result
    Sabhi users ko Har Period me SAME result milega (Zero confusion)
    """
    # Period number ke last 4 digits se seed hashing
    seed_value = int(period_str[-4:])
    random.seed(seed_value)
    
    result_type = random.choice(["BIG 🟢", "SMALL 🔴"])
    number = random.randint(0, 9)
    color = "GREEN 💚" if number in [1, 3, 7, 9] else ("RED 🔴" if number in [2, 4, 6, 8] else "VIOLET 💜")
    
    # Random seed reset
    random.seed()
    
    return result_type, number, color

# 4. Main Menu Markup (Telegram Mini Keyboard)
def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_predict = types.KeyboardButton("🎯 Get Prediction")
    btn_period = types.KeyboardButton("⏰ Current Period")
    btn_help = types.KeyboardButton("❓ Help / Info")
    markup.add(btn_predict, btn_period, btn_help)
    return markup

# 5. Bot Handlers
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_msg = (
        "<b>🎰 Welcome to Wingo 1-Min Prediction Bot!</b>\n\n"
        "Niche diye gaye <b>Mini Keyboard Buttons</b> ka use karke instant prediction aur period number dekhein."
    )
    bot.reply_to(message, welcome_msg, parse_mode="HTML", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda message: message.text == "🎯 Get Prediction")
def handle_prediction(message):
    period = get_current_period()
    result, num, color = generate_prediction(period)
    
    response = (
        f"<b>⚡ WINGO 1-MIN PREDICTION ⚡</b>\n\n"
        f"<b>📌 Period No:</b> <code>{period}</code>\n"
        f"<b>🎯 Result:</b> <b>{result}</b>\n"
        f"<b>🔢 Number:</b> <code>{num}</code>\n"
        f"<b>🎨 Color:</b> {color}\n\n"
        f"<i>⚠️ Note: Next minute start hone se pehle bet lagayein!</i>"
    )
    bot.reply_to(message, response, parse_mode="HTML", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda message: message.text == "⏰ Current Period")
def handle_period(message):
    period = get_current_period()
    response = f"<b>⏰ Current Wingo Period Number:</b>\n<code>{period}</code>"
    bot.reply_to(message, response, parse_mode="HTML", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda message: message.text == "❓ Help / Info")
def handle_info(message):
    info_text = (
        "<b>ℹ️ Bot Information:</b>\n\n"
        "• <b>24/7 Active:</b> Render Server Hosted\n"
        "• <b>Algorithm:</b> Deterministic Hash (Sabhi users ko ek period par same prediction milega)\n"
        "• <b>Timezone:</b> IST (Indian Standard Time)"
    )
    bot.reply_to(message, info_text, parse_mode="HTML", reply_markup=get_main_keyboard())

# 6. Server Execution
if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.start()
    bot.infinity_polling()
