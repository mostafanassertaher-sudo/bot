import os
import telebot
from yt_dlp import YoutubeDL
from flask import Flask
from threading import Thread

# --- الجزء الخاص بالسيرفر الوهمي عشان Render ---
app = Flask('')
@app.route('/')
def home():
    return "البوت شغال بنجاح!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
# -------------------------------------------

API_TOKEN = '8249071787:AAF2pvdmzYZmbujiGtJXDU4ncjjdZbUxWms' # حط التوكن بتاعك هنا
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك يا مصطفى! ابعتلي لينك الفيديو وهنزلهولك فوراً.")

@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text
    if "http" not in url:
        return
        
    bot.reply_to(message, "جاري التحميل... انتظر ثواني ⏳")
    
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'video.mp4',
            'max_filesize': 45000000,
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        with open('video.mp4', 'rb') as video:
            bot.send_video(message.chat.id, video)
        
        os.remove('video.mp4')
        
    except Exception as e:
        bot.reply_to(message, f"حصلت مشكلة: {str(e)}")

if __name__ == "__main__":
    keep_alive() # تشغيل السيرفر الوهمي
    bot.polling(none_stop=True)
