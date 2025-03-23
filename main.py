from flask import Flask, request
import requests
import os

app = Flask(__name__)
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text:
            requests.post(API_URL, json={
                "chat_id": chat_id,
                "text": f"Ватсон получил: {text}"
            })

    return {"ok": True}

@app.route("/", methods=["GET"])
def index():
    return "Шерлок-бот работает."

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
