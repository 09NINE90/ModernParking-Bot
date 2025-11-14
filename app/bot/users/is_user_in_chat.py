from aiogram.enums import ChatMemberStatus

from app.bot.config import bot


async def is_user_in_chat(user_tg_id: int, group_id: int) -> bool:
    """
    Проверяет, является ли пользователь участником канала/группы
    """
    try:
        member = await bot.get_chat_member(
            chat_id=group_id,
            user_id=user_tg_id
        )
        valid_statuses = [
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR
        ]
        return member.status in valid_statuses

    except Exception as e:
        print(f"Ошибка при проверке участника: {e}")
        return False