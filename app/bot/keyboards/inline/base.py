from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.constants.callback_data import CallbackData


def create_back_to_main_markup() -> InlineKeyboardMarkup:
    """Клавиатура для возврата в главное меню"""
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="Главное меню", callback_data=CallbackData.BACK_TO_MAIN)
        ]]
    )


def create_back_markup(callback_data: str, text: str = "🔙 Назад") -> InlineKeyboardMarkup:
    """Универсальная клавиатура для возврата"""
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text=text, callback_data=callback_data)
        ]]
    )


back_to_main_markup = create_back_to_main_markup()

return_to_main_markup = create_back_markup(
    callback_data=CallbackData.BACK_TO_MAIN
)

back_to_revoke_request_markup = create_back_markup(
    callback_data=CallbackData.REVOKE_REQUEST,
    text="🔙 Назад"
)

back_to_revoke_release_markup = create_back_markup(
    callback_data=CallbackData.REVOKE_RELEASE,
    text="🔙 Назад"
)

back_to_create_default_schedule_markup = create_back_markup(
    callback_data=CallbackData.CREATE_DEFAULT_SCHEDULE,
    text="🔙 Назад"
)

back_to_delete_default_schedule_markup = create_back_markup(
    callback_data=CallbackData.DELETE_DEFAULT_SCHEDULE,
    text="🔙 Назад"
)


def create_feedback_markup() -> InlineKeyboardMarkup:
    """Клавиатура для обратной связи"""
    keyboard = [
        [InlineKeyboardButton(text="❗️ Сообщить об ошибке", callback_data=CallbackData.FEEDBACK_ERROR)],
        [InlineKeyboardButton(text="💡 Предложить идею", callback_data=CallbackData.FEEDBACK_IDEA)],
        [InlineKeyboardButton(text="✍️ Оставить отзыв", callback_data=CallbackData.FEEDBACK_FEEDBACK)],
        [InlineKeyboardButton(text="Главное меню", callback_data=CallbackData.BACK_TO_MAIN)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


feedback_markup = create_feedback_markup()


# Главная клавиатура
def create_main_markup(is_admin: bool = False) -> InlineKeyboardMarkup:
    """Создает главную клавиатуру"""
    keyboard = [
        [InlineKeyboardButton(text="📊 Моя статистика", callback_data=CallbackData.MY_STATISTICS)],
        [
            InlineKeyboardButton(text="🗓 Освободить место", callback_data=CallbackData.RELEASE_SPOT),
            InlineKeyboardButton(text="Отозвать место", callback_data=CallbackData.REVOKE_RELEASE)
        ],
        [
            InlineKeyboardButton(text="🚗 Запросить место", callback_data=CallbackData.REQUEST_SPOT),
            InlineKeyboardButton(text="Отозвать запрос", callback_data=CallbackData.REVOKE_REQUEST)
        ],
        [InlineKeyboardButton(text="📝 Создать расписание", callback_data=CallbackData.CREATE_DEFAULT_SCHEDULE)],
        [InlineKeyboardButton(text="🗑 Удалить расписание", callback_data=CallbackData.DELETE_DEFAULT_SCHEDULE)]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


main_markup = create_main_markup()


# Клавиатуры для работы с местами
def create_found_spot_markup() -> InlineKeyboardMarkup:
    """Клавиатура при нахождении места"""
    keyboard = [
        [InlineKeyboardButton(text="✅ Занять место", callback_data=CallbackData.TAKE_SPOT)],
        [InlineKeyboardButton(text="❌ Отклонить место", callback_data=CallbackData.CANCEL_SPOT)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def create_reminder_spot_confirmation_markup() -> InlineKeyboardMarkup:
    """Клавиатура для напоминания о подтверждении места"""
    keyboard = [
        [InlineKeyboardButton(text="✅ Да, я займу", callback_data=CallbackData.TAKE_SPOT_BY_REMINDER)],
        [InlineKeyboardButton(text="❌ Отклонить место", callback_data=CallbackData.CANCEL_SPOT_BY_REMINDER)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def create_success_save_default_schedule_markup() -> InlineKeyboardMarkup:
    """Клавиатура после успешного сохранения расписания"""
    keyboard = [
        [InlineKeyboardButton(text="📝 Создать еще одно расписание",
                              callback_data=CallbackData.CREATE_DEFAULT_SCHEDULE)],
        [InlineKeyboardButton(text="Главное меню", callback_data=CallbackData.BACK_TO_MAIN)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


found_spot_markup = create_found_spot_markup()
reminder_spot_confirmation_markup = create_reminder_spot_confirmation_markup()
success_save_default_schedule_markup = create_success_save_default_schedule_markup()
