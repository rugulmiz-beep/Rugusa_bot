from fastapi import FastAPI, Request
import uvicorn
import telegram
import os

TOKEN = os.getenv("BOT_TOKEN")  # 🧪 Берёт токен из переменных среды
bot = telegram.Bot(token=TOKEN)

app = FastAPI()

@app.post("/")
async def handle_webhook(request: Request):
    data = await request.json()
    
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        
        # Команды
        if text == "/start":
            await bot.send_message(chat_id=chat_id, text="👋 Привет! Я RUGUSA. Готов к службе.")
        elif text == "/help":
            await bot.send_message(chat_id=chat_id, text="🛠 Доступные команды:\n/start\n/help\n/info")
        elif text == "/info":
            await bot.send_message(chat_id=chat_id, text="💡 Я — бот RUGUSA, созданный с душой.")
        else:
            await bot.send_message(chat_id=chat_id, text="🔍 Неизвестная команда. Напиши /help.")
    
    return {"ok": True}
from fastapi import FastAPI, Request
import uvicorn
import os

app = FastAPI()

@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    message = data.get("message", {})
    text = message.get("text", "").lower()
    chat_id = message.get("chat", {}).get("id")

    if text in ["/start", "start"]:
        reply = "👋 Привет! Я готов к работе."
    elif text in ["pognali", "поехали"]:
        reply = "🚀 Погнали!"
    elif "погода" in text:
        reply = "☀️ Сейчас хорошая погода. (Пример)"
    else:
        reply = "🤖 Я тебя слышу. Скажи что-нибудь ещё."

    if chat_id:
        send_message(chat_id, reply)

    return {"ok": True}

def send_message(chat_id, text):
    import requests
    token = os.environ.get("TOKEN")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
