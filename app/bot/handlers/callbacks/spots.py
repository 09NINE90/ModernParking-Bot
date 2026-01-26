from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.constants.callback_data import CallbackData
from app.bot.handlers.callbacks.utils.release_spots_utils import select_spot, process_spot_release
from app.bot.handlers.callbacks.utils.request_spots_utils import show_request_calendar, process_spot_request
from app.bot.keyboards import back_to_main_markup
from app.logs.log_builder import log


def setup_spots_callbacks(router: Router) -> None:
    """Настройка callback обработчиков для работы с местами"""

    @router.callback_query(F.data == CallbackData.RELEASE_SPOT)
    async def handle_release_spot_callback(callback: CallbackQuery, state: FSMContext):
        """
            Обработка начала освобождения места
        """
        try:
            await select_spot(callback, state)
        except Exception as e:
            await log(
                log_message=f"Ошибка в handle_release_spot_callback: {e}"
            )
            await callback.message.edit_text(
                text="❌ Ошибка при начале освобождения места"
                     "<i>Обратитесь к администратору.\nВызовете:/feedback </i>",
                reply_markup=back_to_main_markup
            )

    @router.callback_query(F.data.startswith(CallbackData.RELEASE_DATE_PREFIX))
    async def handle_release_date_callback(callback: CallbackQuery, state: FSMContext):
        """
            Обработка выбора даты для освобождения места
        """
        try:
            date_str = callback.data.replace(CallbackData.RELEASE_DATE_PREFIX, "")
            await process_spot_release(callback, date_str, state)
        except ValueError:
            await callback.answer("❌ Неверный формат даты")
        except Exception as e:
            await log(
                log_message=f"Ошибка в handle_release_date_callback: {e}"
            )
            await callback.message.edit_text(
                text="❌ Ошибка при выборе даты для освобождения места"
                     "<i>Обратитесь к администратору.\nВызовете:/feedback </i>",
                reply_markup=back_to_main_markup
            )

    @router.callback_query(F.data == CallbackData.REQUEST_SPOT)
    async def handle_request_spot_callback(callback: CallbackQuery, state: FSMContext):
        """
            Обработка начала запроса парковочного места
        """
        try:
            await show_request_calendar(callback, state)
        except Exception as e:
            await log(
                log_message=f"Ошибка в handle_request_spot_callback: {e}"
            )
            await callback.message.edit_text(
                text="❌ Ошибка при начале запроса парковочного места"
                     "<i>Обратитесь к администратору.\nВызовете:/feedback </i>",
                reply_markup=back_to_main_markup
            )

    @router.callback_query(F.data.startswith(CallbackData.REQUEST_DATE_PREFIX))
    async def handle_request_date_callback(callback: CallbackQuery, state: FSMContext):
        """
            Обработка выбора даты для запроса парковочного места
        """
        try:
            date_str = callback.data.replace(CallbackData.REQUEST_DATE_PREFIX, "")
            await process_spot_request(callback, state, date_str)
        except Exception as e:
            await log(
                log_message=f"Ошибка в handle_release_spot_callback: {e}"
            )
            await callback.message.edit_text(
                text="❌ Ошибка при выборе даты для запроса парковочного места"
                     "<i>Обратитесь к администратору.\nВызовете:/feedback </i>",
                reply_markup=back_to_main_markup
            )
