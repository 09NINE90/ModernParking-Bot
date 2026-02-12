from app.config import settings
from app.data import get_db_connection
from app.data.models import ParkingStatsPeriodDTO
from app.services import ServiceFactory
from app.utils.emoji_util import statistics_emoji


async def send_quarter_report():
    with get_db_connection() as conn:
        statistics_service = ServiceFactory.create_statistics_service(conn)

        stats: list[ParkingStatsPeriodDTO] = statistics_service.get_parking_stats_by_period(
            period_type="quarter",
            period_count=1
        )

        message_text = format_period_stats_message(stats[0])

        from app.bot import bot
        await bot.send_message(
            text=message_text,
            chat_id=settings.GROUP_ID,
        )


def format_period_stats_message(stat: ParkingStatsPeriodDTO) -> str:
    """
        Формирует текст статистики по одному периоду для отправки в Telegram.
        Использует все поля, возвращаемые get_parking_stats_by_period.
    """
    req_rate = f"{stat.request_success_rate}%" if stat.request_success_rate is not None else "0%"
    rel_rate = f"{stat.release_success_rate}%" if stat.release_success_rate is not None else "0%"

    message_text = (
        "Всем привет!\n\n"
        f"{statistics_emoji} <b>Статистика распределения парковочных мест за период {stat.period_display}</b>\n\n"

        f"<b>Освобождение мест:</b>\n"
        f"┌ Всего освобождено: <b>{stat.total_releases}</b>\n"
        f"├ Мест отдано: <b>{stat.accepted_releases}</b>\n"
        f"├ Ожидание распределения: <b>{stat.pending_releases}</b>\n"
        f"├ Отозвали мест: <b>{stat.canceled_releases}</b>\n"
        f"├ Не нашлось, кому отдать: <b>{stat.not_found_releases}</b>\n"
        f"├ Ожидание подтверждения: <b>{stat.waiting_releases}</b>\n"
        f"└ Процент успешно отданных мест: <b>{rel_rate}</b>\n\n"

        f"<b>Запросы мест:</b>\n"
        f"┌ Всего запросов: <b>{stat.total_requests}</b>\n"
        f"├ Мест принято: <b>{stat.accepted_requests}</b>\n"
        f"├ Ожидание распределения: <b>{stat.pending_requests}</b>\n"
        f"├ Отозвали запрос: <b>{stat.canceled_requests}</b>\n"
        f"├ Не найдено мест: <b>{stat.not_found_requests}</b>\n"
        f"├ Ожидание подтверждения: <b>{stat.waiting_confirmation_requests}</b>\n"
        f"└ Процент успешных запросов: <b>{req_rate}</b>\n\n"

        f"<b>Уникальные участники и места:</b>\n"
        f"┌ Уникальных запрашивающих: <b>{stat.unique_requesters}</b>\n"
        f"├ Уникальных освобождающих: <b>{stat.unique_releasers}</b>\n"
        f"├ Уникальных получателей: <b>{stat.unique_recipients}</b>\n"
        f"└ Уникальных мест: <b>{stat.unique_spots_released}</b>\n\n"
    )
    return message_text
