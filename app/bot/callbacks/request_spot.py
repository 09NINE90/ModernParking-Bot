import logging
from datetime import date, timedelta

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.callbacks.distribute_parking_spots import distribute_parking_spots
from app.bot.keyboard_markup import return_markup
from app.data.init_db import get_db_connection


async def show_request_calendar(query: CallbackQuery, state: FSMContext):
    today = date.today()
    builder = InlineKeyboardBuilder()

    for i in range(7):
        current_date = today + timedelta(days=i)
        builder.button(
            text=current_date.strftime("%d.%m (%a)"),
            callback_data=f"request_date_{current_date}"
        )

    builder.button(text="🔙 Назад", callback_data="back_to_main")
    builder.adjust(1)

    await query.message.edit_text(
        "Выберите дату, когда освободите свое место:",
        reply_markup=builder.as_markup()
    )


async def process_spot_request(query: CallbackQuery, date_str):
    tg_id = query.from_user.id
    request_date = date.fromisoformat(date_str)

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
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
                            SELECT 1
                            FROM dont_touch.parking_releases
                            WHERE release_date = %s
                              AND user_id_took = %s
                            ''', (request_date, db_user_id))

                if cur.fetchone():
                    await query.message.answer(
                        f"ℹ️ У вас уже есть место на {request_date.strftime('%d.%m.%Y')}",
                        reply_markup=return_markup
                    )
                    return []

                cur.execute('''
                            INSERT INTO dont_touch.parking_requests
                                (id, user_id, request_date)
                            VALUES (gen_random_uuid(), %s, %s)
                            ON CONFLICT (user_id, request_date) DO NOTHING
                            RETURNING id
                            ''', (db_user_id, request_date))

                result = cur.fetchone()
                conn.commit()

                if result:
                    await query.message.edit_text(
                        f"✅ Отлично! Вы заняли место в очереди на парковочное место на {request_date.strftime('%d.%m.%Y')}",
                        reply_markup=return_markup
                    )
                    await check_spot_distribution(query, tg_id, db_user_id, request_date)
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


async def check_spot_distribution(query: CallbackQuery, tg_id, db_user_id, request_date):
    try:
        await query.answer()

        await distribute_parking_spots()

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                            SELECT spot_id
                            FROM dont_touch.parking_releases
                            WHERE release_date = %s
                              AND user_id_took = %s
                            ORDER BY created_at ASC
                            ''', (request_date, str(db_user_id),))

                spot_id = cur.fetchone()
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