from flask import Flask
import threading

app = Flask('')

@app.route('/')
def home():
    return "Bot aktif ve çalışıyor!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

keep_alive()

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# --- AYARLAR ---
TOKEN = '8945132306:AAGp5QgZoICOpTSK9ixZebZtV6m_6pRLNjk'  # Verdiğin gerçek token
ADMIN_ID = 6972370888  # Senin Telegram ID'n (Tek Admin)
PANEL_PASSWORD = "123"  # Admin şifresi

bot = telebot.TeleBot(TOKEN)

# Bellek içi veritabanı yapıları (Demo ve yönetim için)
users_db = {"Ensar1234567:0.00$": 0.0, "emrebaba:0.00$": 0.0, "Wortex:0.00$": 0.0, "Saher:0.00$": 0.0, "GHOSTPP1:0.40$": 0.40}
categories_db = ["PUBG [IOS]", "APP PLATFORM", "Apple Certificates", "PUBG [Android]", "PUBG Aimbot", "Oxide", "8BALL [POOL]", "Mobile Legends", "DELTA FORCE", "CALL OF DUTY", "FreeFire", "EMULATOR", "VALORANT"]
products_db = {"PUBG [IOS]": ["Oasis IOS", "KING MODS [IOS]", "LION IOS", "STAR IOS", "CLOUD IOS", "VN-HAX", "DOLPHIN"]}
key_types_db = {"KING MODS [IOS]": [("30Days", 15.0, 0, 1), ("7Days", 6.0, 5, 0), ("1Days", 1.2, 10, 2)]}

waiting_for_password = []
creating_user_step = {}  # {user_id: {"step": "username/password", "username": "..."}}

# --- ANA MENÜ ---
def get_main_keyboard(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_buy = KeyboardButton("🛍 Buy keys / Anahtar Al")
    btn_account = KeyboardButton("👤 Account / Hesap")
    btn_support = KeyboardButton("🎧 Support / Destek")
    
    markup.add(btn_buy)
    markup.add(btn_account, btn_support)
    
    if user_id == ADMIN_ID:
        btn_admin = KeyboardButton("🛡 Admin panel")
        markup.add(btn_admin)
    else:
        btn_logout = KeyboardButton("🚪 Çıkış Yap")
        markup.add(btn_logout)
        
    return markup

# --- ADMIN PANEL ANA MENÜ ---
def get_admin_panel_markup():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("👥 Users", callback_data="admin_users"),
        InlineKeyboardButton("📁 Catalog", callback_data="admin_catalog"),
        InlineKeyboardButton("🎁 Promocodes", callback_data="admin_promos"),
        InlineKeyboardButton("💳 Payment methods", callback_data="admin_payments"),
        InlineKeyboardButton("📋 Receipts", callback_data="admin_receipts"),
        InlineKeyboardButton("📊 Statistics", callback_data="admin_stats"),
        InlineKeyboardButton("📢 Announcement", callback_data="admin_announcement"),
        InlineKeyboardButton("💰 My balance", callback_data="admin_balance")
    )
    markup.add(InlineKeyboardButton("🔒 Lock panel", callback_data="admin_lock"))
    return markup

# --- KULLANICILAR / BAYİLER MENÜSÜ ---
def get_users_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    for u in users_db.keys():
        markup.add(InlineKeyboardButton(f"👤 {u}", callback_data=f"user_detail_{u}"))
    markup.add(InlineKeyboardButton("➕ Create user", callback_data="admin_create_user"))
    markup.add(
        InlineKeyboardButton("⬅️ Previous", callback_data="prev_page"),
        InlineKeyboardButton("Page 1 of 3", callback_data="page_info"),
        InlineKeyboardButton("Next ➡️", callback_data="next_page")
    )
    markup.add(InlineKeyboardButton("🔙 Go back", callback_data="back_to_admin"))
    return markup

