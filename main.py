import os
import telebot
from telebot import types
from flask import Flask
import threading
from datetime import datetime
import random

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
pending_users = set()
preview_data = {}
total_fess_sent = 0

# ─── TEXTS ────────────────────────────────────────────────
TEXTS = {
    "id": {
        "welcome": "Halo! Selamat datang di *Muncorner Bot* 💚\n\nPilih bahasa kamu:\n_Choose your language:_",
        "menu": "Hai, *{name}*! 👋\n\nApa yang mau kamu lakukan hari ini?",
        "send_guide": "📝 *Panduan Kirim Menfess*\n\nKetik pesan kamu atau kirim foto dengan caption.\n\n_Maks. 4000 karakter · 5 menfess/hari_",
        "preview": "👀 *Preview menfess kamu:*\n\n💚 {text}\n\n_Sudah yakin? Menfess akan dikirim ke channel._",
        "sent": "✅ Menfess kamu berhasil terkirim!\n\n[Lihat Menfess]({link})",
        "quota": "❌ Kamu sudah mencapai batas *5 menfess* hari ini. Coba lagi besok ya!",
        "too_long": "❌ Pesan terlalu panjang! Maksimal 4000 karakter.",
        "bad_word": "❌ Pesan mengandung kata yang tidak diperbolehkan.",
        "cancelled": "❌ Dibatalkan.",
        "pick_delete": "🗑 Pilih menfess yang mau dihapus:",
        "no_fess": "Kamu belum pernah kirim menfess.",
        "confirm_delete": "⚠️ Yakin hapus *Fess #{num}*?\n\n_{preview}_\n\nPesan akan dihapus dari channel.",
        "deleted": "✅ Fess berhasil dihapus dari channel.",
        "delete_fail": "❌ Gagal hapus. Mungkin sudah terlalu lama.",
        "stats_title": "📊 *Statistik MunCorner*",
        "stats_total": "📨 Total menfess",
        "stats_senders": "👥 Total pengirim",
        "rank_label": "🏆 Posisi kamu di leaderboard",
        "you_label": "KAMU",
        "you_pronoun": "kamu",
        "leaderboard_empty": "_Kamu belum ada di leaderboard. Kirim menfess dulu!_",
        "profile_title": "👤 *Profil Saya*",
        "profile_username": "👤 Username",
        "profile_id": "🆔 ID",
        "profile_joined": "📅 Bergabung",
        "profile_total": "📨 Total menfess",
        "profile_quota": "⏳ Kuota hari ini",
        "profile_ranking": "🏆 Ranking",
        "profile_badge": "🎖 Badge",
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
        "btn_back": "« Kembali ke Menu",
        "btn_send_confirm": "✅ Kirim",
        "btn_cancel": "✖ Batal",
        "btn_yes_delete": "🗑 Ya, Hapus",
        "btn_yes_del_account": "🗑 Ya, Hapus",
        "btn_lang": "🌐 Bahasa",
        "btn_notif": "🔔 Notifikasi",
        "btn_del_account": "🗑 Hapus Data Akun",
        "no_username": "tidak ada username",
    },
    "en": {
        "welcome": "Hello! Welcome to *Muncorner Bot* 💚\n\nChoose your language:\n_Pilih bahasa kamu:_",
        "menu": "Hey, *{name}*! 👋\n\nWhat would you like to do today?",
        "send_guide": "📝 *How to Send a Menfess*\n\nType your message or send a photo with caption.\n\n_Max. 4000 characters · 5 menfess/day_",
        "preview": "👀 *Preview your menfess:*\n\n💚 {text}\n\n_Are you sure? Your menfess will be sent to the channel._",
        "sent": "✅ Your menfess has been sent!\n\n[View Menfess]({link})",
        "quota": "❌ You've reached the *5 menfess* limit for today. Try again tomorrow!",
        "too_long": "❌ Message too long! Maximum 4000 characters.",
        "bad_word": "❌ Message contains prohibited words.",
        "cancelled": "❌ Cancelled.",
        "pick_delete": "🗑 Choose a menfess to delete:",
        "no_fess": "You haven't sent any menfess yet.",
        "confirm_delete": "⚠️ Delete *Fess #{num}*?\n\n_{preview}_\n\nThis will be removed from the channel.",
        "deleted": "✅ Menfess successfully deleted from channel.",
        "delete_fail": "❌ Failed to delete. It may have been too long ago.",
        "stats_title": "📊 *MunCorner Statistics*",
        "stats_total": "📨 Total menfess",
        "stats_senders": "👥 Total senders",
        "rank_label": "🏆 Your leaderboard position",
        "you_label": "YOU",
        "you_pronoun": "you",
        "leaderboard_empty": "_You're not on the leaderboard yet. Send a menfess first!_",
        "profile_title": "👤 *My Profile*",
        "profile_username": "👤 Username",
        "profile_id": "🆔 ID",
        "profile_joined": "📅 Joined",
        "profile_total": "📨 Total menfess",
        "profile_quota": "⏳ Today's quota",
        "profile_ranking": "🏆 Ranking",
        "profile_badge": "🎖 Badge",
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
        "btn_back": "« Back to Menu",
        "btn_send_confirm": "✅ Send",
        "btn_cancel": "✖ Cancel",
        "btn_yes_delete": "🗑 Yes, Delete",
        "btn_yes_del_account": "🗑 Yes, Delete",
        "btn_lang": "🌐 Language",
        "btn_notif": "🔔 Notification",
        "btn_del_account": "🗑 Delete Account Data",
        "no_username": "no username",
    }
}

