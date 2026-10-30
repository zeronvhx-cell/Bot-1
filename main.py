import os
import threading
import time
import telebot
from flask import Flask
from telebot.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)

# ==========================================
# 1. FLASK KEEP-ALIVE SUNUCUSU (RENDER İÇİN)
# ==========================================
app = Flask('')

@app.route('/')
def home():
    return "Bot ve Web Sunucusu Aktif!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()

keep_alive()

# ==========================================
# 2. BOT YAPILANDIRMASI VE SABİTLER
# ==========================================
# Token'ını buraya tırnak içinde yazabilirsin
TOKEN = '8945132306:AAGp5QgZoICOpTSK9ixZebZ...' 
ADMIN_ID = 697237088
PANEL_PASSWORD = "12149441286Aa."
ADMIN_SESSION_TIMEOUT = 10800  # 3 Saat (saniye cinsinden)

bot = telebot.TeleBot(TOKEN)

# Oturum ve Durum Hafızası
admin_sessions = {} 
waiting_for_password = set()

# Ürün Veritabanı (Kategori -> Marka -> Süre ve Fiyat)
store_data = {
    "PUBG [IOS]": {
        "Oasis IOS": {"1 Gün": "50 XTR", "7 Gün": "250 XTR", "30 Gün": "700 XTR"},
        "King IOS": {"1 Gün": "60 XTR", "7 Gün": "300 XTR", "30 Gün": "850 XTR"}
    },
    "APP PLATFORM": {
        "Platform VIP": {"30 Gün": "150 XTR"}
    },
    "Apple Certificates": {
        "Developer Cert": {"1 Yıl": "1000 XTR"}
    },
    "PUBG [Android]": {
        "King Mods": {"7 Gün": "200 XTR", "30 Gün": "500 XTR"}
    },
    "PUBG Aimbot": {
        "Pro Aimbot": {"7 Gün": "300 XTR", "30 Gün": "900 XTR"}
    },
    "Oxide": {
        "Oxide Key": {"30 Gün": "450 XTR"}
    },
    "8BALL [POOL]": {
        "Pool Hack": {"7 Gün": "150 XTR", "30 Gün": "400 XTR"}
    },
    "Mobile Legends": {
        "MLBB VIP": {"30 Gün": "400 XTR"}
    }
}

# ==========================================
# 3. YETKİLENDİRME VE KLAVYE FONKSİYONLARI
# ==========================================
def is_admin_logged_in(user_id):
    if user_id != ADMIN_ID:
        return False
    if user_id in admin_sessions:
        if time.time() - admin_sessions[user_id] > ADMIN_SESSION_TIMEOUT:
            del admin_sessions[user_id]
            return False
        return True
    return False

