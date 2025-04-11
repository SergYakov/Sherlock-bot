from flask import Flask, request
import logging
import os
import json
import openai
from datetime import datetime
from pyrogram import Client
from telebot import TeleBot, types

# Настройки
TOKEN = os.getenv("TELEGRAM_TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")

bot = TeleBot(TOKEN)
app = Flask(__name__)

# Память
HISTORY_FILE = "history.json"
MEMORY_FILE = "memory.json"

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

# Команды
@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["/вспомни", "/дневник", "/очисти", "/напомни", "/совет"]
    for b in buttons:
        keyboard.add(b)
    bot.send_message(message.chat.id, "Привет, я Шерлок 🤖 Готов помочь!", reply_markup=keyboard)

@bot.message_handler(commands=["вспомни"])
def show_memory(message):
    user_id = str(message.chat.id)
    notes = memory.get(user_id, [])
    if notes:
        text = "\n".join(f"• {note}" for note in notes)
    else:
        text = "Я пока ничего не запомнил 🧠"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=["дневник"])
def show_history(message):
    user_id = str(message.chat.id)
    notes = history.get(user_id, [])
    if notes:
        text = "\n".join(f"[{note['time']}] {note['text']}" for note in notes)
    else:
        text = "Дневник пуст 🕰️"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=["очисти"])
def clear_all(message):
    user_id = str(message.chat.id)
    history[user_id] = []
    memory[user_id] = []
    save_json(HISTORY_FILE, history)
    save_json(MEMORY_FILE, memory)
    bot.send_message(message.chat.id, "Очищено. Начнём с чистого листа 🧽")

@bot.message_handler(commands=["напомни"])
def set_reminder(message):
    bot.send_message(message.chat.id, "Напоминания пока работают только вручную ⏰")

@bot.message_handler(commands=["совет"])
def send_tip(message):
    bot.send_message(message.chat.id, "Расскажи, что у тебя на душе, и я постараюсь помочь 🧩")

# Обработка всех остальных сообщений
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    user_id = str(message.chat.id)
    msg = message.text.strip()

    # Сохраняем в память
    memory.setdefault(user_id, []).append(msg)
    if len(memory[user_id]) > 20:
        memory[user_id] = memory[user_id][-20:]
    save_json(MEMORY_FILE, memory)

    # Сохраняем в историю
    history.setdefault(user_id, []).append({
        "text": msg,
        "time": datetime.now().strftime("%d.%m %H:%M")
    })
    if len(history[user_id]) > 50:
        history[user_id] = history[user_id][-50:]
    save_json(HISTORY_FILE, history)

    # Ответ от OpenAI
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Ты тёплый и логичный собеседник. Отвечай с заботой и кратко."},
                      {"role": "user", "content": msg}]
        )
        reply = response["choices"][0]["message"]["content"]
    except Exception as e:
        reply = "Ошибка при запросе. Попробуй ещё раз позже."

    bot.send_message(message.chat.id, reply)

# Flask Webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_string = request.get_data().decode("utf-8")
    update = types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "SherlockAI запущен 🕵️", 200

if __name__ == "__main__":
    app.run(debug=False)