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
