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