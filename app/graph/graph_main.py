import os

import psycopg2
import pandas as pd

from app.data.migrations import get_connection
from app.graph.get_quarter import get_current_quarter_and_year
from app.graph.graph_drawing import draw_linear_graph, draw_bar_graph

conn = get_connection()
sql_request = """
              WITH all_dates AS (
    SELECT DISTINCT request_date
    FROM dont_touch.parking_requests
),
     accepted AS (
         SELECT request_date, count(*) AS accepted_count
         FROM dont_touch.parking_requests
         WHERE status = 'ACCEPTED'
         GROUP BY request_date
     ),
     canceled AS (
         SELECT request_date, count(*) AS canceled_count
         FROM dont_touch.parking_requests
         WHERE status = 'CANCELED'
         GROUP BY request_date
     ),
     pending AS (
         SELECT request_date, count(*) AS pending_count
         FROM dont_touch.parking_requests
         WHERE status = 'PENDING'
         GROUP BY request_date
     )

SELECT
    d.request_date AS date,
    COALESCE(a.accepted_count, 0) AS accepted_count,
    COALESCE(c.canceled_count, 0) AS canceled_count,
    COALESCE(p.pending_count, 0) AS pending_count
FROM all_dates d
         LEFT JOIN accepted a ON a.request_date = d.request_date
         LEFT JOIN canceled c ON c.request_date = d.request_date
         LEFT JOIN pending p ON p.request_date = d.request_date
ORDER BY d.request_date;
              """

df = pd.read_sql(sql_request, conn)
conn.close()
os.makedirs(get_current_quarter_and_year(), exist_ok=True)

draw_linear_graph("График значений",
                  "Дата",
                  "Значение",
                  f"{get_current_quarter_and_year()}/metric.png",
                  [df["date"]], [df["accepted_count"], df["canceled_count"],df["pending_count"]],
                  ["r-", "b--", "g--"],
                  ["принято","отменено","ожидает"]
                  )


draw_bar_graph("Статусы заявок по датам",
               df["date"],
               [df["accepted_count"], df["canceled_count"], df["pending_count"]],
               ["Принято","Отменено","Ожидает"],
               f"{get_current_quarter_and_year()}/metric2.png"
               )