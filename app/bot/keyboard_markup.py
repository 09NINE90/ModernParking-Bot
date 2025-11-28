from datetime import timedelta, date

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.constants.weekdays_ru import weekdays_ru, full_weekdays_ru
from app.bot.service.user_schedules.schedules_service import get_readable_schedule
from app.data.models.schedule_dto import ScheduleDto

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

back_to_create_default_schedule_keyboard = [
    [InlineKeyboardButton(text="🔙 Назад", callback_data="create_default_schedule")]
]

back_to_create_default_schedule_markup = InlineKeyboardMarkup(inline_keyboard=back_to_create_default_schedule_keyboard)

back_to_delete_default_schedule_keyboard = [
    [InlineKeyboardButton(text="🔙 Назад", callback_data="delete_default_schedule")]
]

back_to_delete_default_schedule_markup = InlineKeyboardMarkup(inline_keyboard=back_to_delete_default_schedule_keyboard)

feedback_keyboard = [
    [InlineKeyboardButton(text="❗️ Сообщить об ошибке", callback_data="feedback_error")],
    [InlineKeyboardButton(text="💡 Предложить идею", callback_data="feedback_idea")],
    [InlineKeyboardButton(text="✍️ Оставить отзыв", callback_data="feedback_feedback")],
    [InlineKeyboardButton(text="Главное меню", callback_data="back_to_main")]
]

feedback_markup = InlineKeyboardMarkup(inline_keyboard=feedback_keyboard)

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
    # [InlineKeyboardButton(text="📝 Создать расписание", callback_data="create_default_schedule")],
    # [InlineKeyboardButton(text="🗑 Удалить расписание", callback_data="delete_default_schedule")]
]
main_markup = InlineKeyboardMarkup(inline_keyboard=main_keyboard)

found_spot_keyboard = [
    [InlineKeyboardButton(text="✅ Занять место", callback_data="take_spot")],
    [InlineKeyboardButton(text="❌ Отклонить место", callback_data="cancel_spot")]
]

found_spot_markup = InlineKeyboardMarkup(inline_keyboard=found_spot_keyboard)

reminder_spot_confirmation_keyboard = [
    [InlineKeyboardButton(text="✅ Да, я займу", callback_data="take_spot_by_reminder")],
    [InlineKeyboardButton(text="❌ Отклонить место", callback_data="cancel_spot_by_reminder")]
]

reminder_spot_confirmation_markup = InlineKeyboardMarkup(inline_keyboard=reminder_spot_confirmation_keyboard)

success_save_default_schedule_keyboard = [
    [InlineKeyboardButton(text="📝 Создать еще одно расписание", callback_data="create_default_schedule")],
    [InlineKeyboardButton(text="Главное меню", callback_data="back_to_main")]
]

success_save_default_schedule_markup = InlineKeyboardMarkup(inline_keyboard=success_save_default_schedule_keyboard)


def date_list_markup(existing_dates=None, count_days: int = 7, callback_name: str = '') -> InlineKeyboardMarkup:
    today = date.today()
    builder = InlineKeyboardBuilder()

    for i in range(count_days):
        current_date = today + timedelta(days=i)

        if current_date.weekday() == 5 or current_date.weekday() == 6:
            continue

        if current_date in existing_dates:
            continue

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


def create_default_schedule_markup(selected_days: list = None):
    if selected_days is None:
        selected_days = []

    builder = InlineKeyboardBuilder()

    for day in full_weekdays_ru:
        if day in selected_days:
            continue
        builder.button(
            text=f"{day}",
            callback_data=f"add_day_{day}"
        )

    if selected_days:
        builder.button(
            text="💾 Сохранить",
            callback_data="save_schedule"
        )

    builder.button(text="🔙 Назад", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()


def create_delete_schedules_keyboard(schedules: list[ScheduleDto]):
    keyboard = InlineKeyboardBuilder()

    for schedule in schedules:
        day_names = get_readable_schedule(schedule.day_numbers)

        keyboard.button(
            text=f"{day_names}",
            callback_data=f"del_{schedule.id}"
        )

    keyboard.button(
        text="🔙 Назад",
        callback_data="back_to_main"
    )

    keyboard.adjust(1)
    return keyboard.as_markup()


def confirmation_delete_schedule_markup(schedule_id):
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="✅ Да, удалить",
        callback_data=f"yes_del_{schedule_id}"
    )
    keyboard.button(
        text="❌ Отмена",
        callback_data="delete_default_schedule"
    )

    keyboard.adjust(2)
    return keyboard.as_markup()


def schedule_selection_markup(schedules: list):
    keyboard = InlineKeyboardBuilder()

    for schedule in schedules:
        schedule_id = schedule['id']
        day_names = schedule['short_day_names']

        keyboard.button(
            text=f"{day_names}",
            callback_data=f"select_{schedule_id}"
        )

    keyboard.button(
        text="Спасибо, не надо",
        callback_data="cancel_schedule_selection"
    )
    keyboard.adjust(1)
    return keyboard.as_markup()
