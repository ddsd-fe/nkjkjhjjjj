import telebot
from telebot import types
import json
import os
from datetime import datetime

# ⚠️ ТВОЙ ТОКЕН ОТ BOTFATHER
TOKEN = '1234567890:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw'

# ⚠️ ТВОЙ USERNAME (для админки)
ADMIN_USERNAME = 'DUROVPSP'  # без @

bot = telebot.TeleBot(TOKEN)

# ========== ФАЙЛ ДЛЯ ХРАНЕНИЯ ДАННЫХ ==========
DATA_FILE = 'users.json'

def load_users():
    """Загружает список пользователей из файла"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Сохраняет пользователей в файл"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# ========== КОМАНДА СТАРТ ==========
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🔗 Привязать аккаунт"))
    markup.add(types.KeyboardButton("💰 Мой баланс"))
    
    bot.send_message(
        message.chat.id,
        "👋 **Добро пожаловать в Boomer Admin!**\n\n"
        "Привяжи свой аккаунт, чтобы получать звёзды.",
        reply_markup=markup,
        parse_mode='Markdown'
    )

# ========== ПРИВЯЗКА АККАУНТА ==========
@bot.message_handler(func=lambda message: message.text == "🔗 Привязать аккаунт")
def link_account(message):
    msg = bot.send_message(
        message.chat.id,
        "📝 **Введи свой логин из игры:**\n"
        "(например: yanchik_777)",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(msg, process_link)

def process_link(message):
    login = message.text.strip()
    telegram_id = str(message.from_user.id)
    telegram_username = message.from_user.username or "Нет username"
    
    users = load_users()
    
    # Проверяем, не занят ли логин
    for uid, data in users.items():
        if data.get('login') == login:
            bot.send_message(
                message.chat.id,
                f"❌ Логин **{login}** уже привязан к другому аккаунту!",
                parse_mode='Markdown'
            )
            return
    
    # Сохраняем пользователя
    users[telegram_id] = {
        'login': login,
        'username': telegram_username,
        'stars': 0,
        'registered': datetime.now().isoformat()
    }
    
    save_users(users)
    
    bot.send_message(
        message.chat.id,
        f"✅ **Аккаунт привязан!**\n\n"
        f"👤 Логин: {login}\n"
        f"⭐ Баланс: 0\n\n"
        f"Теперь отправляй NFT администратору @{ADMIN_USERNAME}\n"
        f"Звёзды начислятся автоматически!",
        parse_mode='Markdown'
    )

# ========== ПРОВЕРКА БАЛАНСА ==========
@bot.message_handler(func=lambda message: message.text == "💰 Мой баланс")
def check_balance(message):
    telegram_id = str(message.from_user.id)
    users = load_users()
    
    if telegram_id in users:
        data = users[telegram_id]
        bot.send_message(
            message.chat.id,
            f"💰 **ТВОЙ БАЛАНС**\n\n"
            f"👤 Логин: {data['login']}\n"
            f"⭐ Звёзд: {data['stars']}\n\n"
            f"📅 Зарегистрирован: {data['registered'][:10]}",
            parse_mode='Markdown'
        )
    else:
        bot.send_message(
            message.chat.id,
            "❌ Твой аккаунт не привязан!\n"
            "Нажми **🔗 Привязать аккаунт**",
            parse_mode='Markdown'
        )

# ========== АДМИН-ПАНЕЛЬ ==========
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.username != ADMIN_USERNAME:
        return
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("📊 Статистика"))
    markup.add(types.KeyboardButton("👥 Список пользователей"))
    markup.add(types.KeyboardButton("➕ Начислить звёзды"))
    markup.add(types.KeyboardButton("🔍 Найти по логину"))
    
    bot.send_message(
        message.chat.id,
        "🔧 **АДМИН-ПАНЕЛЬ**\n\n"
        "Выбери действие:",
        reply_markup=markup,
        parse_mode='Markdown'
    )

# ========== СТАТИСТИКА ==========
@bot.message_handler(func=lambda message: message.text == "📊 Статистика")
def admin_stats(message):
    if message.from_user.username != ADMIN_USERNAME:
        return
    
    users = load_users()
    
    total = len(users)
    total_stars = sum(data['stars'] for data in users.values())
    
    bot.send_message(
        message.chat.id,
        f"📊 **СТАТИСТИКА**\n\n"
        f"👥 Всего пользователей: {total}\n"
        f"⭐ Всего звёзд: {total_stars}",
        parse_mode='Markdown'
    )

# ========== СПИСОК ПОЛЬЗОВАТЕЛЕЙ ==========
@bot.message_handler(func=lambda message: message.text == "👥 Список пользователей")
def user_list(message):
    if message.from_user.username != ADMIN_USERNAME:
        return
    
    users = load_users()
    
    if not users:
        bot.send_message(message.chat.id, "📭 Нет пользователей")
        return
    
    text = "👥 **ПОЛЬЗОВАТЕЛИ**\n\n"
    for telegram_id, data in list(users.items())[:10]:
        text += f"• {data['login']} — {data['stars']}⭐\n"
    
    bot.send_message(
        message.chat.id,
        text,
        parse_mode='Markdown'
    )

# ========== НАЧИСЛИТЬ ЗВЁЗДЫ ПО ЛОГИНУ ==========
@bot.message_handler(func=lambda message: message.text == "➕ Начислить звёзды")
def admin_add_stars(message):
    if message.from_user.username != ADMIN_USERNAME:
        return
    
    msg = bot.send_message(
        message.chat.id,
        "👤 **Введи логин пользователя:**",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(msg, process_add_login)

def process_add_login(message):
    login = message.text.strip()
    admin_data['target_login'] = login
    
    msg = bot.send_message(
        message.chat.id,
        f"💰 **Введи сумму для {login}:**",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(msg, process_add_amount)

def process_add_amount(message):
    try:
        amount = int(message.text)
        login = admin_data['target_login']
        
        users = load_users()
        
        # Ищем пользователя по логину
        found = False
        for telegram_id, data in users.items():
            if data['login'] == login:
                users[telegram_id]['stars'] += amount
                found = True
                
                # Отправляем уведомление
                try:
                    bot.send_message(
                        telegram_id,
                        f"💰 **ПОПОЛНЕНИЕ БАЛАНСА!**\n\n"
                        f"➕ Вам начислено **{amount}⭐**\n"
                        f"⭐ Новый баланс: {users[telegram_id]['stars']}⭐",
                        parse_mode='Markdown'
                    )
                except:
                    pass
                
                break
        
        if found:
            save_users(users)
            bot.send_message(
                message.chat.id,
                f"✅ **Готово!**\n\n"
                f"👤 {login}\n"
                f"➕ +{amount}⭐",
                parse_mode='Markdown'
            )
        else:
            bot.send_message(
                message.chat.id,
                f"❌ Пользователь {login} не найден!",
                parse_mode='Markdown'
            )
            
    except ValueError:
        bot.send_message(
            message.chat.id,
            "❌ Ошибка! Введи число!",
            parse_mode='Markdown'
        )

# ========== ПОИСК ПО ЛОГИНУ ==========
@bot.message_handler(func=lambda message: message.text == "🔍 Найти по логину")
def admin_find(message):
    if message.from_user.username != ADMIN_USERNAME:
        return
    
    msg = bot.send_message(
        message.chat.id,
        "🔍 **Введи логин для поиска:**",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(msg, process_find)

def process_find(message):
    login = message.text.strip()
    users = load_users()
    
    found = False
    for telegram_id, data in users.items():
        if data['login'] == login:
            bot.send_message(
                message.chat.id,
                f"👤 **НАЙДЕН ПОЛЬЗОВАТЕЛЬ**\n\n"
                f"📝 Логин: {data['login']}\n"
                f"⭐ Баланс: {data['stars']}\n"
                f"📱 Telegram: @{data['username']}\n"
                f"🆔 ID: {telegram_id}",
                parse_mode='Markdown'
            )
            found = True
            break
    
    if not found:
        bot.send_message(
            message.chat.id,
            f"❌ Пользователь {login} не найден!",
            parse_mode='Markdown'
        )

# ========== АВТОМАТИЧЕСКОЕ НАЧИСЛЕНИЕ ПРИ ПЕРЕСЫЛКЕ ==========
@bot.message_handler(func=lambda message: message.forward_from is not None)
def handle_forward(message):
    if message.from_user.username != ADMIN_USERNAME:
        return
    
    # Получаем ID отправителя пересланного сообщения
    sender_id = str(message.forward_from.id)
    
    users = load_users()
    
    if sender_id in users:
        # Начисляем 500 звёзд
        users[sender_id]['stars'] += 500
        
        # Отправляем подтверждение админу
        bot.send_message(
            message.chat.id,
            f"✅ **Звёзды начислены!**\n\n"
            f"👤 Пользователь: {users[sender_id]['login']}\n"
            f"➕ +500⭐\n"
            f"⭐ Новый баланс: {users[sender_id]['stars']}⭐",
            parse_mode='Markdown'
        )
        
        # Уведомляем пользователя
        try:
            bot.send_message(
                sender_id,
                f"💰 **ПОПОЛНЕНИЕ БАЛАНСА!**\n\n"
                f"➕ Вам начислено **500⭐**\n"
                f"⭐ Новый баланс: {users[sender_id]['stars']}⭐",
                parse_mode='Markdown'
            )
        except:
            pass
        
        save_users(users)
        
    else:
        bot.send_message(
            message.chat.id,
            f"❌ Пользователь с ID {sender_id} не привязан!\n\n"
            f"Попроси его сначала нажать /start и привязать аккаунт.",
            parse_mode='Markdown'
        )

# ========== ЗАПУСК ==========
print("=" * 50)
print("✅ БОТ ЗАПУЩЕН!")
print("=" * 50)
print(f"🤖 Бот: @{bot.get_me().username}")
print(f"👑 Админ: @{ADMIN_USERNAME}")
print("📁 Данные хранятся в users.json")
print("=" * 50)

import time
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(5)