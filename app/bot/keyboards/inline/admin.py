from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.bot.constants.callback_data import CallbackData


def create_main_admin_markup() -> InlineKeyboardMarkup:
    """Клавиатура для админа"""
    keyboard = [
        [InlineKeyboardButton(text="📊 Статистика за все время", callback_data=CallbackData.ALL_STATISTICS)],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


main_admin_markup = create_main_admin_markup()


def back_to_main_admin_markup() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="🔙 Назад", callback_data=CallbackData.MAIN_ADMIN)],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


back_to_main_admin = back_to_main_admin_markup()
