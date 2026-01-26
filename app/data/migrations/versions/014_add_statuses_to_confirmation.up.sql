ALTER TABLE DEFAULT_SCHEMA.spot_confirmations
    ADD COLUMN status text NOT NULL DEFAULT 'WAITING'
        CONSTRAINT chk_parking_requests_status
            CHECK (status IN ('CANCELLED', 'ACCEPTED', 'WAITING', 'REJECTED'));
