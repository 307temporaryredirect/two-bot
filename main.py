import os
import telebot
from telebot import types
from flask import Flask
import threading
from datetime import datetime, timedelta
import random
import re
import time

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "-1002445709942"))
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

if not TOKEN:
    print("BOT_TOKEN tidak ada")
    exit()

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route("/")
def home():
    return "Muncorner Bot is running 💚"

# ─── DATA STORE ───────────────────────────────────────────
user_lang = {}
user_fess_count = {}
user_last_messages = {}
user_total_fess = {}
user_first_seen = {}
user_notif = {}
user_clover = {}
user_streak = {}
user_last_checkin = {}
user_peak_rank = {}
user_peak_rank_date = {}
user_peak_badge = {}
user_peak_badge_date = {}
user_prefix = {}
user_hide_badge = {}
ever_registered = set()
pending_users = set()
preview_data = {}
scheduled_fess = []
edit_pending = {}
broadcast_sent = {}
valid_gift_ids = set()
total_fess_sent = 0

# ─── GIFT ─────────────────────────────────────────────────
GIFT_PRICES = {
    "birthday": {"emoji": "🎂", "name": "Birthday Surprise", "price": 30},
    "appreciation": {"emoji": "💌", "name": "Appreciation", "price": 25},
}

def make_gift_template(gift_key, to, msg):
    if gift_key == "birthday":
        return (
            f"🎂 A BIRTHDAY SURPRISE\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"Dear @{to},\n\n"
            f"❝ {msg} ❞\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"[ 🍀 A GIFT FROM SOMEONE IN THE CORNER ]"
        )
    elif gift_key == "appreciation":
        return (
            f"💌 A LITTLE APPRECIATION\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"Dear @{to},\n\n"
            f"❝ {msg} ❞\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"[ 🍀 A GIFT FROM SOMEONE IN THE CORNER ]"
        )

