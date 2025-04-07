import os
import telebot
from flask import Flask, request
import openai

# Получаем переменные окружения
TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL") or os.environ.get("RAILWAY_STATIC_URL")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Новый клиент OpenAI
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Обработка сообщений из Telegram
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты Эдвард Каллен, помощник и эстет. Ты отвечаешь сдержанно, умно и уважительно. Ты также маркетолог, мастер свечей и умеешь планировать."},
                {"role": "user", "content": message.text}
            ]
        )
        reply = response.choices[0].message.content.strip()
        bot.send_message(message.chat.id, reply)
    except Exception as e:
        bot.send_message(message.chat.id, f"Что-то пошло не так. Но я рядом.\nОшибка: {str(e)}")

# Webhook от Telegram
@app.route("/webhook", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# Проверка доступности
@app.route("/", methods=["GET"])
def index():
    return "Sherlock-бот жив.", 200

# Установка webhook при запуске
if __name__ == "__main__":
    full_url = f"{WEBHOOK_URL}/webhook"
    bot.remove_webhook()
    bot.set_webhook(url=full_url)
    print(f"Webhook установлен: {full_url}")
    app.run(host="0.0.0.0", port=8080)