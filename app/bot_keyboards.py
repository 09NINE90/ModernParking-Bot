from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

return_keyboard = [
            [InlineKeyboardButton(text="Главное меню", callback_data="back_to_main")]
        ]
return_markup = InlineKeyboardMarkup(inline_keyboard=return_keyboard)

main_keyboard = [
    [InlineKeyboardButton(text="🗓 Освободить место", callback_data="release_spot")],
    # [InlineKeyboardButton(text="🚗 Запросить место", callback_data="request_spot")],
    # [InlineKeyboardButton(text="📊 Моя статистика", callback_data="my_stats")],
    # [InlineKeyboardButton(text="📋 Доступные места", callback_data="available_spots")]
]
main_markup = InlineKeyboardMarkup(inline_keyboard=main_keyboard)