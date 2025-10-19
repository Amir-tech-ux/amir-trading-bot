import os
import logging
import requests
from flask import Flask, request, jsonify

# ========= Config =========
TOKEN = os.environ.get("TELEGRAM_TOKEN")  # הגדר ב-Render
PUBLIC_URL = os.environ.get("PUBLIC_URL")  # אופציונלי: https://amir-trading-bot.onrender.com
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "amir-secret")  # אופציונלי

if not TOKEN:
    raise RuntimeError("Missing TELEGRAM_TOKEN environment variable")

TG_API = f"https://api.telegram.org/bot{TOKEN}"

# ========= App =========
app = Flask(__name__)
logging.basicConfig(level=logging