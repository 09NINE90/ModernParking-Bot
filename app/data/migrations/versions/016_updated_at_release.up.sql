ALTER TABLE DEFAULT_SCHEMA.parking_releases
    ADD COLUMN IF NOT EXISTS updated_at timestamp;

UPDATE DEFAULT_SCHEMA.parking_releases prl
SET updated_at = COALESCE(req.processed_at, prl.created_at)
FROM DEFAULT_SCHEMA.parking_requests req
WHERE prl.user_id_took = req.user_id
  AND prl.release_date = req.request_date
  AND prl.updated_at IS NULL;

UPDATE DEFAULT_SCHEMA.parking_releases
SET updated_at = created_at
WHERE updated_at IS NULL;

ALTER TABLE DEFAULT_SCHEMA.parking_releases
    ALTER COLUMN updated_at SET NOT NULL;

ALTER TABLE DEFAULT_SCHEMA.parking_releases
    ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP;

COMMENT ON COLUMN DEFAULT_SCHEMA.parking_releases.updated_at IS 'Дата и время последнего обновления записи';
COMMENT ON COLUMN DEFAULT_SCHEMA.spot_confirmations.status IS 'Статус записи подтверждения';