# --- KATALOG MENÜSÜ ---
def get_catalog_menu():
    markup = InlineKeyboardMarkup(row_width=3)
    for cat in categories_db[:8]:
        markup.add(
            InlineKeyboardButton(cat, callback_data=f"cat_select_{cat}"),
            InlineKeyboardButton("⬆️ Up", callback_data=f"cat_up_{cat}"),
            InlineKeyboardButton("⬇️ Down", callback_data=f"cat_down_{cat}")
        )
    markup.add(InlineKeyboardButton("➕ Add category", callback_data="admin_add_cat"))
    markup.add(InlineKeyboardButton("🔙 Go back", callback_data="back_to_admin"))
    return markup

# --- MESAJ YÖNETİCİSİ ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, "Hoş geldin! Lütfen aşağıdaki menüyü kullanın.", reply_markup=get_main_keyboard(user_id))

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    text = message.text

    # Admin Paneli Tetikleme (Şifre İsteme Ekranı)
    if text == "🛡 Admin panel" and user_id == ADMIN_ID:
        waiting_for_password.append(user_id)
        cancel_markup = InlineKeyboardMarkup().add(InlineKeyboardButton("❌ Cancel", callback_data="cancel_admin"))
        bot.send_message(
            message.chat.id, 
            "🛡 **Admin panel**\n\nSend the panel password to continue.", 
            parse_mode="Markdown", 
            reply_markup=cancel_markup
        )
        return

    # Şifre Kontrolü
    if user_id in waiting_for_password:
        if text == PANEL_PASSWORD:
            waiting_for_password.remove(user_id)
            bot.send_message(
                message.chat.id, 
                "👑 **Admin panel unlocked**\n- Admin: Zeron (6972370888)", 
                parse_mode="Markdown", 
                reply_markup=get_admin_panel_markup()
            )
        else:
            waiting_for_password.remove(user_id)
            bot.send_message(message.chat.id, "❌ Hatalı şifre!")
        return

    # Yeni Kullanıcı Oluşturma Adımları (Önce Username, Sonra Password)
    if user_id in creating_user_step:
        state = creating_user_step[user_id]
        if state["step"] == "waiting_username":
            state["username"] = text
            state["step"] = "waiting_password"
            bot.send_message(message.chat.id, f"🔑 Kullanıcı adı alındı: `{text}`\nŞimdi bu kullanıcı için **şifre** gönderin:", parse_mode="Markdown")
            return
        elif state["step"] == "waiting_password":
            password = text
            username = state["username"]
            users_db[f"{username} - 0.00$"] = 0.0
            del creating_user_step[user_id]
            bot.send_message(message.chat.id, f"✅ Başarıyla oluşturuldu!\nKullanıcı: `{username}`\nŞifre: `{password}`", parse_mode="Markdown", reply_markup=get_admin_panel_markup())
            return

    # Normal Menü Butonları
    if "Buy keys" in text or "Anahtar Al" in text:
        bot.send_message(message.chat.id, "🛍 **Katalog / Anahtar Al:**\nKategoriler yükleniyor...", reply_markup=get_catalog_menu())
    elif "Account" in text or "Hesap" in text:
        bot.send_message(message.chat.id, "👤 **Hesap Yönetimi** (Ödeme yöntemleri, geçmiş vb.)")
    elif "Support" in text or "Destek" in text:
        bot.send_message(message.chat.id, "🎧 Destek için resmi destek botumuz: `@DestekBotKullaniciAdi`", parse_mode="Markdown")
    elif "Çıkış Yap" in text:
        bot.send_message(message.chat.id, "Hesaptan çıkış yapıldı.", reply_markup=get_main_keyboard(user_id))

