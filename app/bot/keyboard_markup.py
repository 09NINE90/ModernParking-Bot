from datetime import timedelta, date

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.constants.weekdays_ru import weekdays_ru

return_keyboard = [
    [InlineKeyboardButton(text="Главное меню", callback_data="back_to_main")]
]
return_markup = InlineKeyboardMarkup(inline_keyboard=return_keyboard)

back_keyboard = [
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
]
back_markup = InlineKeyboardMarkup(inline_keyboard=back_keyboard)

main_keyboard = [
    [InlineKeyboardButton(text="🗓 Освободить место", callback_data="release_spot")],
    [InlineKeyboardButton(text="🚗 Запросить место", callback_data="request_spot")],
]
main_markup = InlineKeyboardMarkup(inline_keyboard=main_keyboard)

found_spot_keyboard = [
    [InlineKeyboardButton(text="✅ Занять место", callback_data="take_spot")],
    [InlineKeyboardButton(text="❌ Отклонить место", callback_data="cancel_spot")]
]

found_spot_markup = InlineKeyboardMarkup(inline_keyboard=found_spot_keyboard)


def date_list_markup(count_days: int = 7, callback_name: str = '') -> InlineKeyboardMarkup:
    today = date.today()
    builder = InlineKeyboardBuilder()

    for i in range(count_days):
        current_date = today + timedelta(days=i)
        if current_date.weekday() != 5 and current_date.weekday() != 6:
            weekday_ru = weekdays_ru[current_date.weekday()]
            today_text = ''
            if current_date == today:
                today_text = 'сегодня'
            builder.button(
                text=f"{current_date.strftime('%d.%m')} ({weekday_ru}) {today_text}",
                callback_data=f"{callback_name}_{current_date}"
            )

    builder.button(text="🔙 Назад", callback_data="back_to_main")
    builder.adjust(1)

    return builder.as_markup()
