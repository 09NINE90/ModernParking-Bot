from app.data.repository.users_repository import get_user_id_by_tg_id, minus_one_user_rating_by_id


async def get_db_user_id(cur, tg_user_id):
    user_record = await get_user_id_by_tg_id(cur, tg_user_id)

    if not user_record:
        return None

    return user_record[0]

async def minus_one_user_rating(cur, db_user_id):
    user_id = await minus_one_user_rating_by_id(cur, db_user_id)
    if not user_id:
        return False
    return True