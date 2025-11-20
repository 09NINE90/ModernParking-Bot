from aiogram.filters import Command

from app.bot.callbacks.handle_callback import handle_callback
from app.bot.callbacks.handle_feedback import handle_write_feedback
from app.bot.callbacks.release_spot import handle_spot_number
from app.bot.commands.feedback import feedback
from app.bot.commands.help import help_command
from app.bot.commands.start import start
from app.bot.commands.statistics import statistics
from app.bot.commands.weekly_statistics import weekly_statistics
from app.bot.parking_states import ParkingStates


def register_handlers(router):
    router.message.register(start, Command("start"))
    router.message.register(help_command, Command("help"))
    router.message.register(feedback, Command("feedback"))
    # router.message.register(statistics, Command("statistics"))
    router.message.register(weekly_statistics, Command("weekly_statistics"))
    router.message.register(handle_spot_number, ParkingStates.waiting_for_spot_number)
    router.message.register(handle_write_feedback, ParkingStates.waiting_for_feedback)
    router.callback_query.register(handle_callback)