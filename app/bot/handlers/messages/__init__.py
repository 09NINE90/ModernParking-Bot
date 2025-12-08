from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.bot.handlers.callbacks.utils.feedback_utils import handle_write_feedback
from app.bot.parking_states import ParkingStates
from app.bot.handlers.callbacks.utils.release_spots_utils import handle_spot_number


def setup_messages(router: Router) -> None:
    """Настройка обработчиков сообщений"""

    @router.message(ParkingStates.waiting_for_spot_number)
    async def handle_spot_number_message(message: Message, state: FSMContext):
        await handle_spot_number(message, state)

    @router.message(ParkingStates.waiting_for_feedback)
    async def handle_feedback_message(message: Message, state: FSMContext):
        await handle_write_feedback(message, state)
