import logging

from app.bot import bot

async def get_user_full_mention(user_id: int) -> str:
    """
    Возвращает полное обращение с упоминанием (для кликабельных ссылок)
    """
    try:
        user = await bot.get_chat(user_id)

        display_name = ""
        if user.first_name:
            display_name = user.first_name
        if user.last_name:
            if display_name:
                display_name += f" {user.last_name}"
            else:
                display_name = user.last_name

        if display_name:
            return f"<a href='tg://user?id={user_id}'>{display_name}</a>"

        if user.username:
            return f"<a href='tg://user?id={user_id}'>@{user.username}</a>"

        return f"<a href='tg://user?id={user_id}'>пользователь #{user_id}</a>"

    except Exception as e:
        logging.error(f"Error getting user full mention for {user_id}: {e}")
        return f"пользователь #{user_id}"

async def send_spot_request_assignment_notification(tg_user_id: int, spot_number: int, assignment_date):
    """Отправляет уведомление пользователю о назначении места"""
    user = await get_user_full_mention(tg_user_id)
    try:
        message_text = (
            f"Приветствую, {user}\n\n"
            f"🎉 Вам назначено парковочное место!\n\n"
            f"📍 Место: #{spot_number}\n"
            f"📅 Дата: {assignment_date.strftime('%d.%m.%Y')}\n\n"
            f"Поздравляем с получением места!"
        )

        await bot.send_message(
            chat_id=tg_user_id,
            text=message_text,
            parse_mode='HTML'
        )
        return True
    except Exception as e:
        logging.error(f"Error sending notification to user {tg_user_id}: {e}")
        return False

async def send_spot_release_assignment_notification(tg_user_id: int, spot_number: int, assignment_date):
    """Отправляет уведомление пользователю о назначении места"""
    user = await get_user_full_mention(tg_user_id)
    try:
        message_text = (
            f"Приветствую, {user}\n\n"
            f"✅ Ваше парковочное место назначено!\n\n"
            f"📍 Место: #{spot_number}\n"
            f"📅 Дата: {assignment_date.strftime('%d.%m.%Y')}"
        )

        await bot.send_message(
            chat_id=tg_user_id,
            text=message_text,
            parse_mode='HTML'
        )
        return True
    except Exception as e:
        logging.error(f"Error sending notification to user {tg_user_id}: {e}")
        return False