def t(user_id, key):
    lang = user_lang.get(user_id, "id")
    return TEXTS[lang].get(key, key)

def sensor_username(username):
    if not username:
        return "unknown"
    chars = list(username)
    n = len(chars)
    visible = set(random.sample(range(n), max(1, n // 3)))
    return "".join(c if i in visible else "*" for i, c in enumerate(chars))

def get_leaderboard():
    return sorted(user_total_fess.items(), key=lambda x: x[1], reverse=True)

def get_rank(user_id):
    for i, (uid, _) in enumerate(get_leaderboard()):
        if uid == user_id:
            return i + 1
    return None

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

banned_words = ['anjing', 'bangsat', 'kontol', 'tolol']

def contains_bad_words(text):
    return any(word in text.lower() for word in banned_words)

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
    markup.add(types.InlineKeyboardButton(f"🌐 {t(user_id, 'btn_lang')} — {lang_str}", callback_data="toggle_lang"))
    markup.add(types.InlineKeyboardButton(f"🔔 {t(user_id, 'btn_notif')} — {notif_str}", callback_data="toggle_notif"))
    markup.add(types.InlineKeyboardButton(t(user_id, "btn_del_account"), callback_data="ask_del_account"))
    markup.add(types.InlineKeyboardButton(t(user_id, "btn_back"), callback_data="back_menu"))
    return markup

# ─── HANDLERS ─────────────────────────────────────────────
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id not in user_first_seen:
        user_first_seen[user_id] = datetime.now().strftime("%d %b %Y")
    if user_id not in user_lang:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🇮🇩 Bahasa Indonesia", callback_data="lang_id"))
        markup.add(types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"))
        bot.send_message(user_id, TEXTS["id"]["welcome"], parse_mode="Markdown", reply_markup=markup)
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

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    global total_fess_sent
    user_id = call.from_user.id
    data = call.data

    # ── Language select
    if data in ("lang_id", "lang_en"):
        user_lang[user_id] = "id" if data == "lang_id" else "en"
        name = call.from_user.first_name or "Cornerpeeps"
        bot.edit_message_text(
            t(user_id, "menu").format(name=name),
            call.message.chat.id, call.message.message_id,
            parse_mode="Markdown", reply_markup=main_menu_markup(user_id)
        )

    # ── Back to menu
    elif data == "back_menu":
        name = call.from_user.first_name or "Cornerpeeps"
        bot.edit_message_text(
            t(user_id, "menu").format(name=name),
            call.message.chat.id, call.message.message_id,
            parse_mode="Markdown", reply_markup=main_menu_markup(user_id)
        )

    # ── Send menfess
    elif data == "send_fess":
        if not can_send(user_id):
            bot.answer_callback_query(call.id, t(user_id, "quota"), show_alert=True)
            return
        pending_users.add(user_id)
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
            if pd["type"] == "text":
                msg_sent = bot.send_message(CHANNEL_ID, "💚 " + pd["text"])
                preview = pd["text"]
            else:
                msg_sent = bot.send_photo(CHANNEL_ID, pd["file_id"], caption="💚 " + pd.get("caption", ""))
                preview = f"[foto] {pd.get('caption', '')}"

            total_fess_sent += 1
            user_total_fess[user_id] = user_total_fess.get(user_id, 0) + 1

            if user_id not in user_last_messages:
                user_last_messages[user_id] = []
            user_last_messages[user_id].append((msg_sent.message_id, preview))
            if len(user_last_messages[user_id]) > 3:
                user_last_messages[user_id].pop(0)

            link = f"https://t.me/c/{str(CHANNEL_ID)[4:]}/{msg_sent.message_id}"

            if user_notif.get(user_id, True):
                bot.edit_message_text(
                    t(user_id, "sent").format(link=link),
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

    # ── Stats
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
                    uname = sensor_username(str(pos) + "user")
                    text += f"#{pos} @{uname} ({count})\n"
            text += "```"
        else:
            text += t(user_id, "leaderboard_empty")

        bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                              parse_mode="Markdown", reply_markup=back_markup(user_id))

    # ── Delete fess
    elif data == "delete_fess":
        messages = user_last_messages.get(user_id, [])
        if not messages:
            bot.edit_message_text(
                t(user_id, "no_fess"),
                call.message.chat.id, call.message.message_id,
                reply_markup=back_markup(user_id)
            )
            return
        markup = types.InlineKeyboardMarkup()
        for i, (msg_id, preview) in enumerate(messages):
            short = preview[:28] + "..." if len(preview) > 28 else preview
            markup.add(types.InlineKeyboardButton(f"🗑 Fess #{i+1} — {short}", callback_data=f"ask_delete_{msg_id}_{i+1}"))
        markup.add(types.InlineKeyboardButton(t(user_id, "btn_cancel"), callback_data="back_menu"))
        bot.edit_message_text(
            t(user_id, "pick_delete"),
            call.message.chat.id, call.message.message_id,
            reply_markup=markup
        )

    elif data.startswith("ask_delete_"):
        parts = data.split("_")
        msg_id = int(parts[2])
        num = parts[3]
        messages = user_last_messages.get(user_id, [])
        preview = next((p for m, p in messages if m == msg_id), "...")
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
                user_last_messages[user_id] = [(m, p) for m, p in user_last_messages[user_id] if m != msg_id]
            bot.edit_message_text(
                t(user_id, "deleted"),
                call.message.chat.id, call.message.message_id,
                reply_markup=back_markup(user_id)
            )
        except Exception:
            bot.edit_message_text(
                t(user_id, "delete_fail"),
                call.message.chat.id, call.message.message_id,
                reply_markup=back_markup(user_id)
            )

    # ── Profile
    elif data == "my_profile":
        uname = call.from_user.username or t(user_id, "no_username")
        first_seen = user_first_seen.get(user_id, "—")
        total = user_total_fess.get(user_id, 0)
        quota = quota_left(user_id)
        rank = get_rank(user_id)
        rank_str = f"#{rank}" if rank else "—"

        if total >= 50:
            badge = "🔥 Top Sender"
        elif total >= 20:
            badge = "⭐ Active Sender"
        elif total >= 5:
            badge = "💚 Regular"
        else:
            badge = "🌱 Newbie"

        text = t(user_id, "profile_title") + "\n\n"
        text += f"{t(user_id, 'profile_username')}: *@{uname}*\n"
        text += f"{t(user_id, 'profile_id')}: `{user_id}`\n"
        text += f"{t(user_id, 'profile_joined')}: *{first_seen}*\n"
        text += f"{t(user_id, 'profile_total')}: *{total}*\n"
        text += f"{t(user_id, 'profile_quota')}: *{quota}/5*\n"
        text += f"{t(user_id, 'profile_ranking')}: *{rank_str}*\n"
        text += f"{t(user_id, 'profile_badge')}: {badge}"

        bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                              parse_mode="Markdown", reply_markup=back_markup(user_id))

    # ── Settings
    elif data == "settings":
        bot.edit_message_text(
            t(user_id, "settings_title"),
            call.message.chat.id, call.message.message_id,
            parse_mode="Markdown", reply_markup=settings_markup(user_id)
        )

    elif data == "toggle_lang":
        current = user_lang.get(user_id, "id")
        user_lang[user_id] = "en" if current == "id" else "id"
        bot.edit_message_text(
            t(user_id, "settings_title"),
            call.message.chat.id, call.message.message_id,
            parse_mode="Markdown", reply_markup=settings_markup(user_id)
        )

    elif data == "toggle_notif":
        user_notif[user_id] = not user_notif.get(user_id, True)
        bot.edit_message_text(
            t(user_id, "settings_title"),
            call.message.chat.id, call.message.message_id,
            parse_mode="Markdown", reply_markup=settings_markup(user_id)
        )

    elif data == "ask_del_account":
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton(t(user_id, "btn_yes_del_account"), callback_data="confirm_del_account"),
            types.InlineKeyboardButton(t(user_id, "btn_cancel"), callback_data="settings")
        )
        bot.edit_message_text(
            t(user_id, "delete_account"),
            call.message.chat.id, call.message.message_id,
            parse_mode="Markdown", reply_markup=markup
        )

    elif data == "confirm_del_account":
        user_lang.pop(user_id, None)
        user_fess_count.pop(user_id, None)
        user_last_messages.pop(user_id, None)
        user_total_fess.pop(user_id, None)
        user_first_seen.pop(user_id, None)
        user_notif.pop(user_id, None)
        pending_users.discard(user_id)
        preview_data.pop(user_id, None)
        bot.edit_message_text(
            t(user_id, "account_deleted_msg"),
            call.message.chat.id, call.message.message_id
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

    if message.content_type == 'text':
        text = message.text.strip()
        if len(text) > 4000:
            bot.reply_to(message, t(user_id, "too_long"))
            return
        if contains_bad_words(text):
            bot.reply_to(message, t(user_id, "bad_word"))
            return
        preview_data[user_id] = {"type": "text", "text": text}
        preview_text = t(user_id, "preview").format(text=text[:200] + ("..." if len(text) > 200 else ""))

    elif message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        caption = message.caption.strip() if message.caption else ""
        if len(caption) > 1024:
            bot.reply_to(message, t(user_id, "too_long"))
            return
        if contains_bad_words(caption):
            bot.reply_to(message, t(user_id, "bad_word"))
            return
        preview_data[user_id] = {"type": "photo", "file_id": file_id, "caption": caption}
        preview_text = t(user_id, "preview").format(text=f"[foto] {caption}" if caption else "[foto]")
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
    run_bot()