# ─── TEXTS ────────────────────────────────────────────────
TEXTS = {
    "id": {
        "welcome": "Halo! Selamat datang di *Muncorner Bot* 💚\n\nPilih bahasa kamu:\n_Choose your language:_",
        "welcome_bonus": "\n\n🍀 *+10 Clover* sebagai welcome bonus!",
        "menu": "Hai, *{name}*! 👋\n\nApa yang mau kamu lakukan hari ini?",
        "send_guide": "📝 *Panduan Kirim Menfess*\n\nKamu bisa langsung ketik isi menfess yang mau kamu kirim sekarang tanpa trigger apapun (bisa teks aja atau gambar dengan teks), lalu kirim.\n\n_Maks. 4000 karakter · 5 menfess/hari_",
        "preview": "👀 *Preview Menfess Kamu:*\n\n{badge}💚 {text}\n\n_Sudah yakin? Menfess akan dikirim ke channel._",
        "sent": "✅ Menfess kamu berhasil terkirim! +2 🍀\n\n[Lihat Menfess]({link})",
        "quota": "❌ Kamu sudah mencapai batas *5 menfess* hari ini. Coba lagi besok ya!",
        "too_long": "❌ Pesan terlalu panjang! Maksimal 4000 karakter.",
        "bad_word": "❌ Pesan mengandung kata yang tidak diperbolehkan.",
        "cancelled": "❌ Dibatalkan.",
        "pick_delete": "🗑 Pilih menfess yang mau dihapus:",
        "no_fess": "Kamu belum pernah kirim menfess.",
        "confirm_delete": "⚠️ Yakin hapus *Fess #{num}*?\n\n_{preview}_\n\nPesan akan dihapus dari channel.",
        "deleted": "✅ Fess berhasil dihapus dari channel.",
        "delete_fail": "❌ Gagal hapus. Mungkin sudah terlalu lama.",
        "stats_title": "📊 *Statistik Muncorner*",
        "stats_total": "📨 Total Menfess",
        "stats_senders": "👥 Total Pengirim",
        "rank_label": "🏆 Posisi Kamu Di Leaderboard",
        "you_label": "KAMU",
        "you_pronoun": "kamu",
        "leaderboard_empty": "_Kamu belum ada di leaderboard. Kirim menfess dulu!_",
        "profile_title": "👤 *Profil Saya*",
        "profile_username": "👤 Username",
        "profile_id": "🆔 ID",
        "profile_joined": "📅 Bergabung",
        "profile_total": "📨 Total Menfess",
        "profile_quota": "⏳ Kuota Hari Ini",
        "profile_ranking": "🏆 Ranking Sekarang",
        "profile_peak_rank": "📈 Rank Tertinggi",
        "profile_badge": "🎖 Badge Sekarang",
        "profile_peak_badge": "👑 Badge Tertinggi",
        "profile_clover": "🍀 Clover",
        "settings_title": "⚙️ *Pengaturan*",
        "notif_active": "✅ Aktif",
        "notif_inactive": "🔕 Nonaktif",
        "delete_account": "⚠️ Yakin hapus semua data akun kamu?",
        "account_deleted_msg": "✅ Data akun berhasil dihapus.",
        "send_error": "❌ Gagal kirim. Error: {e}",
        "btn_send": "💚 Kirim Menfess",
        "btn_stats": "📊 Statistik",
        "btn_delete": "🗑 Hapus Menfess",
        "btn_profile": "👤 Profil Saya",
        "btn_settings": "⚙️ Pengaturan",
        "btn_badge_benefit": "🎖 Badge Benefit",
        "btn_gift": "🎁 Kirim Hadiah",
        "btn_checkin": "🌿 Check-in Harian",
        "btn_back": "« Kembali ke Menu",
        "btn_send_confirm": "✅ Kirim",
        "btn_cancel": "✖ Batal",
        "btn_yes_delete": "🗑 Ya, Hapus",
        "btn_yes_del_account": "🗑 Ya, Hapus",
        "btn_lang": "🌐 Bahasa",
        "btn_notif": "🔔 Notifikasi",
        "btn_del_account": "🗑 Hapus Data Akun",
        "no_username": "tidak ada username",
        "checkin_done": "🌿 Check-in Berhasil! +1 🍀\n\nStreak kamu: *{streak} hari*",
        "checkin_already": "✅ Kamu sudah check-in hari ini!",
        "checkin_streak": "🎉 Streak 7 Hari! Bonus +5 🍀",
        "not_enough_clover": "❌ Clover kamu tidak cukup! Butuh *{need}* 🍀, kamu punya *{have}* 🍀",
        "gift_sent": "✅ Hadiah berhasil dikirim ke channel! -{price} 🍀",
        "gift_notif": "🎁 Kamu dapat hadiah di Muncorner!\n\n[Lihat Hadiah]({link})",
        "gift_preview": "👀 *Preview Hadiah:*\n\n{preview}\n\nKirim ke channel?",
        "schedule_set": "⏰ Menfess dijadwalkan untuk *{time}* WIB! +3 🍀 saat terkirim",
        "schedule_format": "❌ Format waktu salah! Gunakan format: *HH:MM*\nContoh: *23:00*",
        "edit_select": "✏️ Pilih menfess yang mau diedit:",
        "edit_type": "✏️ Ketik pesan baru untuk mengganti menfess ini:",
        "edit_done": "✅ Menfess berhasil diedit!",
        "edit_fail": "❌ Gagal edit. Mungkin waktu edit sudah habis.",
        "edit_expired": "❌ Waktu edit sudah habis!",
        "poll_question": "📊 Ketik pertanyaan polling kamu:",
        "poll_options": "📊 Ketik opsi-opsi polling, pisahkan dengan enter.\n\nMinimal 2, maksimal 10 opsi.",
        "poll_sent": "✅ Polling berhasil dikirim! +1 🍀",
        "hide_badge_on": "👻 Badge Disembunyikan",
        "hide_badge_off": "✅ Badge Ditampilkan Kembali",
        "prefix_select": "🎨 Pilih Prefix Heart Kamu:",
        "invisible_guide": "🖊 Ketik pesan invisible ink kamu:\n\n_Pesan akan tersembunyi di channel, harus di-tap untuk dibaca._",
        "no_edit_benefit": "❌ Badge kamu belum bisa edit menfess.",
        "first_fess_bonus": "\n🌟 Bonus Menfess Pertama Hari Ini! +1 🍀",
    },
    "en": {
        "welcome": "Hello! Welcome to *Muncorner Bot* 💚\n\nChoose your language:\n_Pilih bahasa kamu:_",
        "welcome_bonus": "\n\n🍀 *+10 Clover* as a welcome bonus!",
        "menu": "Hey, *{name}*! 👋\n\nWhat would you like to do today?",
        "send_guide": "📝 *How to Send a Menfess*\n\nYou can now directly type the message you want to send without any trigger (it can be just text or an image with text), then send it.\n\n_Max. 4000 characters · 5 menfess/day_",
        "preview": "👀 *Preview Your Menfess:*\n\n{badge}💚 {text}\n\n_Are you sure? Your menfess will be sent to the channel._",
        "sent": "✅ Your menfess has been sent! +2 🍀\n\n[View Menfess]({link})",
        "quota": "❌ You've reached the *5 menfess* limit for today. Try again tomorrow!",
        "too_long": "❌ Message too long! Maximum 4000 characters.",
        "bad_word": "❌ Message contains prohibited words.",
        "cancelled": "❌ Cancelled.",
        "pick_delete": "🗑 Choose a menfess to delete:",
        "no_fess": "You haven't sent any menfess yet.",
        "confirm_delete": "⚠️ Delete *Fess #{num}*?\n\n_{preview}_\n\nThis will be removed from the channel.",
        "deleted": "✅ Menfess successfully deleted from channel.",
        "delete_fail": "❌ Failed to delete. It may have been too long ago.",
        "stats_title": "📊 *Muncorner Statistics*",
        "stats_total": "📨 Total Menfess",
        "stats_senders": "👥 Total Senders",
        "rank_label": "🏆 Your Leaderboard Position",
        "you_label": "YOU",
        "you_pronoun": "you",
        "leaderboard_empty": "_You're not on the leaderboard yet. Send a menfess first!_",
        "profile_title": "👤 *My Profile*",
        "profile_username": "👤 Username",
        "profile_id": "🆔 ID",
        "profile_joined": "📅 Joined",
        "profile_total": "📨 Total Menfess",
        "profile_quota": "⏳ Today's Quota",
        "profile_ranking": "🏆 Current Ranking",
        "profile_peak_rank": "📈 Peak Rank",
        "profile_badge": "🎖 Current Badge",
        "profile_peak_badge": "👑 Highest Badge",
        "profile_clover": "🍀 Clover",
        "settings_title": "⚙️ *Settings*",
        "notif_active": "✅ Active",
        "notif_inactive": "🔕 Inactive",
        "delete_account": "⚠️ Are you sure you want to delete all your account data?",
        "account_deleted_msg": "✅ Account data successfully deleted.",
        "send_error": "❌ Failed to send. Error: {e}",
        "btn_send": "💚 Send Menfess",
        "btn_stats": "📊 Statistics",
        "btn_delete": "🗑 Delete Menfess",
        "btn_profile": "👤 My Profile",
        "btn_settings": "⚙️ Settings",
        "btn_badge_benefit": "🎖 Badge Benefit",
        "btn_gift": "🎁 Send Gift",
        "btn_checkin": "🌿 Daily Check-in",
        "btn_back": "« Back to Menu",
        "btn_send_confirm": "✅ Send",
        "btn_cancel": "✖ Cancel",
        "btn_yes_delete": "🗑 Yes, Delete",
        "btn_yes_del_account": "🗑 Yes, Delete",
        "btn_lang": "🌐 Language",
        "btn_notif": "🔔 Notification",
        "btn_del_account": "🗑 Delete Account Data",
        "no_username": "no username",
        "checkin_done": "🌿 Check-in Successful! +1 🍀\n\nYour streak: *{streak} days*",
        "checkin_already": "✅ You've already checked in today!",
        "checkin_streak": "🎉 7-Day Streak! Bonus +5 🍀",
        "not_enough_clover": "❌ Not enough Clover! Need *{need}* 🍀, you have *{have}* 🍀",
        "gift_sent": "✅ Gift sent to channel! -{price} 🍀",
        "gift_notif": "🎁 You received a gift on Muncorner!\n\n[View Gift]({link})",
        "gift_preview": "👀 *Gift Preview:*\n\n{preview}\n\nSend to channel?",
        "schedule_set": "⏰ Menfess scheduled for *{time}* WIB! +3 🍀 when sent",
        "schedule_format": "❌ Wrong time format! Use: *HH:MM*\nExample: *23:00*",
        "edit_select": "✏️ Choose a menfess to edit:",
        "edit_type": "✏️ Type your new message:",
        "edit_done": "✅ Menfess successfully edited!",
        "edit_fail": "❌ Failed to edit. Edit time may have expired.",
        "edit_expired": "❌ Edit time has expired!",
        "poll_question": "📊 Type your poll question:",
        "poll_options": "📊 Type poll options, separated by enter.\n\nMinimum 2, maximum 10 options.",
        "poll_sent": "✅ Poll sent! +1 🍀",
        "hide_badge_on": "👻 Badge Hidden",
        "hide_badge_off": "✅ Badge Visible Again",
        "prefix_select": "🎨 Choose Your Heart Prefix:",
        "invisible_guide": "🖊 Type your invisible ink message:\n\n_Message will be hidden in channel, must be tapped to read._",
        "no_edit_benefit": "❌ Your badge cannot edit menfess yet.",
        "first_fess_bonus": "\n🌟 First Menfess Bonus Today! +1 🍀",
    }
}

def t(user_id, key):
    lang = user_lang.get(user_id, "id")
    return TEXTS[lang].get(key, key)

# ─── BADGE ────────────────────────────────────────────────
def get_badge_emoji(user_id):
    rank = get_rank(user_id)
    if rank is None: return "🐣"
    if rank <= 2: return "👑"
    if rank <= 5: return "🔥"
    if rank <= 20: return "⭐"
    if rank <= 50: return "💫"
    return "🐣"

def get_badge_label(user_id):
    rank = get_rank(user_id)
    if rank is None: return "🐣 Newbie"
    if rank <= 2: return "👑 Legend"
    if rank <= 5: return "🔥 Top Sender"
    if rank <= 20: return "⭐ Active"
    if rank <= 50: return "💫 Regular"
    return "🐣 Newbie"

def get_badge_level(user_id):
    rank = get_rank(user_id)
    if rank is None: return 0
    if rank <= 2: return 4
    if rank <= 5: return 3
    if rank <= 20: return 2
    if rank <= 50: return 1
    return 0

