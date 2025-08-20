import telebot
from telebot import types
import json
import random
import os

# ======= НАСТРОЙКИ =======
TOKEN = "8083498021:AAGpV8vPTCjto3gsZ16WKviZhzI9bXnQF4M"
ADMIN_ID = 5054256518  # ВСТАВЬ СВОЙ TELEGRAM ID (см. /myid)
CHANNEL_USERNAME = "@mrbrainrot001"  # например "@my_channel"
BOT_USERNAME = "mrbrainrotbot"  # без @, например "MyGiveawayBot"
PARTICIPANTS_FILE = "participants.json"
# файл для сохранения участников
# =========================

bot = telebot.TeleBot(TOKEN)

# Загружаем участников из файла
if os.path.exists(PARTICIPANTS_FILE):
    with open(PARTICIPANTS_FILE, "r") as f:
        participants = json.load(f)
else:
    participants = []

def save_participants():
    with open(PARTICIPANTS_FILE, "w") as f:
        json.dump(participants, f)

# ======= КОМАНДЫ =======

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 Привет! Я бот для проведения розыгрышей.\nНапиши /help, чтобы увидеть все доступные команды.")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    help_text = (
        "📋 Доступные команды:\n\n"
        "/post - Опубликовать пост с кнопкой участия (только админ)\n"
        "/participants - Показать количество участников (только админ)\n"
        "/reset - Очистить список участников (только админ)\n"
        "/raffle - Провести розыгрыш (только админ)\n"
        "/end - Завершить розыгрыш и очистить список (только админ)"
    )
    bot.reply_to(message, help_text)

# ======= КНОПКА "Участвовать" =======
@bot.callback_query_handler(func=lambda call: call.data == "join")
def join_raffle(call):
    user = f"@{call.from_user.username}" if call.from_user.username else call.from_user.first_name
    if user not in participants:
        participants.append(user)
        save_participants()
        bot.answer_callback_query(call.id, "Вы успешно добавлены в список участников! ✅")
    else:
        bot.answer_callback_query(call.id, "Вы уже участвуете в розыгрыше 😉")

# ======= КОМАНДЫ ДЛЯ АДМИНА =======
@bot.message_handler(commands=['post'])
def post(message):
    if message.from_user.id != ADMIN_ID:
        return
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Участвовать", callback_data="join"))
    bot.send_message(CHANNEL_USERNAME, "🎉 Начинается новый розыгрыш!\n\nНажмите кнопку ниже, чтобы участвовать:", reply_markup=markup)

@bot.message_handler(commands=['participants'])
def show_participants(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, f"👥 Участников: {len(participants)}")

@bot.message_handler(commands=['reset'])
def reset(message):
    if message.from_user.id != ADMIN_ID:
        return
    participants.clear()
    save_participants()
    bot.reply_to(message, "Список участников очищен ✅")

@bot.message_handler(commands=['raffle'])
def raffle(message):
    if message.from_user.id != ADMIN_ID:
        return
    if len(participants) < 3:
        bot.reply_to(message, "Недостаточно участников для розыгрыша ❌ (нужно минимум 3)")
        return
    winners = random.sample(participants, 3)
    text = "🎉 Розыгрыш!\n\n🏆 Победители:\n"
    for i, w in enumerate(winners, start=1):
        text += f"{i} место: {w}\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['end'])
def end_raffle(message):
    if message.from_user.id != ADMIN_ID:
        return
    if len(participants) < 3:
        bot.reply_to(message, "Недостаточно участников для завершения розыгрыша ❌")
        return
    winners = random.sample(participants, 3)
    text = "🎉 Розыгрыш завершён!\n\n🏆 Победители:\n"
    for i, w in enumerate(winners, start=1):
        text += f"{i} место: {w}\n"
    bot.send_message(message.chat.id, text)
    participants.clear()
    save_participants()

# ======= ЗАПУСК =======
print("Бот запущен...")
bot.polling(none_stop=True)

