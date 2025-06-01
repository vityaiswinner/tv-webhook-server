from flask import Flask, request
import requests
import hmac
import hashlib
import time
import json

app = Flask(__name__)

# 🔐 BYBIT
BYBIT_API_KEY = "ТВОЙ_API_KEY"
BYBIT_API_SECRET = "ТВОЙ_API_SECRET"

# 📲 TELEGRAM
TELEGRAM_TOKEN = "7994754245:AAFcckYNSTEnZkcaoIPNbcqJULo5GHv5wro"
CHAT_ID = "5369718011"

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': text}
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"Telegram error: {response.text}")
    except Exception as e:
        print(f"Telegram exception: {e}")

def send_signed_request(endpoint, method="POST", params=None):
    if params is None:
        params = {}

    timestamp = str(int(time.time() * 1000))
    method_upper = method.upper()
    # Тіло запиту — без пробілів
    body = json.dumps(params, separators=(',', ':')) if params else ""
    # Підпис складаємо по документації
    payload = timestamp + method_upper + endpoint + "" + body  # queryString пустий

    signature = hmac.new(
        BYBIT_API_SECRET.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    headers = {
        "X-BAPI-API-KEY": BYBIT_API_KEY,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-SIGN": signature,
        "X-BAPI-RECV-WINDOW": "5000",
        "Content-Type": "application/json"
    }

    url = f"https://api.bybit.com{endpoint}"
    response = requests.request(method_upper, url, headers=headers, data=body)
    try:
        return response.json()
    except Exception as e:
        print(f"Bybit response error: {e}, response text: {response.text}")
        return {}

def open_position(side):
    order = {
        "category": "linear",
        "symbol": "ARBUSDT",
        "side": side,
        "orderType": "Market",
        "qty": "10",
        "timeInForce": "GoodTillCancel",
    }
    result = send_signed_request("/v5/order/create", "POST", order)
    print(f"open_position result: {result}")
    return result

def close_all_positions():
    close = {
        "category": "linear",
        "symbol": "ARBUSDT",
        "mode": "BothSide"
    }
    result = send_signed_request("/v5/position/close-pnl", "POST", close)
    print(f"close_all_positions result: {result}")
    return result

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    print(f"Received webhook data: {data}")

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
