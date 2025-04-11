import os
import json
from flask import Flask, request
import telebot
from telebot import types
from datetime import datetime

# Flask app
app = Flask(__name__)

# Telegram bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Файлы хранения
HISTORY_FILE = "history.json"
MEMORY_FILE = "memory.json"

# Загрузка/сохранение
def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

history = load_json(HISTORY_FILE)
memory = load_json(MEMORY_FILE)

# Меню с кнопками
def main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("/вспомни", "/дневник", "/очисти", "/совет")
    return keyboard

# Команды
@bot.message_handler(commands=["start"])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я Шерлок 🕵️‍♂️", reply_markup=main_menu())

@bot.message_handler(commands=["вспомни"])
def handle_memory(message):
    user_id = str(message.chat.id)
    notes = memory.get(user_id, [])
    text = "\n".join(f"• {note}" for note in notes) if notes else "Я пока ничего не запомнил 🧠"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=["дневник"])
def handle_history(message):
    user_id = str(message.chat.id)
    logs = history.get(user_id, [])
    text = "\n".join(f"[{item['time']}] {item['text']}" for item in logs) if logs else "Дневник пока пуст 🕰️"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=["очисти"])
def handle_clear(message):
    user_id = str(message.chat.id)
    history[user_id] = []
    memory[user_id] = []
    save_json(HISTORY_FILE, history)
    save_json(MEMORY_FILE, memory)
    bot.send_message(message.chat.id, "Память и дневник очищены 🧽")

@bot.message_handler(commands=["совет"])
def handle_tip(message):
    bot.send_message(message.chat.id, "Поделись, что у тебя на душе — и я постараюсь поддержать.")

# Обработка всех остальных сообщений
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    user_id = str(message.chat.id)
    text = message.text.strip()

    # Память
    memory.setdefault(user_id, []).append(text)
    memory[user_id] = memory[user_id][-20:]
    save_json(MEMORY_FILE, memory)

    # История
    history.setdefault(user_id, []).append({
        "text": text,
        "time": datetime.now().strftime("%d.%m %H:%M")
    })
    history[user_id] = history[user_id][-50:]
    save_json(HISTORY_FILE, history)

    bot.send_message(message.chat.id, "Запомнил 💾")

# Вебхук
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
        bot.process_new_updates([update])
        return '', 200
    return 'Invalid', 403

@app.route('/', methods=['GET'])
def index():
    return "Sherlock bot запущен!"

# Для локального запуска
if __name__ == '__main__':
    app.run()