def get_edit_minutes(user_id):
    level = get_badge_level(user_id)
    if level == 4: return 30
    if level == 3: return 15
    if level == 2: return 10
    if level == 1: return 5
    return 0

def update_peak(user_id):
    rank = get_rank(user_id)
    badge_level = get_badge_level(user_id)
    today = datetime.now().strftime("%d %b %Y")
    if rank:
        current_peak = user_peak_rank.get(user_id)
        if current_peak is None or rank < current_peak:
            user_peak_rank[user_id] = rank
            user_peak_rank_date[user_id] = today
    current_peak_badge = user_peak_badge.get(user_id, 0)
    if badge_level > current_peak_badge:
        user_peak_badge[user_id] = badge_level
        user_peak_badge_date[user_id] = today

def get_prefix(user_id):
    hide = user_hide_badge.get(user_id, False)
    level = get_badge_level(user_id)
    if hide:
        if level == 4:
            return user_prefix.get(user_id, "💚") + " "
        return "💚 "
    badge = get_badge_emoji(user_id)
    if level == 4:
        prefix = user_prefix.get(user_id, "💚")
        return f"{badge}{prefix} "
    return f"{badge}💚 "

def strip_leading_emoji(text):
    emoji_pattern = re.compile(
        "^[\U0001F000-\U0001FFFF\U00002600-\U000027BF\U0000FE00-\U0000FE0F"
        "\U00002702-\U000027B0\u2600-\u27BF\s]*",
        re.UNICODE
    )
    return emoji_pattern.sub("", text).strip()

# ─── CLOVER ───────────────────────────────────────────────
def add_clover(user_id, amount):
    user_clover[user_id] = user_clover.get(user_id, 0) + amount

def use_clover(user_id, amount):
    current = user_clover.get(user_id, 0)
    if current < amount:
        return False
    user_clover[user_id] = current - amount
    return True

# ─── LEADERBOARD ──────────────────────────────────────────
def get_leaderboard():
    return sorted(user_total_fess.items(), key=lambda x: x[1], reverse=True)

def get_rank(user_id):
    for i, (uid, _) in enumerate(get_leaderboard()):
        if uid == user_id:
            return i + 1
    return None

