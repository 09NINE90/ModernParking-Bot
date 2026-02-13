from aiogram import types

from app.bot.keyboards import back_to_main_markup
from app.bot.utils import get_user_full_mention
from app.config import settings
from app.data import get_db_connection
from app.logs.log_builder import log, LogType
from app.services import ServiceFactory
from app.services.user_service import UserService
from app.utils.emoji_util import statistics_emoji, clock_emoji, sber_arrow_emoji, sber_black_logo_emoji


async def help_command(message: types.Message):
    if message.chat.id == settings.GROUP_ID:
        return

    user = message.from_user
    user_name = await get_user_full_mention(user.id)

    has_access = await UserService.is_user_in_chat(
        user.id,
        settings.GROUP_ID
    )

    if not has_access:
        await log(
            log_type=LogType.WARN,
            log_message=f"Попытка доступа без прав: {user.id} (@{user.username})"
        )
        await message.answer(
            "😔 Вам нельзя пользоваться этим ботом, "
            "так как Вы не состоите в чате парковки офиса."
        )
        return


    with get_db_connection() as conn:
        user_service = ServiceFactory.create_user_service(conn)

        registered = user_service.register_user(user)

        if registered:
            await message.answer(
                text=(
                    f"{sber_black_logo_emoji} <b>Помощь по боту-ассистенту парковки</b>\n\n"

                    "Я ваш личный ассистент парковки в офисе <b>\"Технохаба\"</b>\n"
                    "По адресу: <b>ул. Розы Люксембург 56А</b>\n\n"

                    "📋 <b>Основные возможности:</b>\n"
                    "• Бронирование парковочных мест\n"
                    "• Просмотр доступных мест\n"
                    "• Управление вашими бронированиями\n"
                    "• Получение уведомлений\n"
                    "• Обратная связь\n\n"

                    "🛠 <b>Доступные команды:</b>\n"
                    f"{sber_arrow_emoji} /start - Запуск бота и главное меню\n"
                    f"{sber_arrow_emoji} /help - Инструкция по использованию\n"
                    f"{sber_arrow_emoji} /feedback - Отправить отзыв или предложение\n\n"

                    "🎮 <b>Управление ботом:</b>\n"
                    "Все действия выполняются через кнопки главного меню:\n\n"

                    f"{statistics_emoji} <b>Моя статистика</b>\n"
                    "• Просмотр вашей активности\n"
                    "• История бронирований\n"
                    "• Статистика использования\n\n"

                    "🗓 <b>Освободить место</b>\n"
                    "• Введите номер места, которое хотите освободить\n"
                    "• Укажите дату, когда освободите своё место\n"
                    "• Место автоматически будет предложено или передано пользователям, "
                    "которые сделали запрос места, на указанную Вами дату\n"
                    "• Если место кому-то досталось, Вам придет уведомление об этом\n\n"

                    "🚗 <b>Запросить место</b>\n"
                    "• Выберите дату, когда Вам нужно место\n"
                    "• Система найдет подходящий вариант, если на эту дату есть свободное место\n"
                    "• Если место нашлось, Вам придет уведомление об этом\n\n"

                    "🔄 <b>Управление активностями:</b>\n"
                    "• <b>Отозвать место</b> - вернуть освобожденное место (если его еще никто не занял)\n"
                    "• <b>Отозвать запрос</b> - отменить запрос на место\n\n"

                    f"{clock_emoji} <b>Важно знать:</b>\n"
                    "• Бронирование доступно на рабочие дни (Пн-Пт)\n"
                    "• Можно отозвать свои запросы и освобождения\n"
                    "• Всегда есть кнопка \"Назад\" для возврата\n"
                    "• Используйте \"Главное меню\" для быстрого возврата\n\n"

                    "💡 <b>Советы по использованию:</b>\n"
                    "1. Освобождайте место заранее, если знаете что не приедете\n"
                    "2. Запрашивайте место когда планируете поездку в офис\n"
                    "3. Отзывайте ненужные запросы чтобы не занимать очередь\n"
                    "4. Следите за статистикой для планирования поездок"
                ),
                reply_markup=back_to_main_markup
            )
            await log(
                log_type=LogType.DEBUG,
                log_message=f"Вызвана команда /help:\n{user.id} ({user_name})"
            )
        else:
            await log(log_message=f"Ошибка регистрации пользователя: {user.id}")
            await message.answer(
                "❌ Произошла ошибка при регистрации.\n"
                "Пожалуйста, попробуйте позже."
            )