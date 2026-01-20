from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.keyboards import create_delete_schedules_keyboard, back_to_main_markup, confirmation_delete_schedule_markup
from app.bot.keyboards.inline import back_to_delete_default_schedule_markup
from app.constants import get_week_days_for_day_numbers
from app.data import get_db_connection
from app.services import ServiceFactory


async def delete_default_schedule(callback: CallbackQuery, state: FSMContext):
    tg_user_id = callback.from_user.id

    with get_db_connection() as conn:
        user_service = ServiceFactory.create_user_service(conn)
        spot_requests_schedule_service = ServiceFactory.create_spot_requests_schedule_service(conn)

        db_user_id = user_service.get_db_user_id_by_tg_id(tg_user_id)
        if not db_user_id:
            return None

        result_list = spot_requests_schedule_service.get_spot_requests_schedule_by_user_with_id(
            user_id=db_user_id,
        )

        if result_list is not None:
            keyboard = create_delete_schedules_keyboard(result_list)

            message_text = ("🗑️ <b>Удаление расписания</b>\n\n"
                            "Выберите расписание для удаления:")

            await callback.message.edit_text(
                text=message_text,
                reply_markup=keyboard
            )
        else:
            await callback.message.edit_text(
                text="👀 У Вас нет сохраненных расписаний для удаления.",
                reply_markup=back_to_main_markup
            )

        return None


async def confirmation_delete_schedule_by_id(callback: CallbackQuery, state: FSMContext, schedule_id):
    with get_db_connection() as conn:
        spot_requests_schedule_service = ServiceFactory.create_spot_requests_schedule_service(conn)
        result = spot_requests_schedule_service.get_spot_requests_schedule_by_id(
            schedule_id=schedule_id
        )
        if result is not None:
            week_days = get_week_days_for_day_numbers(result.day_numbers)

            message_text = f"🗑️ Уверены, что хотите удалить расписание на: <b>{week_days}</b>?"

            await callback.message.edit_text(
                text=message_text,
                reply_markup=confirmation_delete_schedule_markup(result.id)
            )

        return None


async def delete_schedule_by_id(callback: CallbackQuery, state: FSMContext, schedule_id):
    with get_db_connection() as conn:
        spot_requests_schedule_service = ServiceFactory.create_spot_requests_schedule_service(conn)

        is_delete = spot_requests_schedule_service.delete_spot_requests_schedule_by_id(
            schedule_id=schedule_id
        )

        if is_delete:
            message_text = "Расписание успешно удалено"
            await callback.message.edit_text(
                text=message_text,
                reply_markup=back_to_delete_default_schedule_markup
            )
        else:
            message_text = "Что-то пошло не так..."
            await callback.message.edit_text(
                text=message_text,
                reply_markup=back_to_delete_default_schedule_markup
            )

        return None