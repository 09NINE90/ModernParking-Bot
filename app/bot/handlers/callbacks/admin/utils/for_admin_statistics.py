from aiogram.types import CallbackQuery

from app.bot.keyboards import back_to_main_admin, create_stats_period_markup, back_to_stats_period_markup
from app.data import get_db_connection
from app.data.models import ParkingStatsPeriodDTO
from app.services import ServiceFactory
from app.utils.emoji_util import warn_emoji, statistics_emoji, canceled_emoji


async def for_admin_statistics(callback: CallbackQuery):
    tg_user_id = callback.from_user.id

    with get_db_connection() as conn:
        user_service = ServiceFactory.create_user_service(conn)
        statistics_service = ServiceFactory.create_statistics_service(conn)

        is_admin = user_service.is_user_admin(tg_user_id)
        if not is_admin:
            await callback.message.edit_text(
                text=f"{warn_emoji} Вы не админ!",
            )
            return None

        all_stats = statistics_service.get_all_statistics_by_all_time()
        if not all_stats:
            await callback.message.edit_text(
                text=f"{canceled_emoji} Не удалось получить статистику. Попробуйте позже.",
                reply_markup=back_to_main_admin
            )
            return None

        request_stats = all_stats['requests']
        release_stats = all_stats['releases']

        message_text = (
            f"{statistics_emoji} <b>Статистика распределения парковочных мест за все время</b>\n\n"

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

        await callback.message.edit_text(
            text=message_text,
            reply_markup=back_to_main_admin
        )

    return None


async def get_period_stats(callback: CallbackQuery, period_name: str):
    tg_user_id = callback.from_user.id
    period_count = 4
    period_text = ""
    match period_name:
        case "week":
            period_text = "неделю"
            period_count = 4
        case "month":
            period_text = "месяц"
            period_count = 6
        case "quarter":
            period_text = "квартал"
            period_count = 4
        case "year":
            period_text = "год"
            period_count = 2

    with get_db_connection() as conn:
        user_service = ServiceFactory.create_user_service(conn)
        statistics_service = ServiceFactory.create_statistics_service(conn)

        is_admin = user_service.is_user_admin(tg_user_id)
        if not is_admin:
            await callback.message.edit_text(
                text=f"{warn_emoji} Вы не админ!",
            )
            return None

        stats: list[ParkingStatsPeriodDTO] = statistics_service.get_parking_stats_by_period(
            period_type=period_name,
            period_count=period_count
        )

        period_displays: list[str] = []
        for stat in stats:
            period_displays.append(stat.period_display)

        await callback.message.edit_text(
            text=f"Выберите {period_text} для получения статистики",
            reply_markup=create_stats_period_markup(period_name, period_displays)
        )

    return None


async def show_period_stats_details(callback: CallbackQuery, period_name: str, period_display: str):
    tg_user_id = callback.from_user.id

    with get_db_connection() as conn:
        user_service = ServiceFactory.create_user_service(conn)
        statistics_service = ServiceFactory.create_statistics_service(conn)

        is_admin = user_service.is_user_admin(tg_user_id)
        if not is_admin:
            await callback.message.edit_text(f"{warn_emoji} Вы не админ!")
            return

        match period_name:
            case "week":
                period_count = 4
            case "month":
                period_count = 6
            case "quarter":
                period_count = 4
            case "year":
                period_count = 2
            case _:
                await callback.message.edit_text(f"{warn_emoji} Неверный тип периода")
                return

        stats: list[ParkingStatsPeriodDTO] = statistics_service.get_parking_stats_by_period(
            period_type=period_name,
            period_count=period_count,
        )

    stat = next((s for s in stats if s.period_display == period_display), None)
    if not stat:
        await callback.message.edit_text(f"{warn_emoji} Статистика для выбранного периода не найдена")
        return

    text = format_period_stats_message(stat)
    await callback.message.edit_text(
        text=text,
        reply_markup=back_to_stats_period_markup(period_name),
    )


def format_period_stats_message(stat: ParkingStatsPeriodDTO) -> str:
    """
        Формирует текст статистики по одному периоду для отправки в Telegram.
        Использует все поля, возвращаемые get_parking_stats_by_period.
    """
    req_rate = f"{stat.request_success_rate}%" if stat.request_success_rate is not None else "0%"
    rel_rate = f"{stat.release_success_rate}%" if stat.release_success_rate is not None else "0%"

    message_text = (
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

        f"<b>Баланс спроса и предложения:</b>\n"
        f"{stat.market_balance}\n"
    )
    return message_text
