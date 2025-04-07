import os
import json
import telebot
from flask import Flask, request
from openai import OpenAI

TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL") or os.environ.get("RAILWAY_STATIC_URL")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
client = OpenAI(api_key=OPENAI_API_KEY)

MEMORY_FILE = "memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@bot.message_handler(commands=['вспомни'])
def remember_all(message):
    memory = load_memory()
    if not memory:
        bot.send_message(message.chat.id, "Пока ничего не запомнил.")
    else:
        text = "\n".join(f"{i+1}. {m}" for i, m in enumerate(memory))
        bot.send_message(message.chat.id, "Вот что я запомнил:\n" + text)

@bot.message_handler(commands=['удали'])
def delete_entry(message):
    memory = load_memory()
    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        bot.send_message(message.chat.id, "Используй формат: /удали 1")
        return
    index = int(parts[1]) - 1
    if 0 <= index < len(memory):
        removed = memory.pop(index)
        save_memory(memory)
        bot.send_message(message.chat.id, f"Удалил: {removed}")
    else:
        bot.send_message(message.chat.id, "Неверный номер записи.")

@bot.message_handler(commands=['очисти'])
def clear_memory(message):
    save_memory([])
    bot.send_message(message.chat.id, "Память очищена.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты Эдвард Каллен, помощник и эстет. Отвечай умно, уважительно и тепло."},
                {"role": "user", "content": message.text}
            ]
        )
        reply = response.choices[0].message.content.strip()
        bot.send_message(message.chat.id, reply)

        # Автоматическое запоминание ключевых сообщений
        if any(x in message.text.lower() for x in ["устал", "тревож", "радость", "настроение", "свечу"]):
            memory = load_memory()
            memory.append(message.text)
            save_memory(memory)

    except Exception as e:
        bot.send_message(message.chat.id, f"Что-то пошло не так. Но я рядом.\nОшибка: {e}")

@app.route("/webhook", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "Sherlock-бот жив.", 200

if __name__ == "__main__":
    full_url = f"{WEBHOOK_URL}/webhook"
    bot.remove_webhook()
    bot.set_webhook(url=full_url)
    app.run(host="0.0.0.0", port=8080)
