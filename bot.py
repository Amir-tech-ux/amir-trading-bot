import os
import requests
from flask import Flask, request, jsonify

app =3D Flask(__name__)

# --- ENV ---
TOKEN =3D os.getenv("TOKEN")  # =D7=94=D7=98=D7=95=D7=A7=D7=9F =D7=9E-BotFa=
ther (=D7=9C=D7=94=D7=9B=D7=A0=D7=99=D7=A1 =D7=91-Render >
Environment)
API =3D f"https://api.telegram.org/bot{TOKEN}/"

# --- Helpers ---
def send_text(chat_id: str, text: str):
    if not TOKEN:
        return {"ok": False, "error": "TOKEN is missing"}
    try:
        r =3D requests.post(
            API + "sendMessage",
            data=3D{"chat_id": chat_id, "text": text},
            timeout=3D10
        )
        return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

# --- Routes ---
@app.get("/")
def home():
    return "Bot is running =E2=9C=85"

@app.post("/webhook")
def webhook():
    if not TOKEN:
        return {"ok": False, "error": "TOKEN is missing"}, 400

    update =3D request.get_json(silent=3DTrue) or {}

    msg =3D update.get("message") or update.get("edited_message")
    if msg and "text" in msg:
        chat_id =3D msg["chat"]["id"]
        text =3D msg["text"].strip()

        if text.lower() in ("/start", "start"):
            send_text(chat_id, "=D7=94=D7=91=D7=95=D7=98 =D7=9E=D7=97=D7=95=
=D7=91=D7=A8! =E2=9C=85 =D7=A9=D7=9C=D7=97 =D7=94=D7=95=D7=93=D7=A2=D7=94 =
=D7=9C=D7=91=D7=93=D7=99=D7=A7=D7=94")
        else:
            send_text(chat_id, f"=D7=90=D7=9E=D7=A8=D7=AA: {text}")
        return {"ok": True}, 200

    return {"ok": True}, 200


if __name__ =3D=3D "__main__":
    app.run(host=3D"0.0.0.0", port=3Dint(os.getenv("PORT", 5000)))
