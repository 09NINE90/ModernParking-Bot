from app.data.repository.users_repository import get_user_id_by_tg_id, decrement_user_rating


async def get_db_user_id(cur, tg_user_id):
    user_record = await get_user_id_by_tg_id(cur, tg_user_id)

    if not user_record:
        return None

    return user_record[0]

async def decrement_user_rating_of_1(cur, db_user_id):
    result = await decrement_user_rating(cur, db_user_id)
    if not result:
        return False
    return result[0] is not None