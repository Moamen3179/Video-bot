import telebot
from telebot import types
import yt_dlp
import os
from threading import Thread
from flask import Flask

TOKEN = 8796579115:AAGgi4CfKPBhdAVvrTvyyXrh8Wq16Sf8w1w
CHANNEL = "@el_shaier"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

def get_channel_url():
    try:
        chat = bot.get_chat(CHANNEL)
        if chat.username:
            return "https://" + "t.me/" + chat.username
    except:
        pass
    return "https://" + "t.me/" + CHANNEL.replace("@", "")

def check_sub(user_id):
    try:
        status = bot.get_chat_member(CHANNEL, user_id).status
        if status in ['member', 'administrator', 'creator']:
            return True
    except:
        pass
    return False

def sub_msg(chat_id):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("اشترك في القناة أولاً 📢", url=get_channel_url())
    check_btn = types.InlineKeyboardButton("تم الاشتراك ✅", callback_data="check")
    markup.add(btn)
    markup.add(check_btn)
    bot.send_message(chat_id, "⚠️ عذراً عزيزي، يجب الاشتراك في قناة البوت أولاً لتتمكن من تحميل الفيديوهات مجاناً:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check")
def check_callback(call):
    if check_sub(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "✅ تم التحقق من اشتراكك بنجاح!\n\n📥 أرسل الآن رابط الفيديو (تيك توك، إنستجرام، فيسبوك، يوتيوب شورتس) لتحميله فوراً:")
    else:
        bot.answer_callback_query(call.id, "❌ لم تشترك في القناة بعد! اشترك أولاً ثم اضغط هنا.", show_alert=True)

@bot.message_handler(commands=['start'])
def start_cmd(message):
    if not check_sub(message.from_user.id):
        sub_msg(message.chat.id)
        return
    bot.send_message(message.chat.id, "أهلاً بك في بوت تحميل الفيديوهات السريع! 🎬⚡\n\n📥 أرسل رابط أي فيديو الآن وسأقوم بتحميله لك بأعلى جودة وبدون علامة مائية:")

@bot.message_handler(func=lambda message: True)
def download_video(message):
    if not check_sub(message.from_user.id):
        sub_msg(message.chat.id)
        return

    url = message.text.strip()
    if not url.startswith("http"):
        bot.send_message(message.chat.id, "⚠️ من فضلك أرسل رابط فيديو صحيح يبدأ بـ http أو https")
        return

    wait_msg = bot.send_message(message.chat.id, "⏳ جاري سحب الفيديو بأعلى جودة، انتظر ثواني...")
    filename = f"video_{message.chat.id}_{message.message_id}.mp4"

    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': filename,
        'max_filesize': 48 * 1024 * 1024,
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if os.path.exists(filename):
            with open(filename, 'rb') as video:
                bot.send_video(message.chat.id, video, caption="✅ تم التحميل بنجاح!\n📢 تابعنا للمزيد: @el_shaier")
            os.remove(filename)
            bot.delete_message(message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text("❌ عذراً، حجم الفيديو كبير جداً (أكبر من 50 ميجا) أو الرابط غير مدعوم.", message.chat.id, wait_msg.message_id)
    except Exception as e:
        if os.path.exists(filename):
            os.remove(filename)
        bot.edit_message_text("❌ تعذر تحميل الفيديو! تأكد أن الحساب عام وليس خاصاً، أو جرب رابطاً آخر.", message.chat.id, wait_msg.message_id)

if __name__ == "__main__":
    Thread(target=run_web).start()
    bot.infinity_polling()
