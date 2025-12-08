from aiogram import types

from app.bot.handlers.commands.utils.for_admin_statistics import for_admin_statistics


async def statistics_command(message: types.Message):
    await for_admin_statistics(message)