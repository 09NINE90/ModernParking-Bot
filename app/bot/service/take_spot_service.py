import logging
from aiogram.types import CallbackQuery
from app.bot.keyboard_markup import return_markup
from app.schedule.schedule_utils import cancel_scheduled_cancellation
from app.bot.service.distribution_service import distribute_parking_spots
from app.bot.service.process_confirmation_spot_service import process_spot_confirmation
from app.utils import confirmation_cache


async def take_spot(query: CallbackQuery):
    """Подтверждает занятие парковочного места пользователем."""
    user_tg_id = query.from_user.id

    try:
        confirmation_data = await confirmation_cache.get(user_tg_id)

        if not confirmation_data:
            logging.warning(f"[TAKE_SPOT] ❌ No confirmation data found for user {user_tg_id}")
            await query.message.edit_text("❌ Данные о месте устарели.")
            return

        logging.debug(
            f"[TAKE_SPOT] Attempting to cancel scheduled auto-cancellation for "
            f"spot #{confirmation_data.spot_number}, user {user_tg_id}"
        )
        cancel_scheduled_cancellation(confirmation_data)

        logging.debug(
            f"[TAKE_SPOT] Processing confirmation for user {user_tg_id}, spot #{confirmation_data.spot_number}"
        )
        success = await process_spot_confirmation(confirmation_data)

        if success:
            await query.message.edit_text(
                f"✅ Вы успешно заняли место #{confirmation_data.spot_number} "
                f"на {confirmation_data.assignment_date.strftime('%d.%m.%Y')}",
                reply_markup=return_markup
            )
        else:
            logging.warning(f"[TAKE_SPOT] ❌ Spot #{confirmation_data.spot_number} already taken (user {user_tg_id})")
            await query.message.edit_text(
                "❌ Не удалось занять место. Возможно, оно уже занято.",
                reply_markup=return_markup
            )

        await confirmation_cache.delete(user_tg_id)
    except Exception as e:
        logging.exception(f"[TAKE_SPOT] 🚨 Unexpected error for user {user_tg_id}: {e}")
        await query.message.edit_text(
            "❌ Произошла ошибка при занятии места.",
            reply_markup=return_markup
        )

    finally:
        logging.debug(f"[TAKE_SPOT] Triggering distribution after user {user_tg_id} action")
        try:
            await distribute_parking_spots()
        except Exception as e:
            logging.exception(f"[TAKE_SPOT] 🚨 Error during redistribution after user {user_tg_id}: {e}")
