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

back_to_revoke_request_keyboard = [
    [InlineKeyboardButton(text="🔙 Назад", callback_data="revoke_request")]
]

back_to_revoke_request_markup = InlineKeyboardMarkup(inline_keyboard=back_to_revoke_request_keyboard)

back_to_revoke_release_keyboard = [
    [InlineKeyboardButton(text="🔙 Назад", callback_data="revoke_release")]
]

back_to_revoke_release_markup = InlineKeyboardMarkup(inline_keyboard=back_to_revoke_release_keyboard)

main_keyboard = [
    [InlineKeyboardButton(text="📊 Моя статистика", callback_data="my_statistics")],
    [
        InlineKeyboardButton(text="🗓 Освободить место", callback_data="release_spot"),
        InlineKeyboardButton(text="Отозвать место", callback_data="revoke_release")
    ],
    [
        InlineKeyboardButton(text="🚗 Запросить место", callback_data="request_spot"),
        InlineKeyboardButton(text="Отозвать запрос", callback_data="revoke_request")
    ],
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


def revoke_requests_markup(requests):
    builder = InlineKeyboardBuilder()
    for request in requests:
        spot = "место не назначено"
        if request.spot_id:
            spot = f"место № {request.spot_id}"
        builder.button(
            text=f"{request.request_date.strftime('%d.%m')} ({spot})",
            callback_data=f"confirmation_revoke_request_{request.request_id}"
        )

    builder.button(text="🔙 Назад", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()

def confirmation_revoke_requests_markup(request, markup_text):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"✅ Да, {markup_text}",
        callback_data=f"confirm_revoke_request_{request.request_id}"
    )
    builder.button(
        text="🔙 Отмена",
        callback_data="revoke_request"
    )

    builder.adjust(2)
    return builder.as_markup()

def revoke_releases_markup(releases):
    builder = InlineKeyboardBuilder()
    for release in releases:
        builder.button(
            text=f"{release.release_date.strftime('%d.%m')} место №{release.spot_id}",
            callback_data=f"confirmation_revoke_release_{release.release_id}"
        )

    builder.button(text="🔙 Назад", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()

def confirmation_revoke_release_markup(release):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"✅ Да, отозвать",
        callback_data=f"confirm_revoke_release_{release.release_id}"
    )
    builder.button(
        text="🔙 Отмена",
        callback_data="revoke_release"
    )

    builder.adjust(2)
    return builder.as_markup()