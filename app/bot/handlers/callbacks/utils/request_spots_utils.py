from datetime import datetime, timedelta, date

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.handlers.callbacks.utils.distribution_spots_util import distribute_parking_spots
from app.data import get_db_connection
from app.bot.keyboards import back_to_main_markup, date_list_markup
from app.logs.log_builder import log
from app.services.factory import ServiceFactory


async def show_request_calendar(callback: CallbackQuery, state: FSMContext):
    """
        Показывает календарь для выбора даты запроса парковочного места.

        Создает интерактивную клавиатуру с датами на 7 дней вперед, исключая выходные дни.

        Параметры:
            callback: CallbackQuery объект от Telegram
            state: FSMContext для управления состоянием диалога
    """
    with get_db_connection() as conn:
        tg_user_id = callback.from_user.id
        user_service = ServiceFactory.create_user_service(conn)
        spot_request_service = ServiceFactory.create_spot_request_service(conn)

        db_user_id = user_service.get_db_user_id_by_tg_id(tg_user_id)
        if not db_user_id:
            return None

        today = datetime.today().date()

        existing_dates_result = spot_request_service.get_user_request_dates(db_user_id, today)
        if not existing_dates_result:
            existing_dates = []
        else:
            existing_dates = [date_tuple[0] for date_tuple in existing_dates_result]

        if not is_has_available_dates(existing_dates, today):
            await callback.message.edit_text(
                "На ближайшие 7 дней у Вас уже есть запросы на все рабочие даты.\n\n"
                "<i>Попробуйте отправить запрос позже, когда будут доступны новые даты.</i>",
                reply_markup=back_to_main_markup
            )
        else:
            await callback.message.edit_text(
                "Выберите дату, на которую хотите запросить место:\n\n"
                f"ℹ️ <i>Отображаются только те даты, на которые Вы еще не делали запрос.</i>",
                reply_markup=date_list_markup(existing_dates=existing_dates, callback_prefix='request_date')
            )
    return None


def is_has_available_dates(existing_dates, today):
    available_dates = []
    for i in range(7):
        current_date = today + timedelta(days=i)
        if current_date.weekday() == 5 or current_date.weekday() == 6:
            continue
        if current_date in existing_dates:
            continue
        available_dates.append(current_date)

    return available_dates


async def process_spot_request(callback: CallbackQuery, state: FSMContext, date_str):
    """
        Обрабатывает запрос на парковочное место от пользователя.

        Создает запрос в очереди на указанную дату и проверяет возможность распределения места.

        Параметры:
            callback: CallbackQuery объект от Telegram
            date_str: строка с датой в формате ISO
    """
    tg_user_id = callback.from_user.id
    request_date = date.fromisoformat(date_str)

    with get_db_connection() as conn:
        user_service = ServiceFactory.create_user_service(conn)
        spot_release_service = ServiceFactory.create_spot_release_service(conn)
        spot_request_service = ServiceFactory.create_spot_request_service(conn)

        db_user_id = user_service.get_db_user_id_by_tg_id(tg_user_id)
        if not db_user_id:
            return None

        user_spot = spot_release_service.get_user_spot_by_date(request_date, db_user_id)

        if user_spot:
            await callback.message.answer(
                f"ℹ️ У Вас уже есть место на {request_date.strftime('%d.%m.%Y')}",
                reply_markup=back_to_main_markup
            )
            return None

        result = spot_request_service.create_user_spot_request(db_user_id, request_date)
        conn.commit()

        if result:
            await callback.message.edit_text(
                f"✅ Отлично! Вы заняли место в очереди на парковочное место на {request_date.strftime('%d.%m.%Y')}",
                reply_markup=back_to_main_markup
            )
            await distribute_parking_spots()
        else:
            await callback.message.edit_text(
                f"⚠️ Вы уже заняли место в очереди на парковочное место на {request_date.strftime('%d.%m.%Y')}",
                reply_markup=back_to_main_markup
            )

    return None
