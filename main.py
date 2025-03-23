from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Получаем токен из переменной окружения
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

# Обработка входящих сообщений от Telegram
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text:
            requests.post(API_URL, json={
                "chat_id": chat_id,
                "text": f"Шерлок получил: {text}"
            })

    return "ok"

# Проверка, что бот запущен
@app.route("/", methods=["GET"])
def index():
    return "Шерлок-бот работает."

if __name__ == "__main__":
    app.run(debug=True)

