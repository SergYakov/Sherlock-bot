import os
import telebot
import openai
from flask import Flask, request
from datetime import datetime, timedelta
import threading

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

user_memories = {}

@bot.message_handler(commands=['вспомни'])
def handle_recall(message):
    chat_id = message.chat.id
    memories = user_memories.get(chat_id, [])
    if not memories:
        bot.reply_to(message, "Пока нет сохранённых воспоминаний.")
    else:
        recall_text = "\n".join([f"{i+1}. {text}" for i, text in enumerate(memories)])
        bot.reply_to(message, f"Ваши воспоминания:\n{recall_text}")

@bot.message_handler(commands=['удали'])
def handle_delete(message):
    chat_id = message.chat.id
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Укажите номер или ключевое слово для удаления.")
        return
    target = args[1]
    memories = user_memories.get(chat_id, [])
    if target.isdigit():
        idx = int(target) - 1
        if 0 <= idx < len(memories):
            removed = memories.pop(idx)
            bot.reply_to(message, f"Удалено: {removed}")
        else:
            bot.reply_to(message, "Неверный номер.")
    else:
        user_memories[chat_id] = [m for m in memories if target not in m]
        bot.reply_to(message, f"Удалены воспоминания, содержащие '{target}'.")

@bot.message_handler(commands=['напомни'])
def handle_reminder(message):
    chat_id = message.chat.id
    text = message.text[9:].strip()
    if not text:
        bot.reply_to(message, "Формат: /напомни 10мин сделать зарядку")
        return

    import re
    match = re.match(r'(\d+)\s*(мин|час)', text)
    if not match:
        bot.reply_to(message, "Не понял формат времени. Пример: /напомни 10мин сделать зарядку")
        return

    num, unit = match.groups()
    num = int(num)
    seconds = num * 60 if unit == 'мин' else num * 3600
    reminder_text = text[match.end():].strip() or "Напоминание!"

    def send_reminder():
        bot.send_message(chat_id, f"Напоминаю: {reminder_text}")

    bot.reply_to(message, f"Напоминание установлено через {num} {unit}.")
    threading.Timer(seconds, send_reminder).start()

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_all_messages(message):
    user_text = message.text
    chat_id = message.chat.id

    for key in ["тревожно", "тревога", "устал", "вдохнов", "лепил свеч"]:
        if key in user_text.lower():
            user_memories.setdefault(chat_id, []).append(user_text)
            break

    bot.send_chat_action(chat_id, 'typing')
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты — виртуальный собеседник 'Шерлок'. Отвечай мудро, как Холмс."},
                {"role": "user", "content": user_text}
            ],
            max_tokens=150
        )
        answer = response['choices'][0]['message']['content']
    except Exception:
        answer = "Извините, произошла ошибка при обращении к AI-сервису."

    bot.reply_to(message, answer)

app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
