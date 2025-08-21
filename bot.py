# bot.py
import os, requests
from flask import Flask, request, jsonify

app = Flask(__name__)

TOKEN   = os.getenv("TOKEN")           # טוקן מה-BotFather (להגדיר ב-Render)
CHAT_ID = os.getenv("CHAT_ID")         # אופציונלי: ה-Chat ID הפרטי שלך
API     = lambda m: f"https://api.telegram.org/bot{TOKEN}/{m}"

# ---------- Helpers ----------
def send_text(chat_id: str, text: str):
    if not TOKEN:
        return {"ok": False, "error": "TOKEN is missing"}
    r = requests.post(API("sendMessage"), data={"chat_id": chat_id, "text": text})
    return r.json()

def updates():
    if not TOKEN:
        return {"ok": False, "error": "TOKEN is missing"}
    return requests.get(API("getUpdates")).json()

def find_chat_ids():
    js = updates()
    found, seen = [], set()
    for u in js.get("result", []):
        msg = u.get("message") or u.get("edited_message") \
              or (u.get("callback_query", {}).get("message") if u.get("callback_query") else None)
        if not msg:
            continue
        chat = msg.get("chat", {})
        cid  = chat.get("id")
        if cid and cid not in seen:
            seen.add(cid)
            found.append({
                "chat_id": cid,
                "first_name": chat.get("first_name"),
                "username": chat.get("username"),
                "title": chat.get("title"),
            })
    return found

def target_chat_id():
    """מעדיף CHAT_ID מהסביבה; אם לא קיים – לוקח את האחרון מ-getUpdates."""
    if CHAT_ID:
        return CHAT_ID
    ids = find_chat_ids()
    return str(ids[-1]["chat_id"]) if ids else None

# ---------- Routes ----------
@app.get("/")
def home():
    return "Maayan bot is running ✅"

@app.get("/whoami")
def whoami():
    """שלח /start לבוט בטלגרם ואז כנס לנתיב הזה לקבלת Chat ID."""
    found = find_chat_ids()
    out = {"found": found}
    if CHAT_ID:
        out
