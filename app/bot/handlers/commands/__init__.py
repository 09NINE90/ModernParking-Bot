from aiogram import Dispatcher
from aiogram.filters import CommandStart, Command


def setup_commands(dp: Dispatcher):
    """Регистрация команд"""

    from .start import start_command
    from .help import help_command
    from .feedback import feedback_command
    from .admin import admin_command

    dp.message.register(start_command, CommandStart())
    dp.message.register(help_command, Command("help"))
    dp.message.register(feedback_command, Command("feedback"))
    dp.message.register(admin_command, Command("admin"))