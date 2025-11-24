ALTER TABLE DEFAULT_SCHEMA.parking_requests
    DROP CONSTRAINT IF EXISTS chk_parking_requests_status;

UPDATE DEFAULT_SCHEMA.parking_requests
SET status='ACCEPTED'
WHERE status = 'ACCEPT';

UPDATE DEFAULT_SCHEMA.parking_requests
SET status='NOT_FOUND'
WHERE status = 'NOT FOUND';

ALTER TABLE DEFAULT_SCHEMA.parking_requests
    ADD CONSTRAINT chk_parking_requests_status
        CHECK (status IN ('PENDING', 'ACCEPTED', 'CANCELED', 'NOT_FOUND'));

ALTER TABLE DEFAULT_SCHEMA.parking_releases
    ADD COLUMN status VARCHAR(20) default 'PENDING',
    ADD CONSTRAINT chk_parking_releases_status
        CHECK (status IN ('PENDING', 'ACCEPTED', 'CANCELED', 'NOT_FOUND', 'WAITING'));

UPDATE DEFAULT_SCHEMA.parking_releases
SET status='PENDING'
WHERE user_id_took IS NULL;

UPDATE DEFAULT_SCHEMA.parking_releases
SET status='ACCEPTED'
WHERE user_id_took IS NOT NULL;