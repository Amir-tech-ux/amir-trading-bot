import os


import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- ENV (ברנדר) ---
TOKEN = os.getenv("TOKEN")  # שמור את הטוקן כ־Environment Variable
API = f"https://api.telegram.org/bot{TOKEN}/"

# --- Helpers ---
def send_text(chat_id: str, text: str):
    if not TOKEN:
        return {"ok": False, "error": "TOKEN is missing"}
    try:
        r = requests.post(
            API + "sendMessage",
            data={"chat_id": chat_id, "text": text},
            timeout=10
        )
        return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

# --- Routes ---
@app.get("/")
def home():
    return "Bot is running ✅"

@app.post("/webhook")
def webhook():
    if not TOKEN:
        return {"ok": False, "error": "TOKEN is missing"}, 400

    update = request.get_json(silent=True) or {}

    # הודעת טקסט רגילה
    msg = update.get("message") or update.get("edited_message")
    if msg and "text" in msg:
        chat_id = msg["chat"]["id"]
        text = msg["text"].strip()

        if text.lower() in ("/start", "start"):
            send_text(chat_id, "הבוט מחובר! ✅ שלח הודעה לבדיקה.")
        else:
            send_text(chat_id, f"אמרת: {text}")

        return {"ok": True}, 200

    # Callback של כפתורים
    cq = update.get("callback_query")
    if cq:
        chat_id = cq["message"]["chat"]["id"]
        data = cq.get("data", "")
        send_text(chat_id, f"נלחץ: {data}")
        return {"ok": True}, 200

    return {"ok": True}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
