from datetime import date, timedelta, datetime

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot import ParkingStates
from app.bot.handlers.callbacks.utils.distribution_spots_util import distribute_parking_spots
from app.bot.keyboards import back_to_main_markup, date_list_markup
from app.bot.utils import get_user_full_mention
from app.data import get_db_connection
from app.logs.log_builder import log, LogType
from app.services import ServiceFactory
from app.utils.daily_statistics_util import update_daily_statistics_by_date
from app.utils.emoji_util import info_emoji, warn_emoji, sber_emoji, sber_accept_emoji, canceled_emoji, sber_spot_emoji, \
    sber_date_emoji


async def select_spot(query: CallbackQuery, state: FSMContext):
    """
        Начинает процесс выбора парковочного места для освобождения.

        Запрашивает у пользователя номер места и переводит диалог в состояние ожидания ввода.

        Параметры:
            query: CallbackQuery объект от Telegram
            state: FSMContext для управления состоянием диалога
    """
    await query.message.edit_text(
        f"{sber_spot_emoji} Напишите номер места, которое хотите освободить:",
        reply_markup=back_to_main_markup
    )

    await state.set_state(ParkingStates.waiting_for_spot_number)
    await query.answer()


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
            f"{canceled_emoji} Неверный номер места. Пожалуйста, введите корректный номер:"
        )
        return

    await state.update_data(selected_spot=spot_number)
    await show_release_calendar_message(message, state)


async def show_release_calendar_message(message: types.Message, state: FSMContext):
    """
        Показывает календарь для выбора даты освобождения парковочного места.

        Создает интерактивную клавиатуру с датами на 7 дней вперед, исключая выходные дни.

        Параметры:
            message: объект сообщения от Telegram
            state: FSMContext для управления состоянием диалога
    """
    with get_db_connection() as conn:
        tg_user_id = message.from_user.id

        user_service = ServiceFactory.create_user_service(conn)
        spot_service = ServiceFactory.create_spot_release_service(conn)

        db_user_id = user_service.get_db_user_id_by_tg_id(tg_user_id)
        if not db_user_id:
            return None

        today = datetime.today().date()

        data = await state.get_data()
        spot_number = data.get('selected_spot')

        existing_dates_result = spot_service.get_user_releases_dates(db_user_id, spot_number, today)
        if not existing_dates_result:
            existing_dates = []
        else:
            existing_dates = [date_tuple[0] for date_tuple in existing_dates_result]

        if not is_has_available_dates(existing_dates, today):
            await message.answer(
                f"На ближайшие 7 дней Вы освободили место <b>№{spot_number}</b> на все доступные даты.\n\n"
                "<i>Попробуйте отправить запрос позже, когда будут доступны новые даты.</i>",
                reply_markup=back_to_main_markup
            )
            return None
        else:
            await message.answer(
                f"{sber_date_emoji} Выберите дату, когда освободите свое место:\n\n"
                f"{info_emoji} <i>Отображаются только те даты, на которые место <b>№{spot_number}</b> не было освобождено.</i>",
                reply_markup=date_list_markup(existing_dates=existing_dates, callback_prefix='release_date')
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


async def process_spot_release(callback: CallbackQuery, date_str: str, state: FSMContext):
    """
    Обрабатывает освобождение парковочного места пользователем на указанную дату.

    Сохраняет информацию об освобожденном месте в базу данных и уведомляет пользователя о результате.

    Параметры:
        callback: CallbackQuery объект от Telegram
        date_str: строка с датой в формате ISO
        state: FSMContext для управления состоянием диалога
    """
    datetime_now = datetime.now()
    tg_user_id = callback.from_user.id
    release_date = date.fromisoformat(date_str)

    data = await state.get_data()
    spot_number = data.get('selected_spot')

    if not spot_number:
        await log(log_message="Не найден номер места")
        await callback.message.edit_text(f"{canceled_emoji} Ошибка: не найден номер места")
        return None

    with get_db_connection() as conn:
        spot_num = int(spot_number)

        spot_release_service = ServiceFactory.create_spot_release_service(conn)
        user_service = ServiceFactory.create_user_service(conn)

        db_user_id = user_service.get_db_user_id_by_tg_id(tg_user_id)
        if not db_user_id:
            return None

        result = spot_release_service.create_spot_release(db_user_id, spot_num, release_date)

        conn.commit()

        if result:
            await callback.message.edit_text(
                f"{sber_accept_emoji} Отлично! Вы освободили место №{spot_num} на {release_date.strftime('%d.%m.%Y')}",
                reply_markup=back_to_main_markup
            )

            await update_daily_statistics_by_date(datetime_now)

            user_name = await get_user_full_mention(tg_user_id)
            await log(log_type=LogType.INFO,
                      log_message=f"{user_name} успешно освободил место №{spot_number} "
                                  f"на {release_date.strftime('%d.%m.%Y')}")

            await distribute_parking_spots()

            return None
        else:
            await callback.message.edit_text(
                f"{warn_emoji} Место №{spot_num} уже освобождено на {release_date.strftime('%d.%m.%Y')}",
                reply_markup=back_to_main_markup
            )
            return None


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
            spot_release_service = ServiceFactory.create_spot_release_service(conn)

            spot = spot_release_service.is_valid_spot_number(spot_num)
            return spot is not None

    except Exception as e:
        await log(log_message=f"Ошибка при проверке валидности парковочного места №{spot_number}. Exeption: {e}")
        return False