def sensor_username(pos):
    fake = f"user{pos}mc"
    chars = list(fake)
    n = len(chars)
    visible = set(random.sample(range(n), max(1, n // 3)))
    return "".join(c if i in visible else "*" for i, c in enumerate(chars))

# ─── QUOTA ────────────────────────────────────────────────
def can_send(user_id):
    today = datetime.now().date()
    if user_id not in user_fess_count:
        user_fess_count[user_id] = (today, 0)
    date, count = user_fess_count[user_id]
    if date != today:
        user_fess_count[user_id] = (today, 0)
        count = 0
    if count < 5:
        user_fess_count[user_id] = (today, count + 1)
        return True
    return False

def quota_left(user_id):
    today = datetime.now().date()
    if user_id not in user_fess_count:
        return 5
    date, count = user_fess_count[user_id]
    if date != today:
        return 5
    return max(0, 5 - count)

def is_first_fess_today(user_id):
    today = datetime.now().date()
    if user_id not in user_fess_count:
        return True
    date, count = user_fess_count[user_id]
    return date != today or count == 1

banned_words = ['anjing', 'bangsat', 'kontol', 'tolol']

def contains_bad_words(text):
    return any(word in text.lower() for word in banned_words)

# ─── MARKUPS ──────────────────────────────────────────────
def main_menu_markup(user_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(t(user_id, "btn_send"), callback_data="send_fess"))
    markup.row(
        types.InlineKeyboardButton(t(user_id, "btn_stats"), callback_data="show_stats"),
        types.InlineKeyboardButton(t(user_id, "btn_delete"), callback_data="delete_fess")
    )
    markup.row(
        types.InlineKeyboardButton(t(user_id, "btn_profile"), callback_data="my_profile"),
        types.InlineKeyboardButton(t(user_id, "btn_settings"), callback_data="settings")
    )
    markup.row(
        types.InlineKeyboardButton(t(user_id, "btn_badge_benefit"), callback_data="badge_benefit"),
        types.InlineKeyboardButton(t(user_id, "btn_gift"), callback_data="send_gift")
    )
    markup.add(types.InlineKeyboardButton(t(user_id, "btn_checkin"), callback_data="daily_checkin"))
    return markup

def back_markup(user_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(t(user_id, "btn_back"), callback_data="back_menu"))
    return markup

def settings_markup(user_id):
    lang = user_lang.get(user_id, "id")
    notif = user_notif.get(user_id, True)
    lang_str = "🇮🇩 Indonesia" if lang == "id" else "🇬🇧 English"
    notif_str = t(user_id, "notif_active") if notif else t(user_id, "notif_inactive")
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f" {t(user_id, 'btn_lang')} — {lang_str}", callback_data="toggle_lang"))
    markup.add(types.InlineKeyboardButton(f" {t(user_id, 'btn_notif')} — {notif_str}", callback_data="toggle_notif"))
    markup.add(types.InlineKeyboardButton(t(user_id, "btn_del_account"), callback_data="ask_del_account"))
    markup.add(types.InlineKeyboardButton(t(user_id, "btn_back"), callback_data="back_menu"))
    return markup

def badge_benefit_markup(user_id):
    level = get_badge_level(user_id)
    markup = types.InlineKeyboardMarkup()
    if level == 0:
        markup.add(types.InlineKeyboardButton(t(user_id, "btn_back"), callback_data="back_menu"))
        return markup
    markup.add(types.InlineKeyboardButton("✏️ Edit Menfess", callback_data="edit_fess"))
    markup.add(types.InlineKeyboardButton("📊 Kirim Polling", callback_data="send_poll"))
    if level >= 2:
        markup.add(types.InlineKeyboardButton("⏰ Jadwal Menfess", callback_data="schedule_fess"))
    if level >= 3:
        hide_status = "👁 Tampilkan Badge" if user_hide_badge.get(user_id, False) else "👻 Sembunyikan Badge"
        markup.add(types.InlineKeyboardButton(hide_status, callback_data="toggle_hide_badge"))
    if level >= 4:
        markup.add(types.InlineKeyboardButton("🎨 Custom Prefix", callback_data="custom_prefix"))
        markup.add(types.InlineKeyboardButton("🖊 Invisible Ink", callback_data="invisible_ink"))
    markup.add(types.InlineKeyboardButton(t(user_id, "btn_back"), callback_data="back_menu"))
    return markup

# ─── SCHEDULED FESS WORKER ────────────────────────────────
def scheduled_fess_worker():
    while True:
        now = datetime.now()
        to_send = [f for f in scheduled_fess if f["send_time"] <= now]
        for fess in to_send:
            scheduled_fess.remove(fess)
            try:
                user_id = fess["user_id"]
                prefix = get_prefix(user_id)
                if fess["type"] == "text":
                    clean = strip_leading_emoji(fess["text"])
                    msg_sent = bot.send_message(CHANNEL_ID, prefix + clean)
                    preview = fess["text"]
                else:
                    clean_caption = strip_leading_emoji(fess.get("caption", ""))
                    msg_sent = bot.send_photo(CHANNEL_ID, fess["file_id"], caption=prefix + clean_caption)
                    preview = f"[foto] {fess.get('caption', '')}"

                global total_fess_sent
                total_fess_sent += 1
                user_total_fess[user_id] = user_total_fess.get(user_id, 0) + 1
                add_clover(user_id, 3)
                update_peak(user_id)

                if user_id not in user_last_messages:
                    user_last_messages[user_id] = []
                deadline = datetime.now() + timedelta(minutes=get_edit_minutes(user_id))
                user_last_messages[user_id].append((msg_sent.message_id, preview, deadline))
                if len(user_last_messages[user_id]) > 3:
                    user_last_messages[user_id].pop(0)

                link = f"https://t.me/c/{str(CHANNEL_ID)[4:]}/{msg_sent.message_id}"
                bot.send_message(user_id, f"⏰ Menfess Terjadwal Kamu Berhasil Terkirim! +3 🍀\n\n[Lihat Menfess]({link})", parse_mode="Markdown")
            except Exception as e:
                print(f"Scheduled fess error: {e}")
        time.sleep(30)

# ─── CHANNEL GUARD ────────────────────────────────────────
@bot.channel_post_handler(func=lambda message: True)
def channel_guard(message):
    if message.chat.id != CHANNEL_ID:
        return
    text = message.text or message.caption or ""
    if "[ 🍀 A GIFT FROM THE CORNER ]" in text:
        if message.message_id not in valid_gift_ids:
            try:
                bot.delete_message(CHANNEL_ID, message.message_id)
            except:
                pass

# ─── HANDLERS ─────────────────────────────────────────────
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    is_new = user_id not in ever_registered
    ever_registered.add(user_id)
    if user_id not in user_first_seen:
        user_first_seen[user_id] = datetime.now().strftime("%d %b %Y")
    if is_new:
        add_clover(user_id, 10)
    if user_id not in user_lang:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🇮🇩 Bahasa Indonesia", callback_data="lang_id"))
        markup.add(types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"))
        welcome_text = TEXTS["id"]["welcome"]
        if is_new:
            welcome_text += TEXTS["id"]["welcome_bonus"]
        bot.send_message(user_id, welcome_text, parse_mode="Markdown", reply_markup=markup)
    else:
        name = message.from_user.first_name or "Cornerpeeps"
        bot.send_message(user_id, t(user_id, "menu").format(name=name), parse_mode="Markdown", reply_markup=main_menu_markup(user_id))

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return
    lb = get_leaderboard()
    text = "👑 *Admin Leaderboard*\n\n"
    for i, (uid, count) in enumerate(lb[:20]):
        try:
            uname = bot.get_chat(uid).username or f"id:{uid}"
        except:
            uname = f"id:{uid}"
        text += f"#{i+1} @{uname} — {count} fess\n"
    bot.send_message(ADMIN_ID, text, parse_mode="Markdown")

@bot.message_handler(commands=['addclover'])
def add_clover_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, "Format: /addclover @username jumlah")
        return
    try:
        username = parts[1].replace("@", "")
        amount = int(parts[2])
        target_id = None
        for uid in user_first_seen.keys():
            try:
                chat = bot.get_chat(uid)
                if chat.username == username:
                    target_id = uid
                    break
            except:
                pass
        if target_id:
            add_clover(target_id, amount)
            bot.reply_to(message, f"✅ +{amount} 🍀 Berhasil Ditambahkan Ke @{username}")
        else:
            bot.reply_to(message, "❌ User Tidak Ditemukan.")
    except:
        bot.reply_to(message, "❌ Format Salah.")

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return
    text = message.text.replace('/broadcast', '').strip()
    if not text:
        bot.reply_to(message, "❌ Tulis pesan setelah /broadcast\n\nContoh:\n/broadcast Halo Cornerpeeps! 💚")
        return
    if text not in broadcast_sent:
        broadcast_sent[text] = set()
    success = 0
    failed = 0
    skipped = 0
    for user_id in list(user_first_seen.keys()):
        if user_id in broadcast_sent[text]:
            skipped += 1
            continue
        try:
            bot.send_message(user_id, text, parse_mode="Markdown")
            broadcast_sent[text].add(user_id)
            success += 1
        except:
            failed += 1
    bot.reply_to(message, f"✅ Broadcast Selesai!\n\n📨 Terkirim: {success}\n⏭ Dilewati: {skipped}\n❌ Gagal: {failed}")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    global total_fess_sent
    user_id = call.from_user.id
    data = call.data

    if data in ("lang_id", "lang_en"):
        user_lang[user_id] = "id" if data == "lang_id" else "en"
        name = call.from_user.first_name or "Cornerpeeps"
        bot.edit_message_text(
            t(user_id, "menu").format(name=name),
            call.message.chat.id, call.message.message_id,
            parse_mode="Markdown", reply_markup=main_menu_markup(user_id)
        )

    elif data == "back_menu":
        name = call.from_user.first_name or "Cornerpeeps"
        bot.edit_message_text(
            t(user_id, "menu").format(name=name),
            call.message.chat.id, call.message.message_id,
            parse_mode="Markdown", reply_markup=main_menu_markup(user_id)
        )

    elif data == "daily_checkin":
        today = datetime.now().date()
        last = user_last_checkin.get(user_id)
        if last == today:
            bot.answer_callback_query(call.id, t(user_id, "checkin_already"), show_alert=True)
            return
        yesterday = today - timedelta(days=1)
        if last == yesterday:
            user_streak[user_id] = user_streak.get(user_id, 0) + 1
        else:
            user_streak[user_id] = 1
        user_last_checkin[user_id] = today
        add_clover(user_id, 1)
        streak = user_streak[user_id]
        msg = t(user_id, "checkin_done").format(streak=streak)
        if streak % 7 == 0:
            add_clover(user_id, 5)
            msg += f"\n\n{t(user_id, 'checkin_streak')}"
        bot.answer_callback_query(call.id, msg, show_alert=True)

    elif data == "send_fess":
        if not can_send(user_id):
            bot.answer_callback_query(call.id, t(user_id, "quota"), show_alert=True)
            return
        pending_users.add(user_id)
        preview_data[user_id] = {"mode": "normal"}
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(t(user_id, "btn_cancel"), callback_data="cancel_send"))
        bot.edit_message_text(
            t(user_id, "send_guide"),
            call.message.chat.id, call.message.message_id,
            parse_mode="Markdown", reply_markup=markup
        )

    elif data == "cancel_send":
        pending_users.discard(user_id)
        preview_data.pop(user_id, None)
        edit_pending.pop(user_id, None)
        name = call.from_user.first_name or "Cornerpeeps"
        bot.edit_message_text(
            t(user_id, "menu").format(name=name),
            call.message.chat.id, call.message.message_id,
            parse_mode="Markdown", reply_markup=main_menu_markup(user_id)
        )

    elif data == "confirm_send":
        pd = preview_data.pop(user_id, None)
        pending_users.discard(user_id)
        if not pd:
            bot.answer_callback_query(call.id)
            return
        try:
            prefix = get_prefix(user_id)
            if pd["type"] == "text":
                clean_text = strip_leading_emoji(pd["text"])
                if pd.get("invisible"):
                    clean_text = f"||{clean_text}||"
                msg_sent = bot.send_message(CHANNEL_ID, prefix + clean_text, parse_mode="Markdown")
                preview = pd["text"]
            else:
                clean_caption = strip_leading_emoji(pd.get("caption", ""))
                msg_sent = bot.send_photo(CHANNEL_ID, pd["file_id"], caption=prefix + clean_caption)
                preview = f"[foto] {pd.get('caption', '')}"

            total_fess_sent += 1
            first_today = is_first_fess_today(user_id)
            user_total_fess[user_id] = user_total_fess.get(user_id, 0) + 1
            add_clover(user_id, 2)
            if first_today:
                add_clover(user_id, 1)
            update_peak(user_id)

            deadline = datetime.now() + timedelta(minutes=get_edit_minutes(user_id))
            if user_id not in user_last_messages:
                user_last_messages[user_id] = []
            user_last_messages[user_id].append((msg_sent.message_id, preview, deadline))
            if len(user_last_messages[user_id]) > 3:
                user_last_messages[user_id].pop(0)

            link = f"https://t.me/c/{str(CHANNEL_ID)[4:]}/{msg_sent.message_id}"
            sent_text = t(user_id, "sent").format(link=link)
            if first_today:
                sent_text += t(user_id, "first_fess_bonus")

            if user_notif.get(user_id, True):
                bot.edit_message_text(
                    sent_text,
                    call.message.chat.id, call.message.message_id,
                    parse_mode="Markdown", reply_markup=back_markup(user_id)
                )
            else:
                name = call.from_user.first_name or "Cornerpeeps"
                bot.edit_message_text(
                    t(user_id, "menu").format(name=name),
                    call.message.chat.id, call.message.message_id,
                    parse_mode="Markdown", reply_markup=main_menu_markup(user_id)
                )

            with open("log.txt", "a") as f:
                uname = call.from_user.username or f"id:{user_id}"
                f.write(f"{uname} ({user_id}): {preview}\n")

        except Exception as e:
            bot.edit_message_text(
                t(user_id, "send_error").format(e=e),
                call.message.chat.id, call.message.message_id,
                reply_markup=back_markup(user_id)
            )

    elif data == "show_stats":
        rank = get_rank(user_id)
        lb = get_leaderboard()
        total_senders = len(user_total_fess)
        text = t(user_id, "stats_title") + "\n\n"
        text += f"{t(user_id, 'stats_total')}: *{total_fess_sent}*\n"
        text += f"{t(user_id, 'stats_senders')}: *{total_senders}*\n\n"
        if rank:
            text += t(user_id, "rank_label") + f": *#{rank}*\n\n"
            text += "```\n"
            start_idx = max(0, rank - 4)
            end_idx = min(len(lb), rank + 3)
            for i in range(start_idx, end_idx):
                uid, count = lb[i]
                pos = i + 1
                if uid == user_id:
                    uname = call.from_user.username or t(user_id, "you_pronoun")
                    text += f"#{pos} @{uname} ← {t(user_id, 'you_label')} ({count})\n"
                else:
                    uname = sensor_username(pos)
                    text += f"#{pos} @{uname} ({count})\n"
            text += "```"
        else:
            text += t(user_id, "leaderboard_empty")
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                              parse_mode="Markdown", reply_markup=back_markup(user_id))

    elif data == "delete_fess":
        messages = user_last_messages.get(user_id, [])
        if not messages:
            bot.edit_message_text(t(user_id, "no_fess"), call.message.chat.id, call.message.message_id,
                                  reply_markup=back_markup(user_id))
            return
        markup = types.InlineKeyboardMarkup()
        for i, item in enumerate(messages):
            msg_id, preview = item[0], item[1]
            short = preview[:28] + "..." if len(preview) > 28 else preview
            markup.add(types.InlineKeyboardButton(f"🗑 Fess #{i+1} — {short}", callback_data=f"ask_delete_{msg_id}_{i+1}"))
        markup.add(types.InlineKeyboardButton(t(user_id, "btn_cancel"), callback_data="back_menu"))
        bot.edit_message_text(t(user_id, "pick_delete"), call.message.chat.id, call.message.message_id,
                              reply_markup=markup)

    elif data.startswith("ask_delete_"):
        parts = data.split("_")
        msg_id = int(parts[2])
        num = parts[3]
        messages = user_last_messages.get(user_id, [])
        preview = next((item[1] for item in messages if item[0] == msg_id), "...")
        short = preview[:40] + "..." if len(preview) > 40 else preview
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton(t(user_id, "btn_yes_delete"), callback_data=f"do_delete_{msg_id}"),
            types.InlineKeyboardButton(t(user_id, "btn_cancel"), callback_data="delete_fess")
        )
        bot.edit_message_text(
            t(user_id, "confirm_delete").format(num=num, preview=short),
            call.message.chat.id, call.message.message_id,
            parse_mode="Markdown", reply_markup=markup
        )

    elif data.startswith("do_delete_"):
        msg_id = int(data.split("_")[2])
        try:
            bot.delete_message(CHANNEL_ID, msg_id)
            if user_id in user_last_messages:
                user_last_messages[user_id] = [item for item in user_last_messages[user_id] if item[0] != msg_id]
            bot.edit_message_text(t(user_id, "deleted"), call.message.chat.id, call.message.message_id,
                                  reply_markup=back_markup(user_id))
        except:
            bot.edit_message_text(t(user_id, "delete_fail"), call.message.chat.id, call.message.message_id,
                                  reply_markup=back_markup(user_id))

    elif data == "my_profile":
        uname = call.from_user.username or t(user_id, "no_username")
        first_seen = user_first_seen.get(user_id, "—")
        total = user_total_fess.get(user_id, 0)
        quota = quota_left(user_id)
        rank = get_rank(user_id)
        rank_str = f"#{rank}" if rank else "—"
        badge = get_badge_label(user_id)
        clover = user_clover.get(user_id, 0)
        peak_rank = user_peak_rank.get(user_id)
        peak_rank_date = user_peak_rank_date.get(user_id, "—")
        peak_rank_str = f"#{peak_rank} ({peak_rank_date})" if peak_rank else "—"
        peak_badge_level = user_peak_badge.get(user_id, 0)
        peak_badge_date = user_peak_badge_date.get(user_id, "—")
        badge_labels = ["🐣 Newbie", "💫 Regular", "⭐ Active", "🔥 Top Sender", "👑 Legend"]
        peak_badge_str = f"{badge_labels[peak_badge_level]} ({peak_badge_date})" if peak_badge_level > 0 else "—"
        text = t(user_id, "profile_title") + "\n\n"
        text += f"{t(user_id, 'profile_username')}: *@{uname}*\n"
        text += f"{t(user_id, 'profile_id')}: `{user_id}`\n"
        text += f"{t(user_id, 'profile_joined')}: *{first_seen}*\n"
        text += f"{t(user_id, 'profile_total')}: *{total}*\n"
        text += f"{t(user_id, 'profile_quota')}: *{quota}/5*\n"
        text += f"{t(user_id, 'profile_clover')}: *{clover}* 🍀\n"
        text += f"{t(user_id, 'profile_ranking')}: *{rank_str}*\n"
        text += f"{t(user_id, 'profile_peak_rank')}: *{peak_rank_str}*\n"
        text += f"{t(user_id, 'profile_badge')}: {badge}\n"
        text += f"{t(user_id, 'profile_peak_badge')}: {peak_badge_str}"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                              parse_mode="Markdown", reply_markup=back_markup(user_id))

    elif data == "settings":
        bot.edit_message_text(t(user_id, "settings_title"), call.message.chat.id, call.message.message_id,
                              parse_mode="Markdown", reply_markup=settings_markup(user_id))

    elif data == "toggle_lang":
        current = user_lang.get(user_id, "id")
        user_lang[user_id] = "en" if current == "id" else "id"
        bot.edit_message_text(t(user_id, "settings_title"), call.message.chat.id, call.message.message_id,
                              parse_mode="Markdown", reply_markup=settings_markup(user_id))

    elif data == "toggle_notif":
        user_notif[user_id] = not user_notif.get(user_id, True)
        bot.edit_message_text(t(user_id, "settings_title"), call.message.chat.id, call.message.message_id,
                              parse_mode="Markdown", reply_markup=settings_markup(user_id))

    elif data == "ask_del_account":
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton(t(user_id, "btn_yes_del_account"), callback_data="confirm_del_account"),
            types.InlineKeyboardButton(t(user_id, "btn_cancel"), callback_data="settings")
        )
        bot.edit_message_text(t(user_id, "delete_account"), call.message.chat.id, call.message.message_id,
                              parse_mode="Markdown", reply_markup=markup)

    elif data == "confirm_del_account":
        for d in [user_lang, user_fess_count, user_last_messages, user_total_fess,
                  user_first_seen, user_notif, user_clover, user_streak, user_last_checkin,
                  user_peak_rank, user_peak_rank_date, user_peak_badge, user_peak_badge_date,
                  user_prefix, user_hide_badge, preview_data]:
            d.pop(user_id, None)
        pending_users.discard(user_id)
        edit_pending.pop(user_id, None)
        bot.edit_message_text(t(user_id, "account_deleted_msg"), call.message.chat.id, call.message.message_id)

    elif data == "badge_benefit":
        level = get_badge_level(user_id)
        badge = get_badge_label(user_id)
        if level == 0:
            text = f"🐣 *Badge Benefit*\n\n{badge}\n\nKamu belum punya benefit khusus.\nNaik rank untuk unlock fitur!"
        else:
            text = f"🎖 *Badge Benefit*\n\n{badge}\n\nPilih fitur yang mau digunakan:"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                              parse_mode="Markdown", reply_markup=badge_benefit_markup(user_id))

    elif data == "toggle_hide_badge":
        user_hide_badge[user_id] = not user_hide_badge.get(user_id, False)
        status = t(user_id, "hide_badge_on") if user_hide_badge[user_id] else t(user_id, "hide_badge_off")
        bot.answer_callback_query(call.id, status, show_alert=True)
        badge = get_badge_label(user_id)
        bot.edit_message_text(f"🎖 *Badge Benefit*\n\n{badge}\n\nPilih fitur yang mau digunakan:",
                              call.message.chat.id, call.message.message_id,
                              parse_mode="Markdown", reply_markup=badge_benefit_markup(user_id))

    elif data == "custom_prefix":
        markup = types.InlineKeyboardMarkup()
        hearts = ["🤍", "🖤", "🧡", "💛", "💜", "🩷", "🩵", "❤️", "💚"]
        rows = [hearts[i:i+3] for i in range(0, len(hearts), 3)]
        for row in rows:
            markup.row(*[types.InlineKeyboardButton(h, callback_data=f"set_prefix_{h}") for h in row])
        markup.add(types.InlineKeyboardButton(t(user_id, "btn_back"), callback_data="badge_benefit"))
        bot.edit_message_text(t(user_id, "prefix_select"), call.message.chat.id, call.message.message_id,
                              reply_markup=markup)

    elif data.startswith("set_prefix_"):
        prefix = data.replace("set_prefix_", "")
        user_prefix[user_id] = prefix
        bot.answer_callback_query(call.id, f"✅ Prefix Diubah Ke {prefix}", show_alert=True)
        badge = get_badge_label(user_id)
        bot.edit_message_text(f"🎖 *Badge Benefit*\n\n{badge}\n\nPilih fitur yang mau digunakan:",
                              call.message.chat.id, call.message.message_id,
                              parse_mode="Markdown", reply_markup=badge_benefit_markup(user_id))

    elif data == "invisible_ink":
        pending_users.add(user_id)
        preview_data[user_id] = {"mode": "invisible"}
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(t(user_id, "btn_cancel"), callback_data="cancel_send"))
        bot.edit_message_text(t(user_id, "invisible_guide"), call.message.chat.id, call.message.message_id,
                              parse_mode="Markdown", reply_markup=markup)

    elif data == "edit_fess":
        if get_edit_minutes(user_id) == 0:
            bot.answer_callback_query(call.id, t(user_id, "no_edit_benefit"), show_alert=True)
            return
        messages = user_last_messages.get(user_id, [])
        valid = [(msg_id, preview, deadline) for msg_id, preview, deadline in messages if deadline > datetime.now()]
        if not valid:
            bot.answer_callback_query(call.id, t(user_id, "edit_expired"), show_alert=True)
            return
        markup = types.InlineKeyboardMarkup()
        for i, (msg_id, preview, deadline) in enumerate(valid):
            short = preview[:25] + "..." if len(preview) > 25 else preview
            mins_left = int((deadline - datetime.now()).total_seconds() / 60)
            markup.add(types.InlineKeyboardButton(
                f"✏️ Fess #{i+1} — {short} ({mins_left}m)",
                callback_data=f"do_edit_{msg_id}"
            ))
        markup.add(types.InlineKeyboardButton(t(user_id, "btn_cancel"), callback_data="badge_benefit"))
        bot.edit_message_text(t(user_id, "edit_select"), call.message.chat.id, call.message.message_id,
                              reply_markup=markup)

    elif data.startswith("do_edit_"):
        msg_id = int(data.split("_")[2])
        messages = user_last_messages.get(user_id, [])
        item = next((item for item in messages if item[0] == msg_id), None)
        if not item or item[2] < datetime.now():
            bot.answer_callback_query(call.id, t(user_id, "edit_expired"), show_alert=True)
            return
        edit_pending[user_id] = {"msg_id": msg_id, "deadline": item[2]}
        pending_users.add(user_id)
        preview_data[user_id] = {"mode": "edit", "msg_id": msg_id}
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(t(user_id, "btn_cancel"), callback_data="cancel_send"))
        bot.edit_message_text(t(user_id, "edit_type"), call.message.chat.id, call.message.message_id,
                              parse_mode="Markdown", reply_markup=markup)

    elif data == "schedule_fess":
        pending_users.add(user_id)
        preview_data[user_id] = {"mode": "schedule"}
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(t(user_id, "btn_cancel"), callback_data="cancel_send"))
        bot.edit_message_text(
            "⏰ *Jadwal Menfess*\n\nKetik Waktu Pengiriman Dalam Format *HH:MM* (WIB)\n\nContoh: *23:00*",
            call.message.chat.id, call.message.message_id,
            parse_mode="Markdown", reply_markup=markup
        )

    elif data.startswith("confirm_schedule_"):
        time_str = data.replace("confirm_schedule_", "")
        pd = preview_data.pop(user_id, None)
        pending_users.discard(user_id)
        if not pd:
            bot.answer_callback_query(call.id)
            return
        try:
            now = datetime.now()
            send_time = datetime.strptime(f"{now.strftime('%Y-%m-%d')} {time_str}", "%Y-%m-%d %H:%M")
            send_time = send_time - timedelta(hours=7)
            if send_time < now:
                send_time += timedelta(days=1)
            scheduled_fess.append({
                "user_id": user_id,
                "type": pd["type"],
                "text": pd.get("text", ""),
                "file_id": pd.get("file_id", ""),
                "caption": pd.get("caption", ""),
                "send_time": send_time
            })
            bot.edit_message_text(
                t(user_id, "schedule_set").format(time=time_str),
                call.message.chat.id, call.message.message_id,
                parse_mode="Markdown", reply_markup=back_markup(user_id)
            )
        except:
            bot.edit_message_text(
                t(user_id, "schedule_format"),
                call.message.chat.id, call.message.message_id,
                parse_mode="Markdown", reply_markup=back_markup(user_id)
            )

    elif data == "send_poll":
        pending_users.add(user_id)
        preview_data[user_id] = {"mode": "poll_question"}
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(t(user_id, "btn_cancel"), callback_data="cancel_send"))
        bot.edit_message_text(t(user_id, "poll_question"), call.message.chat.id, call.message.message_id,
                              parse_mode="Markdown", reply_markup=markup)

    elif data == "confirm_poll_send":
        pd = preview_data.pop(user_id, None)
        pending_users.discard(user_id)
        if not pd:
            bot.answer_callback_query(call.id)
            return
        try:
            bot.send_poll(CHANNEL_ID, pd["question"], pd["options"], is_anonymous=True)
            add_clover(user_id, 1)
            bot.edit_message_text(t(user_id, "poll_sent"), call.message.chat.id, call.message.message_id,
                                  parse_mode="Markdown", reply_markup=back_markup(user_id))
        except Exception as e:
            bot.edit_message_text(t(user_id, "send_error").format(e=e),
                                  call.message.chat.id, call.message.message_id,
                                  reply_markup=back_markup(user_id))

    elif data == "send_gift":
        clover = user_clover.get(user_id, 0)
        markup = types.InlineKeyboardMarkup()
        for key, gift in GIFT_PRICES.items():
            markup.add(types.InlineKeyboardButton(
                f"{gift['emoji']} {gift['name']} — {gift['price']} 🍀",
                callback_data=f"gift_select_{key}"
            ))
        markup.add(types.InlineKeyboardButton(t(user_id, "btn_back"), callback_data="back_menu"))
        bot.edit_message_text(
            f"🎁 *Kirim Hadiah*\n\n🍀 Clover Kamu: *{clover}*\n\nPilih Jenis Hadiah:",
            call.message.chat.id, call.message.message_id,
            parse_mode="Markdown", reply_markup=markup
        )

    elif data.startswith("gift_select_"):
        gift_key = data.replace("gift_select_", "")
        gift = GIFT_PRICES[gift_key]
        clover = user_clover.get(user_id, 0)
        if clover < gift["price"]:
            bot.answer_callback_query(
                call.id,
                t(user_id, "not_enough_clover").format(need=gift["price"], have=clover),
                show_alert=True
            )
            return
        pending_users.add(user_id)
        preview_data[user_id] = {"mode": "gift", "gift_key": gift_key, "step": "username"}
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(t(user_id, "btn_cancel"), callback_data="cancel_send"))
        bot.edit_message_text(
            f"{gift['emoji']} *{gift['name']}*\n\nKetik Username Penerima:\n_(Contoh: @username)_",
            call.message.chat.id, call.message.message_id,
            parse_mode="Markdown", reply_markup=markup
        )

    elif data in ("gift_anon_send", "gift_named_send"):
        pd = preview_data.get(user_id, {})
        is_anon = data == "gift_anon_send"
        gift_key = pd.get("gift_key")
        to = pd.get("to", "someone")
        msg = pd.get("msg", "")
        preview_text = make_gift_template(gift_key, to, msg)
        pd["preview_text"] = preview_text
        pd["to_username"] = to
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton(t(user_id, "btn_send_confirm"), callback_data="confirm_gift"),
            types.InlineKeyboardButton(t(user_id, "btn_cancel"), callback_data="cancel_send")
        )
        bot.edit_message_text(
            t(user_id, "gift_preview").format(preview=preview_text),
            call.message.chat.id, call.message.message_id,
            parse_mode="Markdown", reply_markup=markup
        )

    elif data == "confirm_gift":
        pd = preview_data.pop(user_id, None)
        pending_users.discard(user_id)
        if not pd:
            bot.answer_callback_query(call.id)
            return
        gift_key = pd.get("gift_key")
        gift = GIFT_PRICES[gift_key]
        if not use_clover(user_id, gift["price"]):
            bot.answer_callback_query(
                call.id,
                t(user_id, "not_enough_clover").format(need=gift["price"], have=user_clover.get(user_id, 0)),
                show_alert=True
            )
            return
        try:
            msg_sent = bot.send_message(CHANNEL_ID, pd["preview_text"], parse_mode="Markdown")
            valid_gift_ids.add(msg_sent.message_id)
            link = f"https://t.me/c/{str(CHANNEL_ID)[4:]}/{msg_sent.message_id}"
            to_username = pd.get("to_username", "")
            for uid in user_first_seen.keys():
                try:
                    chat = bot.get_chat(uid)
                    if chat.username and chat.username.lower() == to_username.lower():
                        bot.send_message(uid, t(uid, "gift_notif").format(link=link), parse_mode="Markdown")
                        break
                except:
                    pass
            bot.edit_message_text(
                t(user_id, "gift_sent").format(price=gift["price"]),
                call.message.chat.id, call.message.message_id,
                parse_mode="Markdown", reply_markup=back_markup(user_id)
            )
        except Exception as e:
            bot.edit_message_text(
                t(user_id, "send_error").format(e=e),
                call.message.chat.id, call.message.message_id,
                reply_markup=back_markup(user_id)
            )

    bot.answer_callback_query(call.id)


