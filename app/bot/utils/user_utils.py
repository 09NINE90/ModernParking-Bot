from app.bot import bot
from app.logs.log_builder import log


async def get_user_full_mention(user_id: int, is_link: bool = False) -> str:
    """
        Возвращает полное обращение с упоминанием или без.
        В формате HTML
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

        if is_link:
            if display_name:
                return f"<a href='tg://user?id={user_id}'>{display_name}</a>"

            if user.username:
                return f"<a href='tg://user?id={user_id}'>@{user.username}</a>"

            return f"<a href='tg://user?id={user_id}'>пользователь #{user_id}</a>"
        else:
            if display_name:
                return display_name

            if user.username:
                return user.username

            return str(user_id)

    except Exception as e:
        await log(log_message=f"Ошибка получения имени пользователя {user_id} e: {e}")
        return f"пользователь #{user_id}"
