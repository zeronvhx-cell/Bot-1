from flask import Flask
import threading
import time
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# --- FLASK KEEP-ALIVE ---
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

# --- BOT AYARLARI ---
TOKEN = '8945132306:AAFfGAeOZ5P1ALiqeOY8yL14HfAB98Le1VE' 
ADMIN_ID = 697237088
PANEL_PASSWORD = "12149441286Aa."

bot = telebot.TeleBot(TOKEN)

# --- VERİTABANI VE OTURUM YÖNETİMİ ---
categories_db = ["PUBG [IOS]", "APP PLATFORM", "Apple Certificates", "PUBG [Android]", "PUBG Aimbot", "Oxide", "8BALL [POOL]", "Mobile Legends"]
admin_sessions = {} 
waiting_for_password = []

ADMIN_SESSION_TIMEOUT = 10800 # 3 Saat (saniye cinsinden)

def is_admin_logged_in(user_id):
    if user_id != ADMIN_ID:
        return False
    if user_id in admin_sessions:
        if time.time() - admin_sessions[user_id] > ADMIN_SESSION_TIMEOUT:
            del admin_sessions[user_id]
            return False
        return True
    return False

# --- KLAVYELER ---
def get_main_keyboard(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn_buy = KeyboardButton("🛍 Buy keys / Anahtar Al")
    btn_account = KeyboardButton("👤 Account / Hesap")
    btn_support = KeyboardButton("🎧 Support / Destek")
    
    markup.add(btn_buy, btn_account)
    markup.add(btn_support)

    # Sadece admin kişisine özel buton mantığı
    if user_id == ADMIN_ID:
        if is_admin_logged_in(user_id):
            markup.add(KeyboardButton("🔒 Admin panel"), KeyboardButton("🚪 Çıkış Yap"))
        else:
            markup.add(KeyboardButton("🔑 Admin Giriş"))
            
    return markup

# --- MESAJ YÖNETİCİSİ ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    text = "Hoş geldin! Lütfen aşağıdaki menüyü kullanın."
    bot.send_message(message.chat.id, text, reply_markup=get_main_keyboard(user_id))

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    text = message.text

    # Şifre girme aşaması
    if user_id in waiting_for_password:
        waiting_for_password.remove(user_id)
        if text == PANEL_PASSWORD:
            admin_sessions[user_id] = time.time()
            bot.send_message(message.chat.id, "✅ Başarıyla Admin Paneline giriş yaptınız!\n(Oturumunuz 3 saat sonra otomatik kapatılacaktır.)", reply_markup=get_main_keyboard(user_id))
        else:
            bot.send_message(message.chat.id, "❌ Hatalı şifre!", reply_markup=get_main_keyboard(user_id))
        return

    if text == "🔑 Admin Giriş":
        if user_id == ADMIN_ID:
            waiting_for_password.append(user_id)
            bot.send_message(message.chat.id, "🔐 Lütfen admin panel şifresini girin:")
        else:
            bot.send_message(message.chat.id, "Bu komut sadece admin içindir.")

    elif text == "🚪 Çıkış Yap":
        if user_id in admin_sessions:
            del admin_sessions[user_id]
        bot.send_message(message.chat.id, "🔒 Hesaptan / Admin panelinden çıkış yapıldı.", reply_markup=get_main_keyboard(user_id))

    elif text == "🛍 Buy keys / Anahtar Al":
        cat_text = "🛍 **Katalog / Anahtar Al:**\nMevcut Kategoriler:\n" + "\n".join([f"• {cat}" for cat in categories_db])
        bot.send_message(message.chat.id, cat_text, reply_markup=get_main_keyboard(user_id))

    elif text == "👤 Account / Hesap":
        bot.send_message(message.chat.id, "👤 **Hesap Yönetimi** (Ödeme yöntemleri, geçmiş vb.)", reply_markup=get_main_keyboard(user_id))

    elif text == "🎧 Support / Destek":
        bot.send_message(message.chat.id, "🎧 Destek için lütfen yetkiliyle iletişime geçin.", reply_markup=get_main_keyboard(user_id))

    elif text == "🔒 Admin panel":
        if is_admin_logged_in(user_id):
            bot.send_message(message.chat.id, "👑 **Admin Paneline Hoş Geldiniz.**\nBuradan yönetim işlemlerini yapabilirsiniz.", reply_markup=get_main_keyboard(user_id))
        else:
            bot.send_message(message.chat.id, "Oturum süreniz dolmuş. Lütfen tekrar giriş yapın.", reply_markup=get_main_keyboard(user_id))

print("Bot çalışıyor...")
bot.infinity_polling()
