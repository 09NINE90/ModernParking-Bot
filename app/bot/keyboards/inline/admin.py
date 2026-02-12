from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.constants.callback_data import CallbackData
from app.config import settings


def create_main_admin_markup() -> InlineKeyboardMarkup:
    """Клавиатура для админа"""
    keyboard = [
        [InlineKeyboardButton(text="📈 Статистика за все время", callback_data=CallbackData.ALL_STATISTICS)],
        [InlineKeyboardButton(text="📊 Годовая статистика", callback_data=CallbackData.YEAR_STATS)],
        [InlineKeyboardButton(text="📋 Квартальная статистика", callback_data=CallbackData.QUARTER_STATS)],
        [InlineKeyboardButton(text="📅 Месячная статистика", callback_data=CallbackData.MONTH_STATS)],
        [InlineKeyboardButton(text="📉 Недельная статистика", callback_data=CallbackData.WEEK_STATS)],
    ]
    if settings.STAND != "PROM":
        keyboard.append(
            [InlineKeyboardButton(text="🧹 Очистить таблицы", callback_data=CallbackData.CLEAR_TABLES)],
        )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


main_admin_markup = create_main_admin_markup()


def back_to_main_admin_markup() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(
            text="Назад",
            callback_data=CallbackData.MAIN_ADMIN,
            icon_custom_emoji_id="5258236805890710909"
        )],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


back_to_main_admin = back_to_main_admin_markup()


def confirm_clear_tables_markup() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="Да, очистить", callback_data=CallbackData.YES_CLEAR_TABLES, style="success")],
        [InlineKeyboardButton(text="Отмена", callback_data=CallbackData.MAIN_ADMIN, style="danger")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


confirm_clear_tables_admin = confirm_clear_tables_markup()


def create_stats_period_markup(period_name: str, period_displays: list[str]) -> InlineKeyboardMarkup:
    """Клавиатура для админа"""
    builder = InlineKeyboardBuilder()
    for period_display in period_displays:
        builder.button(
            text=period_display,
            callback_data=f"{period_name}_{period_display}",
        )

    builder.button(
        text="Назад",
        callback_data=CallbackData.MAIN_ADMIN,
        icon_custom_emoji_id="5258236805890710909"
    )
    builder.adjust(1)
    return builder.as_markup()


def back_to_stats_period_markup(period_name: str) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(
            text="Назад",
            callback_data=f"{period_name}{CallbackData.POSTFIX_STATS}",
            icon_custom_emoji_id="5258236805890710909"
        )],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
