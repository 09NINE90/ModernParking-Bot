from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.service.requests.revoke_request_service import confirm_revoke_request


async def handle_confirm_revoke_request(query: CallbackQuery, state: FSMContext, request_id):
    await confirm_revoke_request(query, state, request_id)