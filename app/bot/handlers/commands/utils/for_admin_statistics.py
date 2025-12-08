from aiogram import types

from app.data import get_db_connection
from app.services import ServiceFactory


async def for_admin_statistics(message: types.Message):
    tg_user_id = message.from_user.id

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            user_service = ServiceFactory.create_user_service(conn)
            statistics_service = ServiceFactory.create_statistics_service(conn)

            is_admin = user_service.is_user_admin(tg_user_id)
            if not is_admin:
                return None

            all_stats = statistics_service.get_all_statistics_by_all_time()
            if not all_stats:
                await message.answer("❌ Не удалось получить статистику. Попробуйте позже.")
                return None

            request_stats = all_stats['requests']
            release_stats = all_stats['releases']

            message_text = (
                f"📊 <b>Статистика распределения парковочных мест за все время</b>\n\n"

                f"<b>Освобождение мест:</b>\n"
                f"┌ Всего освобождено: <b>{release_stats['total']}</b>\n"
                f"├ Мест отдано: <b>{release_stats['accepted']}</b>\n"
                f"├ Ожидание распределения: <b>{release_stats['pending']}</b>\n"
                f"├ Отозвали мест: <b>{release_stats['canceled']}</b>\n"
                f"├ Не нашлось, кому отдать: <b>{release_stats['not_found']}</b>\n"
                f"├ Ожидание подтверждения: <b>{release_stats['waiting']}</b>\n"
                f"└ Процент успешно отданных мест: <b>{release_stats['acceptance_rate']}%</b>\n\n"

                f"<b>Запросы мест:</b>\n"
                f"┌ Всего запросов: <b>{request_stats['total']}</b>\n"
                f"├ Мест принято: <b>{request_stats['accepted']}</b>\n"
                f"├ Ожидание распределения: <b>{request_stats['pending']}</b>\n"
                f"├ Отозвали запрос: <b>{request_stats['canceled']}</b>\n"
                f"├ Не найдено мест: <b>{request_stats['not_found']}</b>\n"
                f"├ Ожидание подтверждения: <b>{request_stats['waiting_confirmation']}</b>\n"
                f"└ Процент отмененных запросов: <b>{request_stats['cancel_rate']}%</b>\n"

            )

            await message.answer(message_text)

    return None
