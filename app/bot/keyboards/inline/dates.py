from datetime import timedelta, date
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.constants.callback_data import CallbackData
from app.constants import weekdays_ru


def date_list_markup(
        existing_dates: list[date] = None,
        count_days: int = 7,
        callback_prefix: str = ''
) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру со списком дат

    Args:
        existing_dates: Множество дат, которые нужно исключить
        count_days: Количество дней для отображения
        callback_prefix: Префикс для callback_data
    """
    if existing_dates is None:
        existing_dates = set()

    today = date.today()
    builder = InlineKeyboardBuilder()

    for i in range(count_days):
        current_date = today + timedelta(days=i)

        if current_date.weekday() == 5 or current_date.weekday() == 6:
            continue

        if current_date in existing_dates:
            continue

        weekday_ru = weekdays_ru[current_date.weekday()]
        today_text = 'сегодня' if current_date == today else ''

        date_text = f"{current_date.strftime('%d.%m')} ({weekday_ru})"
        if today_text:
            date_text += f" {today_text}"

        builder.button(
            text=date_text,
            callback_data=f"{callback_prefix}_{current_date}"
        )

    builder.button(
        text="Назад",
        callback_data=CallbackData.BACK_TO_MAIN,
        icon_custom_emoji_id="5420128322438851607"
    )
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
            callback_data=f"{CallbackData.CONFIRMATION_REVOKE_REQUEST_PREFIX}{request.request_id}"
        )

    builder.button(
        text="Назад",
        callback_data=CallbackData.BACK_TO_MAIN,
        icon_custom_emoji_id="5420128322438851607"
    )
    builder.adjust(1)
    return builder.as_markup()


def confirmation_revoke_requests_markup(request, markup_text):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"Да, {markup_text}",
        callback_data=f"{CallbackData.CONFIRM_REVOKE_REQUEST_PREFIX}{request.request_id}",
        style="success"
    )
    builder.button(
        text="Отмена",
        callback_data=CallbackData.REVOKE_REQUEST,
        style="danger"
    )

    builder.adjust(2)
    return builder.as_markup()


def revoke_releases_markup(releases):
    builder = InlineKeyboardBuilder()
    for release in releases:
        builder.button(
            text=f"{release.release_date.strftime('%d.%m')} место №{release.spot_id}",
            callback_data=f"{CallbackData.CONFIRMATION_REVOKE_RELEASE_PREFIX}{release.release_id}"
        )

    builder.button(
        text="Назад",
        callback_data=CallbackData.BACK_TO_MAIN,
        icon_custom_emoji_id="5420128322438851607"
    )
    builder.adjust(1)
    return builder.as_markup()


def confirmation_revoke_release_markup(release):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"Да, отозвать",
        callback_data=f"{CallbackData.CONFIRM_REVOKE_RELEASE_PREFIX}{release.release_id}",
        style="success"
    )
    builder.button(
        text="Отмена",
        callback_data=CallbackData.REVOKE_RELEASE,
        style="danger"
    )

    builder.adjust(2)
    return builder.as_markup()
