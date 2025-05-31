from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Справжні токени не вставляй у код напряму!
TELEGRAM_TOKEN = "7994754245:AAFcckYNSTEnZkcaoIPNbcqJULo5GHv5wro"
CHAT_ID = "5369718011"

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    message = data.get("message", "")  # витягуємо текст з {"message": "..."}

    # Надішли сигнал в Telegram
    telegram_msg = f"📩 Сигнал з TradingView:\n{message}"
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(telegram_url, json={
        'chat_id': CHAT_ID,
        'text': telegram_msg
    })

    # Реакція на сигнали
    if "Open Long" in message:
        # Тут логіка відкриття Long
        print("➡️ Відкриваємо ЛОНГ")
    elif "Close entry(s) order Long Open" in message:
        # Тут логіка закриття Long і відкриття Short
        print("⬅️ Закриваємо ЛОНГ, відкриваємо ШОРТ")

    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
