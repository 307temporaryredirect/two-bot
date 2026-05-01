import os
import telebot
from flask import Flask
import threading

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("BOT_TOKEN tidak ada")
    exit()

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running 🚀"

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Bot sudah hidup!")

def run_web():
    print("WEB START")
    app.run(host="0.0.0.0", port=8080)

def run_bot():
    print("BOT START")
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    run_bot()