@bot.message_handler(func=lambda message: True, content_types=['text', 'photo'])
def handle_message(message):
    user_id = message.from_user.id

    if user_id not in pending_users:
        if user_id not in user_lang:
            start(message)
        else:
            name = message.from_user.first_name or "Cornerpeeps"
            bot.send_message(user_id, t(user_id, "menu").format(name=name),
                             parse_mode="Markdown", reply_markup=main_menu_markup(user_id))
        return

    pd = preview_data.get(user_id, {})
    mode = pd.get("mode", "normal")

    if mode == "edit":
        if message.content_type != 'text':
            return
        msg_id = pd.get("msg_id")
        ep = edit_pending.get(user_id)
        if not ep or ep["deadline"] < datetime.now():
            bot.reply_to(message, t(user_id, "edit_expired"))
            pending_users.discard(user_id)
            preview_data.pop(user_id, None)
            return
        new_text = strip_leading_emoji(message.text.strip())
        prefix = get_prefix(user_id)
        try:
            bot.edit_message_text(prefix + new_text, CHANNEL_ID, msg_id)
            if user_id in user_last_messages:
                user_last_messages[user_id] = [
                    (mid, new_text, dl) if mid == msg_id else (mid, prev, dl)
                    for mid, prev, dl in user_last_messages[user_id]
                ]
            bot.send_message(user_id, t(user_id, "edit_done"), reply_markup=main_menu_markup(user_id))
        except:
            bot.send_message(user_id, t(user_id, "edit_fail"), reply_markup=main_menu_markup(user_id))
        pending_users.discard(user_id)
        preview_data.pop(user_id, None)
        edit_pending.pop(user_id, None)
        return

    if mode == "schedule":
        if message.content_type != 'text':
            return
        time_str = message.text.strip()
        try:
            datetime.strptime(time_str, "%H:%M")
        except:
            bot.reply_to(message, t(user_id, "schedule_format"), parse_mode="Markdown")
            return
        preview_data[user_id] = {"mode": "schedule_content", "time_str": time_str}
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(t(user_id, "btn_cancel"), callback_data="cancel_send"))
        bot.send_message(user_id,
            f"⏰ Jadwal: *{time_str}* WIB\n\nSekarang Ketik Atau Kirim Foto Menfess Kamu:",
            parse_mode="Markdown", reply_markup=markup)
        return

    if mode == "schedule_content":
        time_str = pd.get("time_str")
        if message.content_type == 'text':
            text = strip_leading_emoji(message.text.strip())
            if contains_bad_words(text):
                bot.reply_to(message, t(user_id, "bad_word"))
                return
            preview_data[user_id] = {"mode": "schedule_content", "time_str": time_str, "type": "text", "text": text}
        elif message.content_type == 'photo':
            file_id = message.photo[-1].file_id
            caption = strip_leading_emoji(message.caption.strip() if message.caption else "")
            if contains_bad_words(caption):
                bot.reply_to(message, t(user_id, "bad_word"))
                return
            preview_data[user_id] = {"mode": "schedule_content", "time_str": time_str, "type": "photo", "file_id": file_id, "caption": caption}
        else:
            return
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton(t(user_id, "btn_send_confirm"), callback_data=f"confirm_schedule_{time_str}"),
            types.InlineKeyboardButton(t(user_id, "btn_cancel"), callback_data="cancel_send")
        )
        preview_text = preview_data[user_id].get("text", f"[foto] {preview_data[user_id].get('caption', '')}")
        bot.send_message(user_id,
            f"⏰ *Preview Menfess Terjadwal:*\n\n{get_prefix(user_id)}{preview_text}\n\n_Akan Dikirim Jam *{time_str}* WIB_",
            parse_mode="Markdown", reply_markup=markup)
        return

    if mode == "poll_question":
        if message.content_type != 'text':
            return
        preview_data[user_id] = {"mode": "poll_options", "question": message.text.strip()}
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(t(user_id, "btn_cancel"), callback_data="cancel_send"))
        bot.send_message(user_id, t(user_id, "poll_options"), parse_mode="Markdown", reply_markup=markup)
        return

    if mode == "poll_options":
        if message.content_type != 'text':
            return
        options = [o.strip() for o in message.text.split("\n") if o.strip()]
        if len(options) < 2:
            bot.reply_to(message, "❌ Minimal 2 Opsi!")
            return
        if len(options) > 10:
            bot.reply_to(message, "❌ Maksimal 10 Opsi!")
            return
        question = pd.get("question")
        preview_data[user_id] = {"mode": "poll_options", "question": question, "options": options}
        preview_text = f"📊 *{question}*\n\n" + "\n".join([f"• {o}" for o in options])
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton(t(user_id, "btn_send_confirm"), callback_data="confirm_poll_send"),
            types.InlineKeyboardButton(t(user_id, "btn_cancel"), callback_data="cancel_send")
        )
        bot.send_message(user_id, f"👀 *Preview Polling:*\n\n{preview_text}\n\nKirim Ke Channel?",
                         parse_mode="Markdown", reply_markup=markup)
        return

    if mode == "gift" and pd.get("step") == "username":
        if message.content_type != 'text':
            return
        to = message.text.strip().replace("@", "")
        preview_data[user_id]["to"] = to
        preview_data[user_id]["step"] = "message"
        gift_key = pd.get("gift_key")
        gift = GIFT_PRICES[gift_key]
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(t(user_id, "btn_cancel"), callback_data="cancel_send"))
        bot.send_message(user_id,
            f"{gift['emoji']} Untuk: *@{to}*\n\nKetik Pesan Hadiah Kamu:",
            parse_mode="Markdown", reply_markup=markup)
        return

    if mode == "gift" and pd.get("step") == "message":
        if message.content_type != 'text':
            return
        if contains_bad_words(message.text):
            bot.reply_to(message, t(user_id, "bad_word"))
            return
        preview_data[user_id]["msg"] = message.text.strip()
        preview_data[user_id]["step"] = "identity"
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("💚 Anonim", callback_data="gift_anon_send"),
            types.InlineKeyboardButton("👤 Sebut Username", callback_data="gift_named_send")
        )
        markup.add(types.InlineKeyboardButton(t(user_id, "btn_cancel"), callback_data="cancel_send"))
        bot.send_message(user_id, "Kirim Sebagai Siapa?", reply_markup=markup)
        return

    if mode == "invisible":
        if message.content_type != 'text':
            return
        text = strip_leading_emoji(message.text.strip())
        if contains_bad_words(text):
            bot.reply_to(message, t(user_id, "bad_word"))
            return
        preview_data[user_id] = {"type": "text", "text": text, "invisible": True, "mode": "invisible"}
        badge = get_badge_emoji(user_id)
        prefix = user_prefix.get(user_id, "💚") if get_badge_level(user_id) == 4 else "💚"
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton(t(user_id, "btn_send_confirm"), callback_data="confirm_send"),
            types.InlineKeyboardButton(t(user_id, "btn_cancel"), callback_data="cancel_send")
        )
        bot.send_message(user_id,
            f"🖊 *Preview Invisible Ink:*\n\n{badge}{prefix} ||{text}||\n\n_Pesan Akan Tersembunyi Di Channel._",
            parse_mode="Markdown", reply_markup=markup)
        return

    if message.content_type == 'text':
        text = message.text.strip()
        if len(text) > 4000:
            bot.reply_to(message, t(user_id, "too_long"))
            return
        if contains_bad_words(text):
            bot.reply_to(message, t(user_id, "bad_word"))
            return
        preview_data[user_id] = {"type": "text", "text": text, "mode": "normal"}
        badge = get_badge_emoji(user_id)
        preview_text = t(user_id, "preview").format(badge=badge, text=text[:200] + ("..." if len(text) > 200 else ""))

    elif message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        caption = message.caption.strip() if message.caption else ""
        if len(caption) > 1024:
            bot.reply_to(message, t(user_id, "too_long"))
            return
        if contains_bad_words(caption):
            bot.reply_to(message, t(user_id, "bad_word"))
            return
        preview_data[user_id] = {"type": "photo", "file_id": file_id, "caption": caption, "mode": "normal"}
        badge = get_badge_emoji(user_id)
        preview_text = t(user_id, "preview").format(badge=badge, text=f"[foto] {caption}" if caption else "[foto]")
    else:
        return

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton(t(user_id, "btn_send_confirm"), callback_data="confirm_send"),
        types.InlineKeyboardButton(t(user_id, "btn_cancel"), callback_data="cancel_send")
    )
    bot.send_message(user_id, preview_text, parse_mode="Markdown", reply_markup=markup)


# ─── RUN ──────────────────────────────────────────────────
def run_web():
    print("WEB START")
    app.run(host="0.0.0.0", port=8080)

def run_bot():
    print("BOT START")
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    threading.Thread(target=scheduled_fess_worker, daemon=True).start()
    run_bot()
