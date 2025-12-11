from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.bot.constants.callback_data import CallbackData
from app.config import settings


def create_main_admin_markup() -> InlineKeyboardMarkup:
    """Клавиатура для админа"""
    keyboard = [
        [InlineKeyboardButton(text="📊 Статистика за все время", callback_data=CallbackData.ALL_STATISTICS)],
    ]
    if settings.STAND != "PROM":
        keyboard.append(
            [InlineKeyboardButton(text="🧹 Очистить таблицы", callback_data=CallbackData.CLEAR_TABLES)],
        )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


main_admin_markup = create_main_admin_markup()


def back_to_main_admin_markup() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="🔙 Назад", callback_data=CallbackData.MAIN_ADMIN)],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


back_to_main_admin = back_to_main_admin_markup()


def confirm_clear_tables_markup() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="Да, очистить", callback_data=CallbackData.YES_CLEAR_TABLES)],
        [InlineKeyboardButton(text="Отмена", callback_data=CallbackData.MAIN_ADMIN)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


confirm_clear_tables_admin = confirm_clear_tables_markup()