def get_main_keyboard(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn_buy = KeyboardButton("🛍 Buy keys / Anahtar Al")
    btn_account = KeyboardButton("👤 Account / Hesap")
    btn_support = KeyboardButton("🎧 Support / Destek")
    
    markup.add(btn_buy, btn_account)
    markup.add(btn_support)

    if user_id == ADMIN_ID:
        if is_admin_logged_in(user_id):
            markup.add(KeyboardButton("🔒 Admin panel"), KeyboardButton("🚪 Çıkış Yap"))
        else:
            markup.add(KeyboardButton("🔑 Admin Giriş"))
            
    return markup

# ==========================================
# 4. MESAJ VE KOMUT YÖNETİCİLERİ
# ==========================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    text = "Hoş geldin! Lütfen aşağıdaki menüyü kullanın."
    bot.send_message(message.chat.id, text, reply_markup=get_main_keyboard(user_id))

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    text = message.text

    # Şifre Giriş Aşaması
    if user_id in waiting_for_password:
        waiting_for_password.remove(user_id)
        if text == PANEL_PASSWORD:
            admin_sessions[user_id] = time.time()
            bot.send_message(
                message.chat.id, 
                "✅ Başarıyla Admin Paneline giriş yaptınız!\n(Oturumunuz 3 saat sonra otomatik kapatılacaktır.)", 
                reply_markup=get_main_keyboard(user_id)
            )
        else:
            bot.send_message(
                message.chat.id, 
                "❌ Hatalı şifre!", 
                reply_markup=get_main_keyboard(user_id)
            )
        return

    # Ana Menü Butonları
    if text == "🔑 Admin Giriş":
        if user_id == ADMIN_ID:
            waiting_for_password.add(user_id)
            bot.send_message(message.chat.id, "🔐 Lütfen admin panel şifresini girin:")
        else:
            bot.send_message(message.chat.id, "Bu komut sadece admin içindir.")

    elif text == "🚪 Çıkış Yap":
        if user_id in admin_sessions:
            del admin_sessions[user_id]
        bot.send_message(message.chat.id, "🔒 Oturum başarıyla kapatıldı.", reply_markup=get_main_keyboard(user_id))

    elif text == "🛍 Buy keys / Anahtar Al":
        markup = InlineKeyboardMarkup(row_width=2)
        for cat in store_data.keys():
            markup.add(InlineKeyboardButton(text=f"📂 {cat}", callback_data=f"cat_{cat}"))
        bot.send_message(message.chat.id, "🛍 **Katalog / Anahtar Al:**\nLütfen incelemek istediğiniz kategoriyi seçin:", reply_markup=markup)

    elif text == "👤 Account / Hesap":
        bot.send_message(message.chat.id, "👤 **Hesap Yönetimi**\nAktif bir aboneliğiniz veya geçmiş işleminiz bulunmuyor.", reply_markup=get_main_keyboard(user_id))

    elif text == "🎧 Support / Destek":
        bot.send_message(message.chat.id, "🎧 Destek için lütfen yetkili kişiyle iletişime geçin.", reply_markup=get_main_keyboard(user_id))

    elif text == "🔒 Admin panel":
        if is_admin_logged_in(user_id):
            bot.send_message(
                message.chat.id, 
                "👑 **Admin Paneli**\nBuradan ürünleri ve fiyatları yönetebilir, oturumunuzu 3 saat boyunca güvenle kullanabilirsiniz.", 
                reply_markup=get_main_keyboard(user_id)
            )
        else:
            bot.send_message(message.chat.id, "Oturum süreniz dolmuş veya yetkiniz yok. Lütfen tekrar giriş yapın.", reply_markup=get_main_keyboard(user_id))

# ==========================================
# 5. İNLİNE KUTUCUK VE KATALOG GEZİNME SİSTEMİ
# ==========================================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    data = call.data
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    try:
        # Kategori Seçildiğinde -> Markaları Listele
        if data.startswith("cat_"):
            category = data.replace("cat_", "")
            if category in store_data:
                markup = InlineKeyboardMarkup(row_width=1)
                for brand in store_data[category].keys():
                    markup.add(InlineKeyboardButton(text=f"🏷 {brand}", callback_data=f"brand_{category}_{brand}"))
                markup.add(InlineKeyboardButton(text="⬅️ Kategorilere Dön", callback_data="back_to_cats"))
                bot.edit_message_text(
                    chat_id=chat_id, 
                    message_id=message_id, 
                    text=f"📂 **Kategori: {category}**\nLütfen bir marka seçin:", 
                    reply_markup=markup
                )

        # Marka Seçildiğinde -> Süre ve Fiyatları Listele
        elif data.startswith("brand_"):
            parts = data.split("_", 2)
            category = parts[1]
            brand = parts[2]
            if category in store_data and brand in store_data[category]:
                markup = InlineKeyboardMarkup(row_width=1)
                for duration, price in store_data[category][brand].items():
                    markup.add(InlineKeyboardButton(text=f"⏳ {duration} ➔ 💰 {price}", callback_data=f"buy_{brand}_{duration}"))
                markup.add(InlineKeyboardButton(text="⬅️ Geri Dön", callback_data=f"cat_{category}"))
                bot.edit_message_text(
                    chat_id=chat_id, 
                    message_id=message_id, 
                    text=f"🔑 **Marka: {brand}**\nSüre ve Fiyat Seçenekleri:", 
                    reply_markup=markup
                )

        # Geri Dönüş: Kategoriler Listesi
        elif data == "back_to_cats":
            markup = InlineKeyboardMarkup(row_width=2)
            for cat in store_data.keys():
                markup.add(InlineKeyboardButton(text=f"📂 {cat}", callback_data=f"cat_{cat}"))
            bot.edit_message_text(
                chat_id=chat_id, 
                message_id=message_id, 
                text="🛍 **Katalog / Anahtar Al:**\nLütfen incelemek istediğiniz kategoriyi seçin:", 
                reply_markup=markup
            )

        # Satın Alma / XTR Ödeme Tetikleyicisi
        elif data.startswith("buy_"):
            bot.answer_callback_query(
                call.id, 
                text="Telegram Stars (XTR) ile ödeme entegrasyonu başlatılıyor...", 
                show_alert=True
            )

    except Exception as e:
        print(f"Callback Hatası: {e}")

# ==========================================
# 6. BOTU BAŞLAT
# ==========================================
print("Bot başarıyla başlatıldı ve çalışıyor...")
# skip_pending=True ile eski birikmiş çakışma mesajları engellenir
bot.infinity_polling(skip_pending=True)
