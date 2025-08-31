import os
import logging
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("TELEGRAM_TOKEN")
BASE  = f"https://api.telegram.org/bot{TOKEN}"

def send(chat_id: int, text: str):
    try:
        requests.post(f"{BASE}/sendMessage",
                      json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
                      timeout=15)
    except Exception as e:
        app.logger.error(f"send error: {e}")

@app.route("/", methods=["GET"])
def health():
    return "OK", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    msg  = data.get("message") or data.get("edited_message")
    if not msg:
        return jsonify(ok=True)

    chat_id = msg["chat"]["id"]
    text = (msg.get("text") or "").strip()
    low  = text.lower()

    if low.startswith("/start"):
        send(chat_id, "👋 הבוט מחובר דרך Render. פקודות: /status /ping /help /push <טקסט>")
    elif low.startswith("/status"):
        send(chat_id, "✅ פעיל | Webhook OK")
    elif low.startswith("/ping"):
        send(chat_id, "🏓 pong")
    elif low.startswith("/help"):
        send(chat_id, "📖 פקודות:\n/start – התחלה\n/status – מצב\n/ping – בדיקה\n/push <טקסט> – שלח הודעת בדיקה חוזרת")
    elif low.startswith("/push"):
        payload = text[5:].strip() or "בדיקת PUSH"
        send(chat_id, f"📣 PUSH: {payload}")
    else:
        send(chat_id, f"📩 קיבלתי: {text}")

    return jsonify(ok=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
