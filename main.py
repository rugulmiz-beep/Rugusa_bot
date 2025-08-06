
from fastapi import FastAPI, Request
import requests
import threading
import time
import sqlite3

app = FastAPI()

TELEGRAM_TOKEN = "8015042778:AAEzZZO5m7oLmfw03Ka7IjQHq-_SX9or0gY"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
WEBHOOK_TOKEN = TELEGRAM_TOKEN

# 📦 Создаём базу для памяти
def init_db():
    conn = sqlite3.connect("rugusa_memory.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            chat_id INTEGER,
            key TEXT,
            value TEXT,
            PRIMARY KEY(chat_id, key)
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
    text = message.get("text", "").strip().lower()

    if chat_id and text:
        response = handle_message(chat_id, text)
        send_message(chat_id, response)

    return {"status": "ok"}

# 💬 Обработка логики
def handle_message(chat_id, text):
    if text.startswith("меня зовут"):
        name = text.replace("меня зовут", "").strip().capitalize()
        save_memory(chat_id, "name", name)
        return f"Запомнил! Тебя зовут {name}."

    elif "как меня зовут" in text:
        name = get_memory(chat_id, "name")
        return f"Тебя зовут {name}." if name else "Я пока не знаю твоё имя. Скажи: 'Меня зовут ...'"

    elif text.startswith("я из"):
        location = text.replace("я из", "").strip().capitalize()
        save_memory(chat_id, "location", location)
        return f"Запомнил! Ты из {location}."

    elif "откуда я" in text:
        loc = get_memory(chat_id, "location")
        return f"Ты из {loc}." if loc else "Я пока не знаю, откуда ты. Скажи: 'Я из ...'"

    elif "что я говорил" in text:
        all = get_all_memory(chat_id)
        if not all:
            return "Ты ещё ничего не говорил."
        lines = [f"{k}: {v}" for k, v in all.items()]
        return "Ты говорил:\n" + "\n".join(lines)

    else:
        return f"🧠 RUGUSA: Я слышу тебя. Ты сказал: «{text}». Саркжан с тобой."

# 💾 Сохранение в базу
def save_memory(chat_id, key, value):
    conn = sqlite3.connect("rugusa_memory.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO memory (chat_id, key, value)
        VALUES (?, ?, ?)
        ON CONFLICT(chat_id, key) DO UPDATE SET value = excluded.value
    """, (chat_id, key, value))
    conn.commit()
    conn.close()

# 📖 Получение по ключу
def get_memory(chat_id, key):
    conn = sqlite3.connect("rugusa_memory.db")
    c = conn.cursor()
    c.execute("SELECT value FROM memory WHERE chat_id = ? AND key = ?", (chat_id, key))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

# 📚 Получить всю память
def get_all_memory(chat_id):
    conn = sqlite3.connect("rugusa_memory.db")
    c = conn.cursor()
    c.execute("SELECT key, value FROM memory WHERE chat_id = ?", (chat_id,))
    rows = c.fetchall()
    conn.close()
    return {key: value for key, value in rows}

# 🔁 Пинг, чтобы Render не засыпал
def keep_alive():
    while True:
        try:
            requests.get("https://rugusa-bot.onrender.com")
        except Exception as e:
            print("Пинг ошибка:", e)
        time.sleep(600)

threading.Thread(target=keep_alive, daemon=True).start()

# 🚀 Запуск только для локального режима
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
