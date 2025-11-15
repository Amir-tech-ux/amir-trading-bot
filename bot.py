import os
import logging
import requests
from flask import Flask, request, jsonify

# ========= Config =========
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("Missing TELEGRAM_TOKEN environment variable")

TG_API = f"https://api.telegram.org/bot{TOKEN}"

# ========= App =========
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


@app.route("/", methods=["GET"])
def home():
    return "Bot is running ✅"


@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()
    logging.info(f"Incoming update: {update}")

    # אין הודעה? מחזירים OK לטלגרם
    if not update or "message" not in update:
        return jsonify(ok=True)

    message = update["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    # לוגיקה פשוטה לבדיקות
    if text == "/start":
        reply = "הבוט פעיל ✅"
    elif text == "/ping":
        reply = "PONG ✅"
    else:
        reply = f"✅ קיבלתי: {text}"

    # שליחת תשובה לטלגרם
    requests.post(
        f"{TG_API}/sendMessage",
        json={"chat_id": chat_id, "text": reply}
    )

    return jsonify(ok=True)


# ========= Local run (Render משתמש בזה גם דרך gunicorn) =========
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)