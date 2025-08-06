from fastapi import FastAPI, Request
import requests

app = FastAPI()

TELEGRAM_TOKEN = "8015042778:AAEzZZO5m7oLmfw03Ka7IjQHq-_SX9or0gY"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

@app.post("/webhook/{token}")
async def process_webhook(token: str, request: Request):
    if token != TELEGRAM_TOKEN:
        return {"status": "unauthorized"}

    body = await request.json()
    message = body.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "").strip()

    if chat_id and text:
        reply = f"🧠 RUGUSA: Я слышу тебя. Ты сказал: «{text}». Саркжан с тобой."
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": reply})

    return {"status": "ok"}
