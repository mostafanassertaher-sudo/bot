import os
import time
import telebot
from telebot import types
from yt_dlp import YoutubeDL

# --- حط التوكن بتاعك هنا ---
API_TOKEN = '8514462418:AAGo0dc4ZkaphwvyL8JaoFbOEhX9Ho6ksok'
bot = telebot.TeleBot(API_TOKEN)

user_data = {}

# دالة لتحديث شريط التحميل
def progress_hook(d, message, last_update_time):
    if d['status'] == 'downloading':
        p = d.get('_percent_str', '0%')
        s = d.get('_speed_str', 'N/A')
        e = d.get('_eta_str', 'N/A')
        current_time = time.time()
        if current_time - last_update_time[0] > 3:
            try:
                bot.edit_message_text(
                    f"جاري التحميل يا فنان... ⏳\n\nالنسبة: {p}\nالسرعة: {s}\nالوقت المتبقي: {e}",
                    message.chat.id, message.message_id
                )
                last_update_time[0] = current_time
            except: pass

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً يا درش! ابعت اللينك والبوت جاهز بالكوكيز الجديدة `M.youtube.com_cookies.txt` 🎬")

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    url = message.text
    if "http" not in url: return
    msg = bot.reply_to(message, "جاري فحص الرابط... 🔍")
    try:
        ydl_opts_info = {
            'quiet': True,
            'no_warnings': True,
            'cookiefile': 'M.youtube.com_cookies.txt', # تم التعديل للاسم الجديد
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        with YoutubeDL(ydl_opts_info) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Video')
            duration = info.get('duration_string', 'N/A')
        user_data[message.chat.id] = {'url': url, 'title': title}
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton("720p", callback_data="720"),
                   types.InlineKeyboardButton("1080p", callback_data="1080"),
                   types.InlineKeyboardButton("صوت MP3 🎵", callback_data="mp3"))
        bot.edit_message_text(f"✅ تم العثور على: {title}\n⏱️ المدة: {duration}\n\nاختار عايز تحمل إيه:", 
                             message.chat.id, msg.message_id, reply_markup=markup)
    except Exception as e:
        bot.edit_message_text(f"خطأ: {str(e)}", message.chat.id, msg.message_id)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if chat_id not in user_data: return
    url = user_data[chat_id]['url']
    choice = call.data
    status_msg = bot.send_message(chat_id, "بدأت المهمة... 🚀")
    last_update = [time.time()]

    ydl_opts = {
        'outtmpl': f'video_{chat_id}.%(ext)s',
        'progress_hooks': [lambda d: progress_hook(d, status_msg, last_update)],
        'max_filesize': 48000000,
        'noplaylist': True,
        'cookiefile': 'M.youtube.com_cookies.txt', # تم التعديل هنا برضه
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    if choice == "mp3":
        ydl_opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]})
    elif choice == "720":
        ydl_opts.update({'format': 'best[height<=720]'})
    else:
        ydl_opts.update({'format': 'best[height<=1080]'})

    try:
        with YoutubeDL(ydl_opts) as ydl:
            file_info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(file_info)
            if choice == "mp3": filename = filename.rsplit('.', 1)[0] + ".mp3"

        with open(filename, 'rb') as f:
            if choice == "mp3": bot.send_audio(chat_id, f, caption=user_data[chat_id]['title'])
            else: bot.send_video(chat_id, f, caption=user_data[chat_id]['title'])
        
        if os.path.exists(filename): os.remove(filename)
        bot.delete_message(chat_id, status_msg.message_id)
    except Exception as e:
        bot.send_message(chat_id, f"مشكلة أثناء التحميل: {str(e)}")

bot.infinity_polling()
