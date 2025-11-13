import logging
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from app.bot.keyboard_markup import return_markup
from app.bot.schedule.schedule_utils import cancel_scheduled_cancellation
from app.bot.service.distribution_service import distribute_parking_spots
from app.bot.service.spot_confirmation_service import process_spot_confirmation


async def take_spot(query: CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    logging.info(f"🔄 Starting take_spot process for user {user_id}")

    try:
        # Получение данных из состояния
        logging.info(f"📥 Getting state data for user {user_id}")
        data = await state.get_data()
        confirmation_data = data.get('confirmation_data')

        if not confirmation_data:
            logging.warning(f"❌ No confirmation data found for user {user_id}")
            await query.message.edit_text("❌ Данные о месте устарели")
            await state.clear()
            logging.info(f"🧹 State cleared for user {user_id} due to missing confirmation data")
            return

        logging.info(
            f"✅ Confirmation data found for user {user_id}: spot #{confirmation_data.spot_number}, date {confirmation_data.assignment_date}")

        # Отмена запланированного автоматического освобождения места
        logging.info(f"⏹️ Cancelling scheduled cancellation for spot #{confirmation_data.spot_number}, user {user_id}")
        cancel_scheduled_cancellation(confirmation_data)
        logging.info(f"✅ Scheduled cancellation cancelled for spot #{confirmation_data.spot_number}")

        # Обработка подтверждения места
        logging.info(f"🔄 Processing spot confirmation for user {user_id}, spot #{confirmation_data.spot_number}")
        success = await process_spot_confirmation(confirmation_data)

        if success:
            logging.info(f"✅ Spot #{confirmation_data.spot_number} successfully taken by user {user_id}")
            await query.message.edit_text(
                f"✅ Вы успешно заняли место #{confirmation_data.spot_number} "
                f"на {confirmation_data.assignment_date.strftime('%d.%m.%Y')}",
                reply_markup=return_markup
            )
            logging.info(f"📝 Success message sent to user {user_id}")
        else:
            logging.warning(f"❌ Failed to take spot #{confirmation_data.spot_number} for user {user_id}")
            await query.message.edit_text(
                "❌ Не удалось занять место. Возможно, оно уже занято.",
                reply_markup=return_markup
            )
            logging.info(f"📝 Error message sent to user {user_id}")

        # Очистка состояния
        logging.info(f"🧹 Clearing state for user {user_id}")
        await state.clear()
        logging.info(f"✅ State cleared for user {user_id}")

    except Exception as e:
        logging.error(f"🚨 Error taking spot for user {user_id}: {e}", exc_info=True)
        await query.message.edit_text(
            "❌ Произошла ошибка при занятии места",
            reply_markup=return_markup
        )
        logging.info(f"📝 Error notification sent to user {user_id}")

        logging.info(f"🧹 Clearing state for user {user_id} after error")
        await state.clear()
        logging.info(f"✅ State cleared for user {user_id} after error")

    finally:
        # Запуск распределения мест
        logging.info(f"🔄 Starting parking spots distribution after user {user_id} action")
        try:
            await distribute_parking_spots(state, query)
            logging.info(f"✅ Parking spots distribution completed after user {user_id} action")
        except Exception as e:
            logging.error(f"🚨 Error during parking spots distribution after user {user_id} action: {e}", exc_info=True)

        logging.info(f"🏁 take_spot process completed for user {user_id}")