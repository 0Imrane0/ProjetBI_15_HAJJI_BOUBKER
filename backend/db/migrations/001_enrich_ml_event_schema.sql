-- Enrich event storage for ML features, idempotence, and debugging.

ALTER TABLE reports
    ADD COLUMN IF NOT EXISTS business_category VARCHAR(100);

ALTER TABLE navigation_logs
    ADD COLUMN IF NOT EXISTS source_event_id INTEGER,
    ADD COLUMN IF NOT EXISTS event_type VARCHAR(50) NOT NULL DEFAULT 'view',
    ADD COLUMN IF NOT EXISTS duration_source VARCHAR(50) DEFAULT 'unknown',
    ADD COLUMN IF NOT EXISTS metabase_model VARCHAR(50),
    ADD COLUMN IF NOT EXISTS metabase_model_id INTEGER,
    ADD COLUMN IF NOT EXISTS session_id VARCHAR(100),
    ADD COLUMN IF NOT EXISTS raw_payload JSONB;

UPDATE navigation_logs
SET
    event_type = COALESCE(event_type, action, 'view'),
    duration_source = CASE
        WHEN duration IS NULL OR duration = 0 THEN COALESCE(duration_source, 'unknown')
        ELSE COALESCE(duration_source, 'legacy')
    END;

CREATE UNIQUE INDEX IF NOT EXISTS idx_nav_logs_source_event_id
    ON navigation_logs(source_event_id)
    WHERE source_event_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_nav_logs_event_type
    ON navigation_logs(event_type);

CREATE INDEX IF NOT EXISTS idx_reports_business_category
    ON reports(business_category);
