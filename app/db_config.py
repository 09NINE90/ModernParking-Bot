import os

import psycopg2

from dotenv import load_dotenv

load_dotenv()
DATABASE_CONFIG = {
    "dbname": os.environ.get("DB_NAME"),
    "host": os.environ.get("DB_HOST"),
    "port": int(os.environ.get("DB_PORT")),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
}

def init_database():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    try:
        create_tables(conn)
    finally:
        conn.close()

async def create_tables(conn):
    with conn.cursor() as cur:
        cur.execute("""
                    -- Таблица пользователей
                    CREATE TABLE IF NOT EXISTS dont_touch.users
                    (
                        user_id    UUID    NOT NULL PRIMARY KEY,
                        tg_id      INTEGER NOT NULL UNIQUE,
                        status     BOOLEAN   DEFAULT TRUE,
                        rating     INTEGER   DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    -- Таблица парковочных мест
                    CREATE TABLE IF NOT EXISTS dont_touch.parking_spots
                    (
                        spot_id      INTEGER NOT NULL PRIMARY KEY,
                        is_active    BOOLEAN DEFAULT FALSE,
                        floor_number INTEGER
                    );

                    -- Таблица запросов на парковку
                    CREATE TABLE IF NOT EXISTS dont_touch.parking_requests
                    (
                        id           UUID NOT NULL PRIMARY KEY,
                        user_id      UUID NOT NULL,
                        request_date DATE NOT NULL,
                        status       VARCHAR(20) DEFAULT 'PENDING',
                        created_at   TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
                        processed_at TIMESTAMP,

                        CONSTRAINT fk_parking_requests_user_id
                            FOREIGN KEY (user_id)
                                REFERENCES dont_touch.users
                                ON DELETE CASCADE,

                        CONSTRAINT chk_parking_requests_status
                            CHECK (status IN ('PENDING', 'ACCEPT', 'CANCELED', 'NOT FOUND'))
                    );

                    -- Таблица освобожденных мест
                    CREATE TABLE IF NOT EXISTS dont_touch.parking_releases
                    (
                        id           UUID    NOT NULL PRIMARY KEY,
                        user_id      UUID    NOT NULL,
                        spot_id      INTEGER NOT NULL,
                        release_date DATE    NOT NULL,
                        created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        user_id_took UUID,

                        CONSTRAINT fk_parking_releases_user_id
                            FOREIGN KEY (user_id)
                                REFERENCES dont_touch.users
                                ON DELETE CASCADE,

                        CONSTRAINT fk_parking_releases_spot_id
                            FOREIGN KEY (spot_id)
                                REFERENCES dont_touch.parking_spots
                                ON DELETE CASCADE,

                        CONSTRAINT fk_parking_releases_user_id_took
                            FOREIGN KEY (user_id_took)
                                REFERENCES dont_touch.users
                                ON DELETE SET NULL
                    );

                    -- Создание индексов для улучшения производительности
                    CREATE INDEX IF NOT EXISTS idx_users_tg_id ON dont_touch.users (tg_id);
                    CREATE INDEX IF NOT EXISTS idx_parking_requests_user_date ON dont_touch.parking_requests (user_id, request_date);
                    CREATE INDEX IF NOT EXISTS idx_parking_requests_status ON dont_touch.parking_requests (status);
                    CREATE INDEX IF NOT EXISTS idx_parking_releases_date ON dont_touch.parking_releases (release_date);
                    CREATE INDEX IF NOT EXISTS idx_parking_releases_spot_date ON dont_touch.parking_releases (spot_id, release_date);
                    """)
        conn.commit()