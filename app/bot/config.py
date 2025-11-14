import os
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.environ.get("BOT_TOKEN")
DELAY_MINUTES_CONFIRM_SPOT=int(os.environ.get("DELAY_MINUTES_CONFIRM_SPOT"))
GROUP_ID = int(os.environ.get('GROUP_ID'))
CHANNEL_ID = int(os.environ.get('CHANNEL_ID'))

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
