import logging
from datetime import date, timedelta

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.callbacks.distribute_parking_spots import distribute_parking_spots
from app.bot.keyboard_markup import return_markup
from app.data.init_db import get_db_connection
from app.bot.parking_states import ParkingStates


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
    try:
        spot_num = int(spot_number)
    except ValueError:
        return False

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                            SELECT 1
                            FROM dont_touch.parking_spots ps
                            WHERE ps.spot_id = %s
                            ''', (spot_num,))
                return cur.fetchone() is not None
    except Exception as e:
        logging.error(f"Error checking spot number {spot_number}: {e}")
        return False

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

    data = await state.get_data()
    spot_number = data.get('selected_spot')

    if not spot_number:
        await query.message.edit_text("❌ Ошибка: не найден номер места")
        return

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                spot_num = int(spot_number)

                cur.execute(
                    'SELECT user_id FROM dont_touch.users WHERE tg_id = %s',
                    (tg_id,)
                )
                user_record = cur.fetchone()

                if not user_record:
                    await query.message.edit_text("❌ Ошибка: пользователь не найден")
                    return

                db_user_id = user_record[0]

                cur.execute('''
                    INSERT INTO dont_touch.parking_releases 
                    (id, user_id, spot_id, release_date)
                    VALUES (gen_random_uuid(), %s, %s, %s)
                    ON CONFLICT (spot_id, release_date) DO NOTHING
                    RETURNING id
                ''', (db_user_id, spot_num, release_date))

                result = cur.fetchone()
                conn.commit()

                if result:
                    await query.message.edit_text(
                        f"✅ Отлично! Вы освободили место #{spot_num} на {release_date.strftime('%d.%m.%Y')}",
                        reply_markup=return_markup
                    )
                    await check_spot_distribution(query, db_user_id, spot_num, release_date)
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

# Проверяет распределено ли место
async def check_spot_distribution(query: CallbackQuery, db_user_id, spot_number, release_date):
    try:
        await query.answer()

        await distribute_parking_spots()

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                            SELECT pr.user_id_took
                            FROM dont_touch.parking_releases pr
                            WHERE pr.release_date = %s
                              AND pr.user_id = %s
                                AND pr.spot_id = %s
                            ''', (release_date, db_user_id, spot_number))

                user_id_took = cur.fetchone()

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