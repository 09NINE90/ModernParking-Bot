import logging
from datetime import date, timedelta

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.callbacks.distribute_parking_spots import distribute_parking_spots
from app.bot.keyboard_markup import return_markup
from app.data.init_db import get_db_connection
from app.data.repository.parking_releases_repository import get_user_spot_by_date, \
    get_spot_id_by_user_id_and_request_date
from app.data.repository.parking_requests_repository import insert_request_on_date
from app.data.repository.users_repository import get_user_id_by_tg_id


async def show_request_calendar(query: CallbackQuery, state: FSMContext):
    """
        Показывает календарь для выбора даты запроса парковочного места.

        Создает интерактивную клавиатуру с датами на 7 дней вперед, исключая выходные дни.

        Параметры:
            query: CallbackQuery объект от Telegram
            state: FSMContext для управления состоянием диалога
    """
    today = date.today()
    builder = InlineKeyboardBuilder()

    for i in range(7):
        current_date = today + timedelta(days=i)
        if current_date.weekday() != 5 and current_date.weekday() != 6:
            builder.button(
                text=current_date.strftime("%d.%m (%a)"),
                callback_data=f"release_date_{current_date}"
            )

    builder.button(text="🔙 Назад", callback_data="back_to_main")
    builder.adjust(1)

    await query.message.edit_text(
        "Выберите дату, когда освободите свое место:",
        reply_markup=builder.as_markup()
    )


async def process_spot_request(query: CallbackQuery, date_str):
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
                    await check_spot_distribution(query, db_user_id, request_date)
                else:
                    await query.message.edit_text(
                        f"⚠️ Вы уже заняли место в очереди на парковочное место на {request_date.strftime('%d.%m.%Y')}",
                        reply_markup=return_markup
                    )

    except Exception as e:
        logging.error(f"Error saving spot request for user {tg_id}, date {request_date}: {e}")
        await query.message.edit_text(
            "❌ Произошла ошибка при сохранении. Попробуйте позже.",
            reply_markup=return_markup
        )


async def check_spot_distribution(query: CallbackQuery, db_user_id, request_date):
    """
        Проверяет распределение парковочных мест для пользователя после создания запроса.

        Выполняет немедленную проверку доступности мест и уведомляет пользователя о результате.

        Параметры:
            query: CallbackQuery объект от Telegram
            db_user_id: UUID пользователя в базе данных
            request_date: дата проверки распределения
    """
    try:
        await query.answer()

        await distribute_parking_spots()

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                spot_id = await get_spot_id_by_user_id_and_request_date(cur, db_user_id, request_date)
                if not spot_id:
                    await query.message.answer(
                        "😔 Пока что не найдено свободных мест на эту дату\n"
                        "Как только место появится, я обязательно сообщу",
                        reply_markup=return_markup
                    )

                conn.commit()
    except Exception as e:
        logging.error(f"Error checking spot by date for user {db_user_id}, date {request_date}: {e}")
        await query.message.answer(
            "❌ Произошла ошибка при поиске мест. Попробуйте позже.",
            reply_markup=return_markup
        )
        return []
    finally:
        return []