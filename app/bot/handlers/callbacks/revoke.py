from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.constants.callback_data import CallbackData
from app.bot.handlers.callbacks.utils.revoke.revoke_release_util import choose_release_for_revocation, \
    confirmation_revoke_release, confirm_revoke_release
from app.bot.handlers.callbacks.utils.revoke.revoke_request_util import choose_request_for_revocation, \
    confirmation_revoke_request, confirm_revoke_request
from app.bot.keyboards import back_to_main_markup
from app.bot.keyboards.inline import back_to_revoke_release_markup, back_to_revoke_request_markup
from app.logs.log_builder import log


def setup_revoke_callbacks(router: Router) -> None:
    """
        Отзыв запроса на парковочное место
    """

    @router.callback_query(F.data == CallbackData.REVOKE_REQUEST)
    async def revoke_request_callback(callback: CallbackQuery, state: FSMContext):
        """
            Начало выбора запроса для отзыва
        """
        try:
            await state.clear()
            await choose_request_for_revocation(callback, state)
        except Exception as e:
            await callback.message.edit_text(
                text=f"❌ Ошибка при выборе запроса на отзыв"
                     "<i>Обратитесь к администратору.\nВызовете:/feedback </i>",
                reply_markup=back_to_main_markup
            )
            await log(
                log_message=f"Ошибка в revoke_request_callback: {e}"
            )

    @router.callback_query(F.data.startswith(CallbackData.CONFIRMATION_REVOKE_REQUEST_PREFIX))
    async def confirmation_revoke_request_callback(callback: CallbackQuery, state: FSMContext):
        """
            Ожидание подтверждения отзыва запроса на парковочное место
        """
        try:
            await state.clear()
            request_id = callback.data.replace(CallbackData.CONFIRMATION_REVOKE_REQUEST_PREFIX, "")
            await confirmation_revoke_request(callback, request_id)
        except Exception as e:
            await callback.message.edit_text(
                text=f"❌ Ошибка при выборе даты для отзыва запроса"
                     "<i>Обратитесь к администратору.\nВызовете:/feedback </i>",
                reply_markup=back_to_revoke_request_markup
            )
            await log(
                log_message=f"Ошибка в confirmation_revoke_request_callback: {e}"
            )

    @router.callback_query(F.data.startswith(CallbackData.CONFIRM_REVOKE_REQUEST_PREFIX))
    async def confirm_revoke_request_callback(callback: CallbackQuery, state: FSMContext):
        """
            Отзыв запроса на парковочное место
        """
        try:
            await state.clear()
            request_id = callback.data.replace(CallbackData.CONFIRM_REVOKE_REQUEST_PREFIX, "")
            await confirm_revoke_request(callback, request_id)
        except Exception as e:
            await callback.message.edit_text(
                text="❌ Ошибка подтверждения отзыва запроса на парковочное место"
                     "<i>Обратитесь к администратору.\nВызовете:/feedback </i>",
                reply_markup=back_to_revoke_request_markup
            )
            await log(
                log_message=f"Ошибка в confirm_revoke_request_callback: {e}"
            )

    """
        Отзыв освобожденного места
    """

    @router.callback_query(F.data == CallbackData.REVOKE_RELEASE)
    async def revoke_release_callback(callback: CallbackQuery, state: FSMContext):
        """
            Начало выбора места для отзыва освобождения
        """
        try:
            await state.clear()
            await choose_release_for_revocation(callback)
        except Exception as e:
            await callback.message.edit_text(
                text="❌ Ошибка при выборе места для отзыва освобождения"
                     "<i>Обратитесь к администратору.\nВызовете:/feedback </i>",
                reply_markup=back_to_main_markup
            )
            await log(
                log_message=f"Ошибка в revoke_release_callback: {e}"
            )

    @router.callback_query(F.data.startswith(CallbackData.CONFIRMATION_REVOKE_RELEASE_PREFIX))
    async def confirmation_revoke_release_callback(callback: CallbackQuery, state: FSMContext):
        """
            Ожидание подтверждения отзыва места для освобождения
        """
        try:
            await state.clear()
            release_id = callback.data.replace(CallbackData.CONFIRMATION_REVOKE_RELEASE_PREFIX, "")
            await confirmation_revoke_release(callback, release_id)
        except Exception as e:
            await callback.message.edit_text(
                text=f"❌ Ошибка при подтверждении отзыва места для освобождения"
                     "<i>Обратитесь к администратору.\nВызовете:/feedback </i>",
                reply_markup=back_to_revoke_release_markup
            )
            await log(
                log_message=f"Ошибка в confirmation_revoke_release_callback: {e}"
            )

    @router.callback_query(F.data.startswith(CallbackData.CONFIRM_REVOKE_RELEASE_PREFIX))
    async def confirm_revoke_release_callback(callback: CallbackQuery, state: FSMContext):
        """
            Отзыв освобожденного места
        """
        try:
            await state.clear()
            release_id = callback.data.replace(CallbackData.CONFIRM_REVOKE_RELEASE_PREFIX, "")
            await confirm_revoke_release(callback, release_id)
        except Exception as e:
            await callback.message.edit_text(
                text=f"❌ Ошибка при освобождении места"
                     "<i>Обратитесь к администратору.\nВызовете:/feedback </i>",
                reply_markup=back_to_revoke_release_markup
            )
            await log(
                log_message=f"Ошибка в confirm_revoke_release_callback: {e}"
            )
