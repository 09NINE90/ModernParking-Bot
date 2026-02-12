from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.constants.callback_data import CallbackData
from app.constants import full_weekdays_ru, get_readable_schedule
from app.data.models.dto.schedule_dto import ScheduleDto


def create_default_schedule_markup(selected_days: list[str] = None) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора дней недели при создании расписания

    Args:
        selected_days: Список уже выбранных дней
    """
    if selected_days is None:
        selected_days = []

    builder = InlineKeyboardBuilder()

    for day in full_weekdays_ru:
        if day in selected_days:
            continue
        builder.button(
            text=f"{day}",
            callback_data=f"{CallbackData.ADD_DAY_PREFIX}{day}"
        )

    if selected_days:
        builder.button(
            text="Сохранить",
            callback_data=CallbackData.SAVE_SCHEDULE,
            icon_custom_emoji_id='5462956611033117422'
        )

    builder.button(
        text="Назад",
        callback_data=CallbackData.BACK_TO_MAIN,
        icon_custom_emoji_id="5258236805890710909"
    )
    builder.adjust(1)
    return builder.as_markup()


def create_delete_schedules_keyboard(schedules: list[ScheduleDto]) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора расписания для удаления

    Args:
        schedules: Список расписаний пользователя
    """
    builder = InlineKeyboardBuilder()

    for schedule in schedules:
        day_names = get_readable_schedule(schedule.day_numbers)
        builder.button(
            text=f"{day_names}",
            callback_data=f"{CallbackData.DEL_PREFIX}{schedule.id}"
        )

    builder.button(
        text="Назад",
        callback_data=CallbackData.BACK_TO_MAIN,
        icon_custom_emoji_id="5258236805890710909"
    )

    builder.adjust(1)
    return builder.as_markup()


def confirmation_delete_schedule_markup(schedule_id: str) -> InlineKeyboardMarkup:
    """
    Клавиатура для подтверждения удаления расписания

    Args:
        schedule_id: ID расписания
    """
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Да, удалить",
        callback_data=f"{CallbackData.YES_DEL_PREFIX}{schedule_id}",
        style="success"
    )
    builder.button(
        text="Отмена",
        callback_data=CallbackData.DELETE_DEFAULT_SCHEDULE,
        style="danger"
    )

    builder.adjust(2)
    return builder.as_markup()


def schedule_selection_markup(schedules: list[dict]) -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора расписания

    Args:
        schedules: Список расписаний в виде словарей
    """
    builder = InlineKeyboardBuilder()

    for schedule in schedules:
        schedule_id = schedule['id']
        day_names = schedule['short_day_names']
        builder.button(
            text=f"{day_names}",
            callback_data=f"{CallbackData.SELECT_PREFIX}{schedule_id}"
        )

    builder.button(
        text="Спасибо, не надо",
        callback_data=CallbackData.CANCEL_SCHEDULE_SELECTION
    )
    builder.adjust(1)
    return builder.as_markup()
