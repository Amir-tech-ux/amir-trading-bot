import os
import requests
from flask import Flask, request, jsonify

# ========= הגדרות בסיס =========

TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN env var is missing")

API_URL = f"https://api.telegram.org/bot{TOKEN}"

# אפשרות: לשים פה ID קבוע אחר כך (או דרך env)
DEFAULT_CHAT_ID = int(os.environ.get("ALERT_CHAT_ID", "0"))

app = Flask(__name__)


# ========= פונקציות עזר לטלגרם =========

def send_message(chat_id: int, text: str) -> None:
    """
    שליחת הודעה רגילה לטלגרם
    """
    try:
        requests.post(
            f"{API_URL}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown"
            },
            timeout=10
        )
    except Exception as e:
        print("send_message error:", e)


# ========= Webhook של טלגרם (הבוט הרגיל) =========

@app.post("/")
def telegram_webhook():
    """
    נקודת הכניסה הרגילה לעדכוני טלגרם.
    כאן מגיעים /Ping, /Start וכל שאר ההודעות.
    """
    update = request.get_json(silent=True) or {}

    message = update.get("message") or update.get("edited_message")
    if not message:
        return jsonify({"ok": True})

    chat = message.get("chat", {})
    chat_id = chat.get("id")
    text = message.get("text") or ""

    if not chat_id or not text:
        return jsonify({"ok": True})

    t = text.strip()

    # ---- פקודות בסיס ----
    lower = t.lower()

    if lower.startswith("/ping"):
        send_message(chat_id, "Ping ✅ (מעיין מחובר דרך Render)")
        return jsonify({"ok": True})

    if lower.startswith("/start"):
        msg = (
            "✅ בוט *מעיין* מחובר.\n\n"
            "אתה יכול להשתמש בפקודות:\n"
            "`/ping` – בדיקת חיבור\n"
            "`/help` – סיכום פקודות\n\n"
            "בהמשך נחבר גם סריקות אוטומטיות והתראות ליקווידיטי."
        )
        send_message(chat_id, msg)
        return jsonify({"ok": True})

    if lower.startswith("/help"):
        msg = (
            "*פקודות זמינות כרגע:*\n"
            "`/ping` – בדיקת חיבור\n"
            "`/start` – התחלה\n\n"
            "התראות אוטומטיות יגיעו מהמערכת (TradingView → Render → Telegram) "
            "כאשר יזוהו מצבי ליקווידיטי או נרות מפלצתיים."
        )
        send_message(chat_id, msg)
        return jsonify({"ok": True})

    # טקסט רגיל – בינתיים רק הודעת ברירת מחדל
    send_message(
        chat_id,
        "קיבלתי ✅\nכרגע רוב הפעולה היא בהתראות אוטומטיות, "
        "בהמשך נוסיף גם ניתוחים ישירים מהבוט."
    )
    return jsonify({"ok": True})


# ========= Webhook מיוחד מ-TradingView לליקווידיטי =========

@app.post("/tv-liquidity")
def tv_liquidity():
    """
    Webhook מ-TradingView עבור התראה על Liquidity / נר מפלצתי.
    TradingView שולח JSON, ואנחנו ממירים אותו להתראת פוש בטלגרם.
    """
    data = request.get_json(silent=True) or {}

    # נתונים שיגיעו מ-TradingView (נגדיר שם)
    symbol = data.get("symbol", "NASDAQ")
    timeframe = data.get("timeframe", "H1")
    rsi = data.get("rsi", "45–48")
    macd = data.get("macd", "flattening")
    direction = data.get("direction", "down")  # 'down' או 'up'
    extra = data.get("note", "")

    arrow = "🔻" if direction == "down" else "🔺"

    he_msg = (
        f"🚨 *Liquidity Alert – {symbol}*\n"
        f"רמזור אדום – תיתכן תנועה חזקה תוך 10–20 דקות ({timeframe}).\n"
        f"RSI {rsi}, MACD {macd}, בולינגר נפתח.\n"
        f"{arrow} הכנה לשורט גבוה בלבד (לא להיכנס מהרצפה).\n"
    )
    if extra:
        he_msg += f"\nהערה: {extra}\n"

    en_msg = (
        "\n---\n"
        f"🚨 *Liquidity Alert – {symbol}*\n"
        f"Red light – possible strong move in 10–20 minutes ({timeframe}).\n"
        f"RSI {rsi}, MACD {macd}, Bollinger opening.\n"
        f"{arrow} Prepare for a high-entry short only. Do NOT short at the bottom.\n"
    )

    final_text = he_msg + en_msg

    # לאן שולחים? – עדיף לשים ALERT_CHAT_ID כ-env, ובינתיים fallback:
    chat_id = DEFAULT_CHAT_ID

    if not chat_id:
        # אם לא הוגדר ALERT_CHAT_ID – לא נזרוק שגיאה, רק נדפיס לוג
        print("⚠ ALERT_CHAT_ID is not set – cannot send Telegram alert")
        return jsonify({"ok": False, "error": "ALERT_CHAT_ID missing"})

    send_message(chat_id, final_text)
    return jsonify({"ok": True})


# ========= ברירת מחדל להרצה לוקאלית (לא רלוונטי ל-Render עם gunicorn, אבל לא מזיק) =========

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)