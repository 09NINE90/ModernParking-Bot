from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.service.release.revoke_release_service import confirm_revoke_release


async def handle_confirm_revoke_release(query: CallbackQuery, state: FSMContext, release_id):
    await confirm_revoke_release(query, state, release_id)