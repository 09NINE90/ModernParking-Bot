from aiogram import types


async def chat_info(message: types.Message):
    """Получаем информацию о чате/топике"""
    chat_info = f"""
    📋 Информация о чате:

    ID чата: `{message.chat.id}`
    Тип чата: {message.chat.type}
    Название: {message.chat.title or 'Нет названия'}
    Username: @{message.chat.username or 'Нет username'}

    📝 Информация о сообщении:

    ID сообщения: {message.message_id}
    ID топика: {message.message_thread_id or 'Не топик'}
    Дата: {message.date}
    """

    # Если это топик в форуме
    if message.message_thread_id:
        chat_info += f"\n🎯 Это топик в форуме! ID топика: `{message.message_thread_id}`"

    await message.answer(chat_info, parse_mode="Markdown")