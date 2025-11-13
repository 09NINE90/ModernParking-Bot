ALTER TABLE dont_touch.parking_requests
    DROP CONSTRAINT IF EXISTS chk_parking_requests_status;

ALTER TABLE dont_touch.parking_requests
    ADD CONSTRAINT chk_parking_requests_status
        CHECK (status IN ('PENDING', 'ACCEPTED', 'CANCELED', 'NOT_FOUND', 'WAITING_CONFIRMATION'));