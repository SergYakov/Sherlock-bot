import os
import telebot
from flask import Flask, request

# Получаем токен из переменных окружения
TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Обработка входящих сообщений
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.send_message(message.chat.id, "Да, Ватсон!")

# Вебхук для Telegram
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

# Установка вебхука при запуске
if __name__ == "__main__":
    url = os.environ.get("WEBHOOK_URL") or os.environ.get("RAILWAY_STATIC_URL")
    full_url = f"{url}/webhook"
    bot.remove_webhook()
    bot.set_webhook(url=full_url)
    print(f"Webhook установлен на: {full_url}")
    app.run(host="0.0.0.0", port=8080)