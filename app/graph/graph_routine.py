import asyncio
import os
from datetime import datetime

import pandas as pd

from app.bot.config import bot
from app.data.migrations import get_connection
from app.graph.enrich_df_with_usernames import enrich_df_with_usernames
from app.graph.get_quarter import get_current_quarter_and_year, get_previous_quarter_and_year, \
    get_first_and_last_quarter_dates
from app.graph.graph_drawing import draw_bar_graph

users_current_stat_sql_query = "SELECT tg_id as users, rating FROM dont_touch.users"


def spot_stat_sql_query(first_date, last_date):
    return f"""
select spot_id as spot, count(*) as rating from dont_touch.parking_releases
where release_date>='{first_date}' and release_date<'{last_date}'
group by spot_id
order by spot_id
"""


# Мето
async def get_current_report():
    current_quarter_and_year = get_current_quarter_and_year()
    os.makedirs(current_quarter_and_year, exist_ok=True)
    conn = get_connection()

    await get_spot_report(spot_stat_sql_query(get_first_and_last_quarter_dates(current_quarter_and_year).first_date, get_first_and_last_quarter_dates(current_quarter_and_year).last_date), conn, "current")
    await get_user_report(users_current_stat_sql_query, conn, "current")


async def get_user_report(sql_query, conn, type):
    df = pd.read_sql(sql_query, conn)
    df = await enrich_df_with_usernames(df, bot)
    return_file = f"{get_current_quarter_and_year()}/user_stat-{datetime.now()}.png"
    title = "Актуальный рейтинг пользователей"
    if type == "quarter":
        return_file = f"{get_previous_quarter_and_year()}/user_stat-final.png"
        title = "Рейтинг пользователей за прошедший квартал"

    draw_bar_graph(title,
                   df["users"],
                   [df["rating"]],
                   ["Пользователь"],
                   return_file
                   )



async def get_spot_report(sql_query, conn, type):
    df = pd.read_sql(sql_query, conn)
    return_file = f"{get_current_quarter_and_year()}/spot_stat-{datetime.now()}.png"
    title = "Актуальный рейтинг парковочных мест"
    if type == "quarter":
        return_file = f"{get_previous_quarter_and_year()}/spot_stat-final.png"
        title = "Рейтинг мест за прошедший квартал"

    draw_bar_graph(title,
                   df["spot"],
                   [df["rating"]],
                   ["Место"],
                   return_file
                   )

async def main():
    try:
        await get_current_report()
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())