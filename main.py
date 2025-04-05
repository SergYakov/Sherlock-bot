import os
import telebot
from flask import Flask, request

# Получаем токены из переменных окружения
TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Обработка сообщений
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.send_message(message.chat.id, "Да, Ватсон!")

# Webhook-эндпоинт
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

# Проверка доступности
@app.route('/', methods=['GET'])
def index():
    return 'Sherlock-бог жив.', 200

# Установка webhook
if __name__ == "__main__":
    url = os.environ.get('RAILWAY_STATIC_URL') or os.environ.get('WEBHOOK_URL')  # можно вручную задать
    full_url = f'{url}/{TOKEN}'
    bot.remove_webhook()
    bot.set_webhook(url=full_url)
    print(f'Webhook установлен на: {full_url}')
    app.run(host='0.0.0.0', port=8080)