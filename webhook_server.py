from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("7994754245:AAFcckYNSTEnZkcaoIPNbcqJULo5GHv5wro")
CHAT_ID = os.getenv("5369718011")

@app.route('/', methods=['POST'])
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
