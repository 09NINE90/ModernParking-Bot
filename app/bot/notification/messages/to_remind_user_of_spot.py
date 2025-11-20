async def to_remind_user_of_spot(spot_id: int):
    message_text = (
        f"🔔 <b>Напоминание</b>\n"
        f"На завтра Вам забронировано место <b>№{spot_id}</b>"
    )

    return message_text
