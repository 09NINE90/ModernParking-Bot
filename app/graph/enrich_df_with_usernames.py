import pandas as pd
from aiogram.exceptions import TelegramBadRequest


async def enrich_df_with_usernames(df, bot):
    usernames = []

    for tg_id in df["users"]:
        try:
            chat = await bot.get_chat(tg_id)
            usernames.append(chat.username or f"id_{tg_id}")
        except TelegramBadRequest:
            usernames.append(f"{tg_id}")
        except Exception as e:
            usernames.append(f"error_{tg_id}")
            print(f"Error processing tg_id {tg_id}: {e}")

    df["users"] = usernames
    return df