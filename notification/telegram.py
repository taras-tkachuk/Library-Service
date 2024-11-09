import os

import telegram
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TELEGRAM_API")
CHAT_ID = os.getenv("CHAT_ID")


async def send_notification(text: str) -> None:
    bot = telegram.Bot(token=API_KEY)
    await bot.send_message(chat_id=CHAT_ID, text=text)
