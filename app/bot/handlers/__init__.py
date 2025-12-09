from aiogram import Dispatcher


def setup_handlers(dp: Dispatcher):
    """Регистрация всех обработчиков"""
    from .commands import setup_commands
    from .callbacks import setup_callbacks
    from .messages import setup_messages

    setup_commands(dp)
    setup_callbacks(dp)
    setup_messages(dp)