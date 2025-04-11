import os
from flask import Flask, request
import telebot

# Получаем токен из переменной окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)

# Обработка команды /start
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет! Я Шерлок, твой спутник.")

# Простой текстовый ответ
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.send_message(message.chat.id, f"Ты сказал: {message.text}")

# Вебхук: обработка запросов от Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_str = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return '', 200
    else:
        return 'Invalid request', 403

# Проверка работы сервера
@app.route('/', methods=['GET'])
def index():
    return "Бот работает! Шерлок на связи."

# Важно: переменная app должна быть глобальной
if __name__ == '__main__':
    app.run()