import os
import telebot
from telebot import types
from yt_dlp import YoutubeDL

# --- حط التوكن بتاعك هنا ---
API_TOKEN = '8514462418:AAGo0dc4ZkaphwvyL8JaoFbOEhX9Ho6ksok'
bot = telebot.TeleBot(API_TOKEN)

# اسم الملف كما في الصورة (lowercase m)
COOKIE_FILE = 'm.youtube.com_cookies.txt'

# مخزن مؤقت للروابط
user_data = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً يا درش! ابعت اللينك واختار الجودة وهنزلك الفيديو فوراً 🎬")

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    url = message.text
    if "http" not in url: return
    
    # حفظ الرابط في الذاكرة
    user_data[message.chat.id] = url
    
    # أزرار اختيار الجودة
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("720p", callback_data="720")
    btn2 = types.InlineKeyboardButton("1080p", callback_data="1080")
    markup.add(btn1, btn2)
    
    bot.reply_to(message, "اختار الجودة المطلوبة:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if chat_id not in user_data: return
    
    url = user_data[chat_id]
    quality = call.data
    
    bot.delete_message(chat_id, call.message.message_id)
    status_msg = bot.send_message(chat_id, "جاري التحميل... 🚀")
    
    # إعدادات التحميل مع ميزة المشاهدة الفورية (FastStart)
    ydl_opts = {
        'cookiefile': COOKIE_FILE if os.path.exists(COOKIE_FILE) else None,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        
        # اختيار الجودة وإجبار صيغة MP4 للمشاهدة الفورية
        'format': f'best[ext=mp4][height<={quality}]/best[height<={quality}]',
        'outtmpl': f'video_{chat_id}.mp4',
        
        # ميزة المشاهدة الفورية (نقل الفهرس لأول الفيديو)
        'postprocessor_args': ['-movflags', '+faststart'],
        
        'max_filesize': 48000000, # 48 ميجا ليميت تليجرام
        'noplaylist': True,
        'quiet': True
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = f"video_{chat_id}.mp4"

        with open(filename, 'rb') as f:
            bot.send_video(chat_id, f, supports_streaming=True) # تفعيل المشاهدة الفورية
        
        if os.path.exists(filename):
            os.remove(filename)
        bot.delete_message(chat_id, status_msg.message_id)
        
    except Exception as e:
        bot.send_message(chat_id, f"حصلت مشكلة: {str(e)}")

bot.infinity_polling()
