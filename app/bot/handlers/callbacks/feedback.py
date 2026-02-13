from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.constants.callback_data import CallbackData
from app.bot.handlers.callbacks.utils.feedback_utils import processing_feedback
from app.bot.keyboards import back_to_main_markup
from app.logs.log_builder import log
from app.utils.emoji_util import canceled_emoji


def setup_feedback_callbacks(router: Router) -> None:
    @router.callback_query(F.data.startswith(CallbackData.FEEDBACK_PREFIX))
    async def feedback_callback(callback: CallbackQuery, state: FSMContext):
        """
            Выбор типа обратной связи
        """
        try:
            feedback_type = callback.data.replace(CallbackData.FEEDBACK_PREFIX, "")
            await processing_feedback(callback, state, feedback_type)
        except Exception as e:
            await callback.message.edit_text(
                text=f"{canceled_emoji} Ошибка при отправки обратной связи"
                     "<i>Обратитесь к администратору.\nВызовете:/feedback </i>",
                reply_markup=back_to_main_markup
            )
            await log(
                log_message=f"Ошибка в feedback_callback: {e}"
            )