# --- CALLBACK YÖNETİMİ ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    data = call.data

    if data == "cancel_admin":
        if user_id in waiting_for_password:
            waiting_for_password.remove(user_id)
        bot.answer_callback_query(call.id, "İptal edildi.")
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass

    elif data == "admin_users":
        bot.answer_callback_query(call.id)
        bot.edit_message_text("Total: 14\n\nBayi/Kullanıcı yönetimi:", call.message.chat.id, call.message.message_id, reply_markup=get_users_menu())

    elif data == "admin_create_user":
        bot.answer_callback_query(call.id)
        creating_user_step[user_id] = {"step": "waiting_username"}
        bot.send_message(call.message.chat.id, "👤 Yeni bayi/kullanıcı için **kullanıcı adı** gönderin:")

    elif data == "admin_catalog":
        bot.answer_callback_query(call.id)
        bot.edit_message_text("📁 **Catalog**\nCategories: 15", call.message.chat.id, call.message.message_id, reply_markup=get_catalog_menu())

    elif data.startswith("cat_select_"):
        cat_name = data.replace("cat_select_", "")
        bot.answer_callback_query(call.id)
        markup = InlineKeyboardMarkup(row_width=3)
        if cat_name in products_db:
            for prod in products_db[cat_name]:
                markup.add(
                    InlineKeyboardButton(prod, callback_data=f"prod_select_{prod}"),
                    InlineKeyboardButton("⬆️ Up", callback_data=f"prod_up_{prod}"),
                    InlineKeyboardButton("⬇️ Down", callback_data=f"prod_down_{prod}")
                )
        markup.add(InlineKeyboardButton("🔙 Go back", callback_data="admin_catalog"))
        bot.edit_message_text(f"📋 **Category: {cat_name}**\nStatus: active\nProducts: {len(products_db.get(cat_name, []))}", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif data.startswith("prod_select_"):
        prod_name = data.replace("prod_select_", "")
        bot.answer_callback_query(call.id)
        markup = InlineKeyboardMarkup(row_width=1)
        if prod_name in key_types_db:
            for kt, pr, stock, sold in key_types_db[prod_name]:
                markup.add(InlineKeyboardButton(f"🏷 {kt} - ${pr:.2f}", callback_data=f"keytype_{prod_name}_{kt}"))
        markup.add(InlineKeyboardButton("➕ Add key type", callback_data=f"add_keytype_{prod_name}"))
        markup.add(
            InlineKeyboardButton("✏️ Rename product", callback_data="noop"),
            InlineKeyboardButton("🟢 active", callback_data="noop")
        )
        markup.add(InlineKeyboardButton("🔙 Go back", callback_data="admin_catalog"))
        bot.edit_message_text(f"- Category: PUBG [IOS]\n- Name: {prod_name}\n- Status: active\n- Key types: {len(key_types_db.get(prod_name, []))}", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif data.startswith("keytype_"):
        bot.answer_callback_query(call.id)
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("📦 Manage stock", callback_data="manage_stock"),
            InlineKeyboardButton("✏️ Rename key type", callback_data="noop"),
            InlineKeyboardButton("💵 Change price", callback_data="noop"),
            InlineKeyboardButton("🟢 active", callback_data="noop"),
            InlineKeyboardButton("🗑 Delete key type", callback_data="noop")
        )
        markup.add(InlineKeyboardButton("🔙 Go back", callback_data="admin_catalog"))
        bot.edit_message_text("🔑 **Key type #4**\n\n- Product: KING MODS [IOS]\n- Name: 30Days\n- Price: 15.00$ ( 1945 ⭐️ )\n- Status: active\n- Available stock: 0\n- Sold: 1", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif data == "back_to_admin":
        bot.answer_callback_query(call.id)
        bot.edit_message_text("👑 **Admin panel unlocked**\n- Admin: Zeron (6972370888)", call.message.chat.id, call.message.message_id, reply_markup=get_admin_panel_markup())

    elif data in ["admin_promos", "admin_payments", "admin_receipts", "admin_stats", "admin_announcement", "admin_balance", "admin_lock"]:
        bot.answer_callback_query(call.id, "Bu bölüm seçildi.")
        if data == "admin_lock":
            bot.edit_message_text("🔒 Admin paneli kilitlendi.", call.message.chat.id, call.message.message_id)

if __name__ == '__main__':
    bot.infinity_polling()
