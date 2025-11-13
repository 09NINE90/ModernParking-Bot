from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

return_keyboard = [
    [InlineKeyboardButton(text="Главное меню", callback_data="back_to_main")]
]
return_markup = InlineKeyboardMarkup(inline_keyboard=return_keyboard)

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