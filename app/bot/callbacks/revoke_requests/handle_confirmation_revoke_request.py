from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.service.requests.revoke_request_service import confirmation_revoke_request


async def handle_confirmation_revoke_request(query: CallbackQuery, state: FSMContext, request_id):
    await confirmation_revoke_request(query, state, request_id)