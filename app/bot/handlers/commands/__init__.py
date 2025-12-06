from aiogram import Dispatcher
from aiogram.filters import CommandStart, Command


def setup_commands(dp: Dispatcher):
    """Регистрация команд"""

    from .chat_info import chat_info
    from .start import start_command
    from .help import help_command

    dp.message.register(start_command, CommandStart())
    dp.message.register(chat_info, Command("get_chat_info"))
    dp.message.register(help_command, Command("help"))
    # dp.message.register(feedback_command, Command("feedback"))
    # dp.message.register(statistics_command, Command("statistics"))
