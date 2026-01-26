UPDATE DEFAULT_SCHEMA.spot_confirmations AS sc
SET status     = 'ACCEPTED',
    updated_at = CURRENT_TIMESTAMP
WHERE sc.id IN (SELECT sc2.id
                FROM DEFAULT_SCHEMA.spot_confirmations sc2
                         JOIN DEFAULT_SCHEMA.parking_requests pr
                              ON pr.id = sc2.request_id
                         JOIN DEFAULT_SCHEMA.parking_releases prl
                              ON prl.id = sc2.release_id
                WHERE pr.status = 'ACCEPTED'
                  AND prl.status = 'ACCEPTED'
                  AND pr.user_id = prl.user_id_took);

UPDATE DEFAULT_SCHEMA.spot_confirmations
SET status     = 'CANCELLED',
    updated_at = CURRENT_TIMESTAMP
WHERE is_active = FALSE
  AND status = 'WAITING';

ALTER TABLE DEFAULT_SCHEMA.spot_confirmations
    DROP COLUMN is_active;
