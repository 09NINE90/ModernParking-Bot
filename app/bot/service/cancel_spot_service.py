import logging
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from app.bot.keyboard_markup import return_markup
from app.bot.schedule.schedule_utils import cancel_scheduled_cancellation
from app.bot.service.distribution_service import distribute_parking_spots
from app.bot.service.spot_confirmation_service import process_spot_cancel

async def cancel_spot(query: CallbackQuery, state: FSMContext):
    """Обрабатывает отмену занятия места"""
    try:
        data = await state.get_data()
        confirmation_data = data.get('confirmation_data')

        if not confirmation_data:
            await query.message.edit_text("❌ Данные о месте устарели")
            await state.clear()
            return

        cancel_scheduled_cancellation(confirmation_data)

        success = await process_spot_cancel(confirmation_data)

        if success:
            await query.message.edit_text(
                f"ℹ️ Вы успешно отказались от места #{confirmation_data.spot_number} "
                f"на {confirmation_data.assignment_date.strftime('%d.%m.%Y')}\n"
                "️️⚠️ Я больше не буду предлагать вам места на эту дату",
                reply_markup=return_markup
            )
        else:
            await query.message.edit_text(
                "❌ Не удалось занять место. Возможно, оно уже занято.",
                reply_markup=return_markup
            )
        await state.clear()

    except Exception as e:
        logging.error(f"Error taking spot for user {query.from_user.id}: {e}")
        await query.message.edit_text(
            "❌ Произошла ошибка при занятии места",
            reply_markup=return_markup
        )
        await state.clear()
    finally:
        await distribute_parking_spots(state)