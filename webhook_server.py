from flask import Flask, request
import requests
import hmac
import hashlib
import time
import json

app = Flask(__name__)

# 🔐 BYBIT
BYBIT_API_KEY = "ТВОYЙ_API_KE"
BYBIT_API_SECRET = "ТВОЙ_API_SECRET"

# 📲 TELEGRAM
TELEGRAM_TOKEN = "7994754245:AAFcckYNSTEnZkcaoIPNbcqJULo5GHv5wro"
CHAT_ID = "5369718011"

# ⚙️ Функція для надсилання в Telegram
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': text}
    requests.post(url, json=payload)

# ⚙️ Функція запиту до Bybit
def send_signed_request(endpoint, method="POST", params=None):
    if params is None:
        params = {}

    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    payload = f"{timestamp}{BYBIT_API_KEY}{recv_window}{json.dumps(params)}"
    signature = hmac.new(
        bytes(BYBIT_API_SECRET, "utf-8"),
        bytes(payload, "utf-8"),
        hashlib.sha256
    ).hexdigest()

    headers = {
        "X-BAPI-API-KEY": BYBIT_API_KEY,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-SIGN": signature,
        "X-BAPI-RECV-WINDOW": recv_window,
        "Content-Type": "application/json"
    }

    url = f"https://api.bybit.com{endpoint}"
    response = requests.request(method, url, headers=headers, json=params)
    return response.json()

# ⚙️ Відкрити позицію
def open_position(side):
    order = {
        "category": "linear",
        "symbol": "ARBUSDT",
        "side": side,
        "orderType": "Market",
        "qty": "10",  # Сума — заміни на свою
        "timeInForce": "GoodTillCancel",
    }
    return send_signed_request("/v5/order/create", "POST", order)

# ⚙️ Закрити всі відкриті ордери
def close_all_positions():
    close = {
        "category": "linear",
        "symbol": "ARBUSDT",
        "mode": "BothSide"
    }
    return send_signed_request("/v5/position/close-pnl", "POST", close)

# 🎯 WEBHOOK
@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    message = data.get('message', '')

    if "Open Long" in message:
        close_all_positions()
        open_position("Buy")
        send_telegram_message("✅ Відкрито LONG по ARB")

    elif "Close entry(s) order Long Open" in message:
        close_all_positions()
        open_position("Sell")
        send_telegram_message("🔻 LONG закрито, відкрито SHORT по ARB")

    else:
        send_telegram_message(f"📩 Новий сигнал: {message}")

    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
