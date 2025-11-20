import os
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.environ.get("BOT_TOKEN")
DELAY_MINUTES_CONFIRM_SPOT=int(os.environ.get("DELAY_MINUTES_CONFIRM_SPOT"))
GROUP_ID = int(os.environ.get('GROUP_ID'))
LOGS_CHANNEL_ID = int(os.environ.get('LOGS_CHANNEL_ID'))
FEEDBACK_CHANNEL_ID = int(os.environ.get('FEEDBACK_CHANNEL_ID'))

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
