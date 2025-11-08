import os
import logging
import requests
from flask import Flask, request, jsonify

# ======== Config ========
TOKEN = os.environ.get("TELEGRAM_TOKEN")
PUBLIC_URL = os.environ.get("PUBLIC_URL")  # למשל https://amir-trading-bot.onrender.com
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "amir-secret")

if not TOKEN:
    raise RuntimeError("Missing TELEGRAM_TOKEN environment variable")

TG_API = f"https://api.telegram.org/bot{TOKEN}"

# ======== App ========
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route(f"/{WEBHOOK_SECRET}", methods=["POST"])
def webhook():
    update = request.get_json()
    logging.info(f"Incoming update: {update}")
    if not update or "message" not in update:
        return jsonify({"ok": True})

    chat_id = update["message"]["chat"]["id"]
    text = update["message"].get("text", "")
    reply = f"✅ קיבלתי: {text}"
    requests.post(f"{TG_API}/sendMessage", json={"chat_id": chat_id, "text": reply})
    return jsonify({"ok": True})

# ======== Startup ========
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))