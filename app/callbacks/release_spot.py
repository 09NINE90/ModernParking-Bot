import logging
from datetime import date, timedelta

import psycopg2
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot_keyboards import return_markup
from app.db_config import DATABASE_CONFIG
from app.parking_states import ParkingStates


async def select_spot(query: CallbackQuery, state: FSMContext):
    await query.message.edit_text(
        "Напишите номер места, которое хотите освободить:"
    )

    await state.set_state(ParkingStates.waiting_for_spot_number)

# Обработка введенного номера места
async def handle_spot_number(message: types.Message, state: FSMContext):
    spot_number = message.text.strip()

    if not await is_valid_spot_number(spot_number):
        await message.answer(
            "❌ Неверный номер места. Пожалуйста, введите корректный номер:"
        )
        return

    await state.update_data(selected_spot=spot_number)
    await show_release_calendar_message(message, state)

# Проверка валидности номера места
async def is_valid_spot_number(spot_number: str) -> bool:
    conn = None

    try:
        spot_num = int(spot_number)

        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        cursor.execute('''
                       SELECT *
                       FROM dont_touch.parking_spots ps
                       WHERE ps.spot_id = %s
                       ''', (spot_num,))
        return cursor.fetchone() is not None
    except ValueError:
        return False
    finally:
        if conn:
            conn.close()

# Показать календарь для освобождения места (для сообщений)
async def show_release_calendar_message(message: types.Message, state: FSMContext):
    today = date.today()
    builder = InlineKeyboardBuilder()

    for i in range(7):
        current_date = today + timedelta(days=i)
        builder.button(
            text=current_date.strftime("%d.%m (%a)"),
            callback_data=f"release_date_{current_date}"
        )

    builder.button(text="🔙 Назад", callback_data="back_to_main")
    builder.adjust(1)

    await message.answer(
        "Выберите дату, когда освободите свое место:",
        reply_markup=builder.as_markup()
    )

# Обработка освобождения места
async def process_spot_release(query: CallbackQuery, date_str: str, state: FSMContext):
    tg_id = query.from_user.id
    release_date = date.fromisoformat(date_str)

    # Получаем данные из состояния
    data = await state.get_data()
    spot_number = data.get('selected_spot')

    if not spot_number:
        await query.message.edit_text("❌ Ошибка: не найден номер места")
        return

    conn = None
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()

        # Получаем user_id из базы
        cursor.execute('SELECT user_id FROM dont_touch.users WHERE tg_id = %s', (tg_id,))
        user_record = cursor.fetchone()

        if not user_record:
            await query.message.edit_text("❌ Ошибка: пользователь не найден")
            return

        db_user_id = user_record[0]

        # Добавляем запись об освобождении
        cursor.execute('''
                       INSERT INTO dont_touch.parking_releases (id, user_id, spot_id, release_date)
                       VALUES (gen_random_uuid(), %s, %s, %s)
                       ON CONFLICT (spot_id, release_date) DO NOTHING
                       RETURNING id
                       ''', (db_user_id, int(spot_number), release_date))

        result = cursor.fetchone()
        conn.commit()

        if result:
            await query.message.edit_text(
                f"✅ Отлично! Вы освободили место #{spot_number} на {release_date.strftime('%d.%m.%Y')}",
                reply_markup=return_markup
            )
        else:
            await query.message.edit_text(
                f"⚠️ Место #{spot_number} уже освобождено на {release_date.strftime('%d.%m.%Y')}",
                reply_markup=return_markup
            )

    except Exception as e:
        logging.error(f"Error saving release: {e}")
        await query.message.edit_text(
            "❌ Произошла ошибка при сохранении. Попробуйте позже.",
            reply_markup=return_markup
        )
    finally:
        if conn:
            conn.close()

    await state.clear()