from app.data.models import ParkingReminder


async def to_remind_user_of_spot(remind_data: ParkingReminder):
    from app.scheduler.scheduler_manager import schedule_reminder_cancellation
    cancel_time = await schedule_reminder_cancellation(reminder_data=remind_data)

    message_text = (
        f"🔔 <b>Напоминание</b>\n"
        f"На завтра <u>{remind_data.release_date.strftime('%d.%m.%Y')}</u> Вам забронировано место <b>№{remind_data.spot_id}</b>\n\n"
        f"ℹ️ <i>Успейте подтвердить место до <u>{cancel_time.strftime('%d.%m %H:%M')}</u> "
        f"иначе оно автоматически уйдет другому человеку</i>"
    )

    return message_text