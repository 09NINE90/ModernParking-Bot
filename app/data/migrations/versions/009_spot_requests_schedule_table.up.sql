CREATE TABLE IF NOT EXISTS DEFAULT_SCHEMA.spot_requests_schedule
(
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL,
    day_numbers varchar(15),
    created_at  TIMESTAMP        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_spot_requests_schedule_user FOREIGN KEY (user_id)
        REFERENCES DEFAULT_SCHEMA.users (user_id)
        ON DELETE SET NULL,

    CONSTRAINT uk_spot_requests_schedule_user_day UNIQUE (user_id, day_numbers)
)