from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.callbacks.back_to_main_menu import back_to_main_menu
from app.bot.callbacks.handle_cancel_spot import handle_cancel_spot
from app.bot.callbacks.handle_take_spot import handle_take_spot
from app.bot.callbacks.release_spot import select_spot, process_spot_release
from app.bot.callbacks.request_spot import show_request_calendar, process_spot_request


async def handle_callback(query: CallbackQuery, state: FSMContext):
    data = query.data

    current_state = await state.get_state()
    print(f"current_state: {current_state}")

    match data:
        case "release_spot":
            await select_spot(query, state)

        case str() if data.startswith("release_date_"):
            date_str = data.replace("release_date_", "")
            await process_spot_release(query, date_str, state)

        case "request_spot":
            await show_request_calendar(query, state)

        case str() if data.startswith("request_date_"):
            date_str = data.replace("request_date_", "")
            await process_spot_request(query, date_str, state)

        case "back_to_main":
            await back_to_main_menu(query)

        case "take_spot":
            await handle_take_spot(query, state)

        case "cancel_spot":
            await handle_cancel_spot(query, state)
