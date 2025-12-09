from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.keyboard_markup import return_markup
from app.schedule.schedule_utils import cancel_schedule_distribute_weekly_parking_schedules


async def handle_cancel_schedule_selection(query: CallbackQuery, state: FSMContext):
    tg_user_id = query.from_user.id
    await cancel_schedule_distribute_weekly_parking_schedules(tg_user_id)

    await query.message.edit_text(
        text="Вы <b>отклонили</b> предложение об автоматическом создании запросов на парковочные места на следующую неделю.\n\n"
             "ℹ️ <i>Вы всё равно можете сделать запросы самостоятельно, нажав '🚗 Запросить место' в главном меню</i>",
        reply_markup=return_markup
    )
