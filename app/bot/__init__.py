import os

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))