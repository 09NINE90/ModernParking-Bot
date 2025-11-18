import logging
from datetime import date

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.constants.log_types import LogNotification
from app.bot.notification.log_notification import send_log_notification
from app.bot.service.distribution_service import distribute_parking_spots
from app.bot.keyboard_markup import return_markup, date_list_markup
from app.data.init_db import get_db_connection
from app.data.repository.parking_releases_repository import get_user_spot_by_date
from app.data.repository.parking_requests_repository import insert_request_on_date
from app.data.repository.users_repository import get_user_id_by_tg_id
from app.log_text import SPOT_REQUEST_SAVE_ERROR


async def show_request_calendar(query: CallbackQuery, state: FSMContext):
    """
        Показывает календарь для выбора даты запроса парковочного места.

        Создает интерактивную клавиатуру с датами на 7 дней вперед, исключая выходные дни.

        Параметры:
            query: CallbackQuery объект от Telegram
            state: FSMContext для управления состоянием диалога
    """
    await query.message.edit_text(
        "Выберите дату, когда освободите свое место:",
        reply_markup=date_list_markup(callback_name='request_date')
    )


async def process_spot_request(query: CallbackQuery, date_str, state: FSMContext):
    """
        Обрабатывает запрос на парковочное место от пользователя.

        Создает запрос в очереди на указанную дату и проверяет возможность распределения места.

        Параметры:
            query: CallbackQuery объект от Telegram
            date_str: строка с датой в формате ISO
    """
    tg_id = query.from_user.id
    request_date = date.fromisoformat(date_str)

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                user_record = await get_user_id_by_tg_id(cur, tg_id)

                if not user_record:
                    await query.message.edit_text("❌ Ошибка: пользователь не найден")
                    return None

                db_user_id = user_record[0]

                user_spot = await get_user_spot_by_date(cur, request_date, db_user_id)

                if user_spot:
                    await query.message.answer(
                        f"ℹ️ У вас уже есть место на {request_date.strftime('%d.%m.%Y')}",
                        reply_markup=return_markup
                    )
                    return []

                result = await insert_request_on_date(cur, db_user_id, request_date)
                conn.commit()

                if result:
                    await query.message.edit_text(
                        f"✅ Отлично! Вы заняли место в очереди на парковочное место на {request_date.strftime('%d.%m.%Y')}",
                        reply_markup=return_markup
                    )
                    await distribute_parking_spots()
                else:
                    await query.message.edit_text(
                        f"⚠️ Вы уже заняли место в очереди на парковочное место на {request_date.strftime('%d.%m.%Y')}",
                        reply_markup=return_markup
                    )

    except Exception as e:
        logging.error(SPOT_REQUEST_SAVE_ERROR.format(tg_id, request_date, e))
        await send_log_notification(LogNotification.ERROR, SPOT_REQUEST_SAVE_ERROR.format(tg_id, request_date, e))
        await query.message.edit_text(
            "❌ Произошла ошибка при сохранении. Попробуйте позже.",
            reply_markup=return_markup
        )