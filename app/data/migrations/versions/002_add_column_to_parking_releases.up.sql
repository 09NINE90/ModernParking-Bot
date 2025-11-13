ALTER TABLE dont_touch.parking_requests
    DROP CONSTRAINT IF EXISTS chk_parking_requests_status;

UPDATE dont_touch.parking_requests
SET status='ACCEPTED'
WHERE status = 'ACCEPT';

UPDATE dont_touch.parking_requests
SET status='NOT_FOUND'
WHERE status = 'NOT FOUND';

ALTER TABLE dont_touch.parking_requests
    ADD CONSTRAINT chk_parking_requests_status
        CHECK (status IN ('PENDING', 'ACCEPTED', 'CANCELED', 'NOT_FOUND'));

ALTER TABLE dont_touch.parking_releases
    ADD COLUMN status VARCHAR(20) default 'PENDING',
    ADD CONSTRAINT chk_parking_releases_status
        CHECK (status IN ('PENDING', 'ACCEPTED', 'CANCELED', 'NOT_FOUND', 'WAITING'));

UPDATE dont_touch.parking_releases
SET status='PENDING'
WHERE user_id_took IS NULL;

UPDATE dont_touch.parking_releases
SET status='ACCEPTED'
WHERE user_id_took IS NOT NULL;