import os
import time
import telebot
from telebot import types
from yt_dlp import YoutubeDL

# --- حط التوكن بتاعك هنا ---
API_TOKEN = '8514462418:AAGo0dc4ZkaphwvyL8JaoFbOEhX9Ho6ksok'
bot = telebot.TeleBot(API_TOKEN)

# اسم الملف بالظبط كما في الصورة (lowercase m)
COOKIE_FILE = 'm.youtube.com_cookies.txt'

user_data = {}

def progress_hook(d, message, last_update_time):
    if d['status'] == 'downloading':
        p = d.get('_percent_str', '0%')
        s = d.get('_speed_str', 'N/A')
        current_time = time.time()
        if current_time - last_update_time[0] > 3:
            try:
                bot.edit_message_text(f"جاري التحميل... ⏳\nالنسبة: {p}\nالسرعة: {s}", message.chat.id, message.message_id)
                last_update_time[0] = current_time
            except: pass

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # فحص لو الملف موجود فعلياً في السيرفر
    if os.path.exists(COOKIE_FILE):
        status = "✅ ملف الكوكيز جاهز"
    else:
        status = "❌ ملف الكوكيز مش موجود جنبه"
    bot.reply_to(message, f"أهلاً يا درش! {status}\nابعت اللينك دلوقتي.")

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    url = message.text
    if "http" not in url: return
    msg = bot.reply_to(message, "جاري الفحص... 🔍")
    try:
        ydl_opts = {
            'cookiefile': COOKIE_FILE if os.path.exists(COOKIE_FILE) else None,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'format': 'best[height<=720]', # جودة 720 عشان الحجم
            'outtmpl': f'video_{message.chat.id}.%(ext)s',
            'progress_hooks': [lambda d: progress_hook(d, msg, [time.time()])],
            'max_filesize': 48000000,
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            with open(filename, 'rb') as f:
                bot.send_video(message.chat.id, f, caption=info.get('title'))
            os.remove(filename)
            bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"خطأ: {str(e)}", message.chat.id, msg.message_id)

bot.infinity_polling()
