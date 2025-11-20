from aiogram.fsm.state import State, StatesGroup

class ParkingStates(StatesGroup):
    waiting_for_spot_number = State()
    waiting_for_feedback = State()