CREATE TABLE DEFAULT_SCHEMA.reminder_spot_confirmations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    release_id UUID NULL,
    request_id UUID NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,

    CONSTRAINT fk_reminder_spot_confirmations_user
        FOREIGN KEY (user_id)
        REFERENCES DEFAULT_SCHEMA.users(user_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_reminder_spot_confirmations_release
        FOREIGN KEY (release_id)
        REFERENCES DEFAULT_SCHEMA.parking_releases(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_reminder_spot_confirmations_request
        FOREIGN KEY (request_id)
        REFERENCES DEFAULT_SCHEMA.parking_requests(id)
        ON DELETE SET NULL
);