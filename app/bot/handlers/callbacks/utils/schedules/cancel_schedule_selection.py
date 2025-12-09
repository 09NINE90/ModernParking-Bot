from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.keyboards import back_to_main_markup
from app.scheduler.schedule_utils import cancel_schedule_distribute_weekly_parking_schedules


async def cancel_schedule_selection(callback: CallbackQuery, state: FSMContext):
    tg_user_id = callback.from_user.id
    await cancel_schedule_distribute_weekly_parking_schedules(tg_user_id)

    await callback.message.edit_text(
        text="Вы <b>отклонили</b> предложение об автоматическом создании запросов "
             "на парковочные места на следующую неделю.\n\n"
             "ℹ️ <i>Вы всё равно можете сделать запросы самостоятельно, "
             "нажав '🚗 Запросить место' в главном меню</i>",
        reply_markup=back_to_main_markup
    )
