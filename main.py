
from fastapi import FastAPI, Request
import requests
import threading
import time
import sqlite3

app = FastAPI()

TELEGRAM_TOKEN = "8015042778:AAEzZZO5m7oLmfw03Ka7IjQHq-_SX9or0gY"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
WEBHOOK_TOKEN = TELEGRAM_TOKEN  # для сравнения в URL

# 📦 Инициализация SQLite
def init_db():
    conn = sqlite3.connect("rugusa_memory.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            chat_id INTEGER PRIMARY KEY,
            username TEXT,
            last_message TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.post("/webhook/{token}")
async def process_webhook(token: str, request: Request):
    if token != WEBHOOK_TOKEN:
        return {"status": "unauthorized"}

    body = await request.json()
    message = body.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    username = message.get("chat", {}).get("username", "")
    text = message.get("text", "").strip().lower()

    if chat_id and text:
        save_to_memory(chat_id, username, text)

        if text == "как меня зовут?":
            saved = get_from_memory(chat_id)
            if saved:
                name = saved[1] or "незнакомец"
                reply = f"Ты сказал, что тебя зовут {name}."
            else:
                reply = "Я тебя ещё не знаю. Скажи, как тебя зовут!"
        else:
            reply = f"🧠 RUGUSA: Я слышу тебя. Ты сказал: «{text}». Саркжан с тобой."

        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": reply})

    return {"status": "ok"}

# 💾 Сохраняем сообщение в базу
def save_to_memory(chat_id, username, text):
    conn = sqlite3.connect("rugusa_memory.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO memory (chat_id, username, last_message)
        VALUES (?, ?, ?)
        ON CONFLICT(chat_id) DO UPDATE SET
        username = excluded.username,
        last_message = excluded.last_message
    """, (chat_id, username, text))
    conn.commit()
    conn.close()

# 📖 Читаем из памяти
def get_from_memory(chat_id):
    conn = sqlite3.connect("rugusa_memory.db")
    c = conn.cursor()
    c.execute("SELECT * FROM memory WHERE chat_id = ?", (chat_id,))
    result = c.fetchone()
    conn.close()
    return result

# 🔁 Пинг для Render
def keep_alive():
    while True:
        try:
            requests.get("https://rugusa-bot.onrender.com")
        except Exception as e:
            print("Ошибка пинга:", e)
        time.sleep(600)

threading.Thread(target=keep_alive, daemon=True).start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
