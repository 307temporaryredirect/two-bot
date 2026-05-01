import os
import telebot
from telebot import types
from flask import Flask
import threading
from datetime import datetime

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    print("BOT_TOKEN tidak ada")
    exit()

CHANNEL_ID = -1002445709942

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running 🚀"

pending_users = set()
user_fess_count = {}
user_last_message = {}
total_fess_sent = 0

banned_words = ['anjing', 'bangsat', 'kontol', 'tolol']

def contains_bad_words(text):
    return any(word in text.lower() for word in banned_words)

def can_send(user_id):
    today = datetime.now().date()
    if user_id not in user_fess_count:
        user_fess_count[user_id] = [(today, 1)]
        return True
    date_list = user_fess_count[user_id]
    if date_list[-1][0] != today:
        user_fess_count[user_id] = [(today, 1)]
        return True
    elif date_list[-1][1] < 5:
        user_fess_count[user_id][-1] = (today, date_list[-1][1] + 1)
        return True
    else:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    btn_send = types.InlineKeyboardButton("Kirim Menfess", callback_data="send_fess")
    btn_stat = types.InlineKeyboardButton("Lihat Statistik", callback_data="show_stats")
    btn_unsend = types.InlineKeyboardButton("Hapus Fess Terakhir", callback_data="unsend_fess")
    markup.add(btn_send)
    markup.add(btn_stat, btn_unsend)
    bot.send_message(message.chat.id, "Hai! Pilih menu di bawah ini:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_menu(call):
    user_id = call.from_user.id
    if call.data == "send_fess":
        if not can_send(user_id):
            bot.send_message(user_id, "Hey cornerpeeps! Kamu sudah mencapai batas 5 menfess hari ini. Coba lagi besok ya!")
            return
        pending_users.add(user_id)
        bot.send_message(user_id, "Cornerpeeps! Kamu bisa langsung ketik isi menfess yang mau kamu kirim sekarang tanpa trigger apapun (bisa teks aja atau gambar dengan teks) lalu kirim.")
    elif call.data == "show_stats":
        bot.send_message(user_id, f"Total menfess terkirim: {total_fess_sent}")
    elif call.data == "unsend_fess":
        if user_id in user_last_message:
            try:
                bot.delete_message(CHANNEL_ID, user_last_message[user_id])
                bot.send_message(user_id, "Fess terakhir kamu berhasil dihapus dari channel.")
                del user_last_message[user_id]
            except Exception:
                bot.send_message(user_id, "Gagal hapus Fess. Mungkin sudah terlalu lama atau tidak ditemukan.")
        else:
            bot.send_message(user_id, "Kamu belum mengirim fess atau sudah dihapus.")
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: True, content_types=['text', 'photo'])
def handle_fess(message):
    global total_fess_sent
    user_id = message.from_user.id

    if user_id not in pending_users:
        bot.reply_to(message, "Klik /start dan tekan 'Kirim Menfess' dulu untuk mulai.")
        return

    try:
        msg_sent = None
        username = message.from_user.username or f"id:{user_id}"

        if message.content_type == 'text':
            text = message.text.strip()
            if len(text) > 4000:
                bot.reply_to(message, "Pesan terlalu panjang! Maksimal 4000 karakter.")
                return
            if contains_bad_words(text):
                bot.reply_to(message, "Pesan kamu mengandung kata yang tidak diperbolehkan.")
                return
            msg_sent = bot.send_message(CHANNEL_ID, "💚 " + text)

        elif message.content_type == 'photo':
            file_id = message.photo[-1].file_id
            caption = message.caption.strip() if message.caption else ""
            if len(caption) > 1024:
                bot.reply_to(message, "Caption terlalu panjang! Maksimal 1024 karakter.")
                return
            if contains_bad_words(caption):
                bot.reply_to(message, "Caption kamu mengandung kata yang tidak diperbolehkan.")
                return
            msg_sent = bot.send_photo(CHANNEL_ID, file_id, caption="💚 " + caption)

        if msg_sent:
            total_fess_sent += 1
            user_last_message[user_id] = msg_sent.message_id
            link = f"https://t.me/c/{str(CHANNEL_ID)[4:]}/{msg_sent.message_id}"
            bot.send_message(user_id, f"Fess kamu sudah terkirim!\n\n[Lihat Fess]({link})", parse_mode="Markdown")
            with open("log.txt", "a") as f:
                log = message.text if message.content_type == 'text' else caption
                f.write(f"{username} ({user_id}): {log}\n")

    except Exception as e:
        bot.reply_to(message, f"Gagal kirim fess. Error: {e}")

    pending_users.discard(user_id)

def run_web():
    print("WEB START")
    app.run(host="0.0.0.0", port=8080)

def run_bot():
    print("BOT START")
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    run_bot()
