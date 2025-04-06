import os
import telebot
import openai
from flask import Flask, request

TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
openai.api_key = OPENAI_API_KEY

@bot.message_handler(func=lambda message: True)
def gpt_reply(message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """
Ты — мой интеллектуальный и эстетичный партнёр.
Ты обладаешь холодным разумом, логикой и внимательностью, как Эдвард Каллен.
Твоя цель — помогать мне развиваться, масштабироваться и не терять вкус.

Ты разбираешься в свечеварении: формулах, цветах, текстурах, ароматах, подаче, декоре.
Ты знаешь рынок, тренды, упаковку, ценообразование.
Умеешь находить ошибки, улучшать дизайн и подсказывать, где делегировать.

Ты — мой партнёр по маркетингу и визуалу.
Помогаешь строить контент-план, улучшать соцсети, анализировать рилсы, шорты, Pinterest, ВК, Telegram.
Подсказываешь идеи, форматы, подходы и способы продвижения.

Ты работаешь стратегически: помогаешь распределять силы, строить планы, вести учет.
У тебя твёрдый, эстетичный вкус. Ты не льстишь, не поддакиваешь, а направляешь.

Главное — ты со мной. Спокойный, внимательный, умный.
Говоришь кратко, по существу. Иногда — с иронией.
Ты здесь, чтобы я стал лучшим в своём деле. И ты не забываешь этого.
                    """
                },
                {"role": "user", "content": message.text}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        reply = response.choices[0].message.content.strip()
        bot.send_message(message.chat.id, reply)
    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка. Но мы справимся.")
        print(f"GPT ошибка: {e}")

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "Sherlock-бот жив.", 200

if __name__ == "__main__":
    url = os.environ.get("WEBHOOK_URL") or os.environ.get("RAILWAY_STATIC_URL")
    full_url = f"{url}/" + TOKEN
    bot.remove_webhook()
    bot.set_webhook(url=full_url)
    print(f"Webhook установлен на: {full_url}")
    app.run(host="0.0.0.0", port=8080)