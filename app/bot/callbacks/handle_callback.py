from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.callbacks.back_to_main_menu import back_to_main_menu
from app.bot.callbacks.handle_cancel_spot import handle_cancel_spot
from app.bot.callbacks.handle_my_statistics import handle_my_statistics
from app.bot.callbacks.revoke_releases.handle_confirm_revoke_release import handle_confirm_revoke_release
from app.bot.callbacks.revoke_releases.handle_confirmation_revoke_release import handle_confirmation_revoke_release
from app.bot.callbacks.revoke_releases.handle_show_revoke_release_keyboard import handle_show_revoke_release_keyboard
from app.bot.callbacks.revoke_requests.handle_confirm_revoke_request import handle_confirm_revoke_request
from app.bot.callbacks.revoke_requests.handle_confirmation_revoke_request import handle_confirmation_revoke_request
from app.bot.callbacks.revoke_requests.handle_show_revoke_request_keyboard import handle_show_revoke_request_keyboard
from app.bot.callbacks.handle_take_spot import handle_take_spot
from app.bot.callbacks.release_spot import select_spot, process_spot_release
from app.bot.callbacks.request_spot import show_request_calendar, process_spot_request


async def handle_callback(query: CallbackQuery, state: FSMContext):
    data = query.data

    match data:
        case "release_spot":
            await select_spot(query, state)

        case str() if data.startswith("release_date_"):
            date_str = data.replace("release_date_", "")
            await process_spot_release(query, date_str, state)

        case "revoke_release":
            await state.clear()
            await handle_show_revoke_release_keyboard(query, state)

        case str() if data.startswith("confirmation_revoke_release_"):
            await state.clear()
            release_id = data.replace("confirmation_revoke_release_", "")
            await handle_confirmation_revoke_release(query, state, release_id)

        case str() if data.startswith("confirm_revoke_release_"):
            await state.clear()
            release_id = data.replace("confirm_revoke_release_", "")
            await handle_confirm_revoke_release(query, state, release_id)

        case "request_spot":
            await state.clear()
            await show_request_calendar(query, state)

        case str() if data.startswith("request_date_"):
            await state.clear()
            date_str = data.replace("request_date_", "")
            await process_spot_request(query, date_str, state)

        case "revoke_request":
            await state.clear()
            await handle_show_revoke_request_keyboard(query, state)

        case str() if  data.startswith("confirmation_revoke_request_"):
            await state.clear()
            request_id = data.replace("confirmation_revoke_request_", "")
            await handle_confirmation_revoke_request(query, state, request_id)

        case str() if data.startswith("confirm_revoke_request_"):
            await state.clear()
            request_id = data.replace("confirm_revoke_request_", "")
            await handle_confirm_revoke_request(query, state, request_id)

        case "back_to_main":
            await state.clear()
            await back_to_main_menu(query)

        case "take_spot":
            await state.clear()
            await handle_take_spot(query, state)

        case "cancel_spot":
            await state.clear()
            await handle_cancel_spot(query, state)

        case "my_statistics":
            await state.clear()
            await handle_my_statistics(query)
