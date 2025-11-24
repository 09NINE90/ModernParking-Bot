-- Создание схемы если не существует
CREATE SCHEMA IF NOT EXISTS DEFAULT_SCHEMA;

-- Таблица пользователей
CREATE TABLE IF NOT EXISTS DEFAULT_SCHEMA.users
(
    user_id    UUID    NOT NULL PRIMARY KEY,
    tg_id      INTEGER NOT NULL UNIQUE,
    status     BOOLEAN   DEFAULT TRUE,
    rating     INTEGER   DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица парковочных мест
CREATE TABLE IF NOT EXISTS DEFAULT_SCHEMA.parking_spots
(
    spot_id      INTEGER NOT NULL PRIMARY KEY,
    is_active    BOOLEAN DEFAULT FALSE,
    floor_number INTEGER
);

-- Заполнение парковочных мест
INSERT INTO DEFAULT_SCHEMA.parking_spots (spot_id, floor_number)
SELECT
    g as spot_id,
    CASE
        WHEN g BETWEEN 3 AND 41 THEN 2
        WHEN g BETWEEN 42 AND 85 THEN 3
        WHEN g BETWEEN 86 AND 129 THEN 4
        WHEN g BETWEEN 130 AND 173 THEN 5
    END as floor_number
FROM generate_series(3, 173) AS g
WHERE NOT EXISTS (SELECT 1 FROM DEFAULT_SCHEMA.parking_spots);

-- Таблица запросов на парковку
CREATE TABLE IF NOT EXISTS DEFAULT_SCHEMA.parking_requests
(
    id           UUID NOT NULL PRIMARY KEY,
    user_id      UUID NOT NULL,
    request_date DATE NOT NULL,
    status       VARCHAR(20) DEFAULT 'PENDING',
    created_at   TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,

    CONSTRAINT fk_parking_requests_user_id
        FOREIGN KEY (user_id)
            REFERENCES DEFAULT_SCHEMA.users
            ON DELETE CASCADE,

    CONSTRAINT chk_parking_requests_status
        CHECK (status IN ('PENDING', 'ACCEPT', 'CANCELED', 'NOT FOUND'))
);

-- Таблица освобожденных мест
CREATE TABLE IF NOT EXISTS DEFAULT_SCHEMA.parking_releases
(
    id           UUID    NOT NULL PRIMARY KEY,
    user_id      UUID    NOT NULL,
    spot_id      INTEGER NOT NULL,
    release_date DATE    NOT NULL,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id_took UUID,

    CONSTRAINT fk_parking_releases_user_id
        FOREIGN KEY (user_id)
            REFERENCES DEFAULT_SCHEMA.users
            ON DELETE CASCADE,

    CONSTRAINT fk_parking_releases_spot_id
        FOREIGN KEY (spot_id)
            REFERENCES DEFAULT_SCHEMA.parking_spots
            ON DELETE CASCADE,

    CONSTRAINT fk_parking_releases_user_id_took
        FOREIGN KEY (user_id_took)
            REFERENCES DEFAULT_SCHEMA.users
            ON DELETE SET NULL
);

-- Индексы
CREATE UNIQUE INDEX IF NOT EXISTS uniq_user_id_request_date
ON DEFAULT_SCHEMA.parking_requests(user_id, request_date);

CREATE UNIQUE INDEX IF NOT EXISTS uniq_spot_id_releases_date
ON DEFAULT_SCHEMA.parking_releases(spot_id, release_date);

CREATE INDEX IF NOT EXISTS idx_users_tg_id ON DEFAULT_SCHEMA.users (tg_id);
CREATE INDEX IF NOT EXISTS idx_parking_requests_user_date ON DEFAULT_SCHEMA.parking_requests (user_id, request_date);
CREATE INDEX IF NOT EXISTS idx_parking_requests_status ON DEFAULT_SCHEMA.parking_requests (status);
CREATE INDEX IF NOT EXISTS idx_parking_releases_date ON DEFAULT_SCHEMA.parking_releases (release_date);
CREATE INDEX IF NOT EXISTS idx_parking_releases_spot_date ON DEFAULT_SCHEMA.parking_releases (spot_id, release_date);