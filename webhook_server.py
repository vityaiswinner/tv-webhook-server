from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Тут ми дістаємо значення з середовища, а не передаємо сам токен!
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

@app.route('/webhook', methods=['POST'])  # 🔥 важливо: саме /webhook
def webhook():
    data = request.json
    message = f"📩 Сигнал з TradingView:\n{data}"

    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }

    requests.post(telegram_url, json=payload)
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
