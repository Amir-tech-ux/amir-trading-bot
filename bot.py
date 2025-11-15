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


# ========= Webhook =========
@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()
    logging.info(f"Incoming update: {update}")

    # אם אין הודעה – לצאת
    if not update or "message" not in update:
        return jsonify({"ok": True})

    chat_id = update["message"]["chat"]["id"]
    text = update["message"].get("text", "")

    # תשובה
    reply = "קיבלתי ✔️: " + text

    # שליחת ההודעה חזרה
    requests.post(
        f"{TG_API}/sendMessage",
        json={"chat_id": chat_id, "text": reply}
    )

    return jsonify({"ok": True})


# ========= Startup =========
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))