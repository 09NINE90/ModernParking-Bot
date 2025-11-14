import logging
from datetime import date

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from app.bot.service.distribution_service import distribute_parking_spots
from app.bot.keyboard_markup import return_markup, back_markup, date_list_markup
from app.data.init_db import get_db_connection
from app.bot.parking_states import ParkingStates
from app.data.repository.parking_releases_repository import insert_spot_on_date, get_user_id_took_by_date_and_spot
from app.data.repository.parking_spots_repository import get_spot_by_id
from app.data.repository.users_repository import get_user_id_by_tg_id


async def select_spot(query: CallbackQuery, state: FSMContext):
    """
        Начинает процесс выбора парковочного места для освобождения.

        Запрашивает у пользователя номер места и переводит диалог в состояние ожидания ввода.

        Параметры:
            query: CallbackQuery объект от Telegram
            state: FSMContext для управления состоянием диалога
    """
    await query.message.edit_text(
        "Напишите номер места, которое хотите освободить:",
        reply_markup = back_markup
    )

    await state.set_state(ParkingStates.waiting_for_spot_number)


async def handle_spot_number(message: types.Message, state: FSMContext):
    """
        Обрабатывает введенный пользователем номер парковочного места.

        Проверяет валидность номера и при успехе показывает календарь для выбора даты.

        Параметры:
            message: объект сообщения с введенным номером места
            state: FSMContext для управления состоянием диалога
    """
    spot_number = message.text.strip()

    if not await is_valid_spot_number(spot_number):
        await message.answer(
            "❌ Неверный номер места. Пожалуйста, введите корректный номер:"
        )
        return

    await state.update_data(selected_spot=spot_number)
    await show_release_calendar_message(message, state)


async def is_valid_spot_number(spot_number: str) -> bool:
    """
        Проверяет валидность номера парковочного места.

        Выполняет проверку существования места в базе данных и корректности формата номера.

        Параметры:
            spot_number: строка с номером места для проверки

        Возвращает:
            bool: True если место существует и номер корректен, иначе False
    """
    try:
        spot_num = int(spot_number)
    except ValueError:
        return False

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                spot = await get_spot_by_id(cur, spot_num)
                return spot is not None
    except Exception as e:
        logging.error(f"Error checking spot number {spot_number}: {e}")
        return False


async def show_release_calendar_message(message: types.Message, state: FSMContext):
    """
        Показывает календарь для выбора даты освобождения парковочного места.

        Создает интерактивную клавиатуру с датами на 7 дней вперед, исключая выходные дни.

        Параметры:
            message: объект сообщения от Telegram
            state: FSMContext для управления состоянием диалога
    """
    await message.answer(
        "Выберите дату, когда освободите свое место:",
        reply_markup=date_list_markup(callback_name='release_date')
    )


async def process_spot_release(query: CallbackQuery, date_str: str, state: FSMContext):
    """
    Обрабатывает освобождение парковочного места пользователем на указанную дату.

    Сохраняет информацию об освобожденном месте в базу данных и уведомляет пользователя о результате.

    Параметры:
        query: CallbackQuery объект от Telegram
        date_str: строка с датой в формате ISO
        state: FSMContext для управления состоянием диалога
    """
    tg_id = query.from_user.id
    release_date = date.fromisoformat(date_str)

    data = await state.get_data()
    spot_number = data.get('selected_spot')

    if not spot_number:
        await query.message.edit_text("❌ Ошибка: не найден номер места")
        return

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                spot_num = int(spot_number)

                user_record = await get_user_id_by_tg_id(cur, tg_id)

                if not user_record:
                    await query.message.edit_text("❌ Ошибка: пользователь не найден")
                    return

                db_user_id = user_record[0]

                result = await insert_spot_on_date(cur, db_user_id, spot_num, release_date)

                conn.commit()

                if result:
                    await query.message.edit_text(
                        f"✅ Отлично! Вы освободили место #{spot_num} на {release_date.strftime('%d.%m.%Y')}",
                        reply_markup=return_markup
                    )
                    await check_spot_distribution(query, state, db_user_id, spot_num, release_date)
                else:
                    await query.message.edit_text(
                        f"⚠️ Место #{spot_num} уже освобождено на {release_date.strftime('%d.%m.%Y')}",
                        reply_markup=return_markup
                    )


    except Exception as e:
        logging.error(f"Error saving release for user {tg_id}, spot {spot_number}: {e}")
        await query.message.edit_text(
            "❌ Произошла ошибка при сохранении. Попробуйте позже.",
            reply_markup=return_markup
        )

    await state.clear()


async def check_spot_distribution(query: CallbackQuery, state: FSMContext,db_user_id, spot_number, release_date):
    """
        Проверяет распределение парковочного места и уведомляет пользователя о статусе.

        Выполняет проверку, было ли назначено освобожденное место другому пользователю,
        и информирует владельца о текущем статусе распределения.

        Параметры:
            query: CallbackQuery объект от Telegram
            db_user_id: UUID пользователя в базе данных
            spot_number: номер парковочного места
            release_date: дата проверки распределения
    """
    try:
        await query.answer()

        await distribute_parking_spots()

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                user_id_took = await get_user_id_took_by_date_and_spot(cur, db_user_id, spot_number, release_date)

                if not user_id_took:
                    await query.message.answer(
                        f"⏳ Пока что Ваше место №{spot_number} на дату {release_date.strftime('%d.%m.%Y')} ни на кого не назначено",
                        reply_markup=return_markup
                    )

    except Exception as e:
        logging.error(f"Error checking spot by date for user {db_user_id}, date {release_date}: {e}")
        await query.message.answer(
            "❌ Произошла ошибка при проверке мест. Попробуйте позже.",
            reply_markup=return_markup
        )