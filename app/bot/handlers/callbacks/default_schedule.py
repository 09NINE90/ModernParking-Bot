from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.constants.callback_data import CallbackData
from app.bot.handlers.callbacks.utils.schedules.add_day_schedule import add_day_schedule
from app.bot.handlers.callbacks.utils.schedules.cancel_schedule_selection import cancel_schedule_selection
from app.bot.handlers.callbacks.utils.schedules.create_default_schedule import create_default_schedule
from app.bot.handlers.callbacks.utils.schedules.delete_default_schedule import delete_default_schedule, \
    confirmation_delete_schedule_by_id, delete_schedule_by_id
from app.bot.handlers.callbacks.utils.schedules.save_default_schedule import save_default_schedule
from app.logs.log_builder import log
from app.utils.distribute_weekly_schedules_util import select_schedule


def setup_default_schedule_callbacks(router: Router) -> None:
    """Настройка базовых callback обработчиков"""

    @router.callback_query(F.data == CallbackData.CREATE_DEFAULT_SCHEDULE)
    async def create_default_schedule_callback(callback: CallbackQuery, state: FSMContext):
        """
            Начало создания расписания
        """
        try:
            await create_default_schedule(callback, state)
        except Exception as e:
            await log(
                log_message=f"Ошибка создания расписания: {e}"
            )

    @router.callback_query(F.data.startswith(CallbackData.ADD_DAY_PREFIX))
    async def add_day_schedule_callback(callback: CallbackQuery, state: FSMContext):
        """
            Добавление дня в расписание
        """
        try:
            day = callback.data.replace(CallbackData.ADD_DAY_PREFIX, "")
            await add_day_schedule(callback, state, day)
        except Exception as e:
            await log(
                log_message=f"Ошибка добавления дня в расписание: {e}"
            )

    @router.callback_query(F.data == CallbackData.SAVE_SCHEDULE)
    async def save_default_schedule_callback(callback: CallbackQuery, state: FSMContext):
        """
            Сохранение расписания
        """
        try:
            await save_default_schedule(callback, state)
        except Exception as e:
            await log(
                log_message=f"Ошибка сохранения расписания: {e}"
            )

    @router.callback_query(F.data == CallbackData.DELETE_DEFAULT_SCHEDULE)
    async def delete_default_schedule_callback(callback: CallbackQuery, state: FSMContext):
        """
            Выбор расписания для удаления
        """
        try:
            await delete_default_schedule(callback, state)
        except Exception as e:
            await log(
                log_message=f"Ошибка выбора расписания для удаления: {e}"
            )

    @router.callback_query(F.data.startswith(CallbackData.DEL_PREFIX))
    async def del_day_schedule_callback(callback: CallbackQuery, state: FSMContext):
        """
            Удаление расписания
        """
        try:
            schedule_id = callback.data.replace(CallbackData.DEL_PREFIX, "")
            await confirmation_delete_schedule_by_id(callback, state, schedule_id)
        except Exception as e:
            await log(
                log_message=f"Ошибка удаления расписания: {e}"
            )

    @router.callback_query(F.data.startswith(CallbackData.YES_DEL_PREFIX))
    async def yes_del_schedule_callback(callback: CallbackQuery, state: FSMContext):
        """
            Подтверждение удаления расписания
        """
        try:
            schedule_id = callback.data.replace(CallbackData.YES_DEL_PREFIX, "")
            await delete_schedule_by_id(callback, state, schedule_id)
        except Exception as e:
            await log(
                log_message=f"Ошибка подтверждения удаления расписания: {e}"
            )

    @router.callback_query(F.data.startswith(CallbackData.SELECT_PREFIX))
    async def select_schedule_callback(callback: CallbackQuery, state: FSMContext):
        """
            Выбор расписания для запросов
        """
        try:
            schedule_id = callback.data.replace(CallbackData.SELECT_PREFIX, "")
            await select_schedule(callback, state, schedule_id)
        except Exception as e:
            await log(
                log_message=f"Ошибка выбора расписания для запросов: {e}"
            )

    @router.callback_query(F.data == CallbackData.CANCEL_SCHEDULE_SELECTION)
    async def cancel_select_schedule_callback(callback: CallbackQuery, state: FSMContext):
        """
            Отмена выбора расписания
        """
        try:
            await cancel_schedule_selection(callback, state)
        except Exception as e:
            await log(
                log_message=f"Ошибка отмены выбора расписания: {e}"
            )
