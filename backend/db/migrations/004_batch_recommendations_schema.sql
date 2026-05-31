-- ============================================================
-- Migration 004: Batch recommendation serving schema
-- ============================================================
-- WHAT: Add batch metadata to stored recommendations.
-- WHY: Batch serving needs to know which model/version generated each row and
-- preserve the rank returned to the API.

ALTER TABLE recommendations
    ADD COLUMN IF NOT EXISTS rank INTEGER,
    ADD COLUMN IF NOT EXISTS model_version VARCHAR(100),
    ADD COLUMN IF NOT EXISTS batch_id VARCHAR(100),
    ADD COLUMN IF NOT EXISTS metadata JSONB;

ALTER TABLE recommendations
    ALTER COLUMN algorithm TYPE VARCHAR(100);

CREATE INDEX IF NOT EXISTS idx_recommendations_user_batch_rank
    ON recommendations(user_id, batch_id, rank);

CREATE INDEX IF NOT EXISTS idx_recommendations_batch
    ON recommendations(batch_id, generated_at DESC);

CREATE UNIQUE INDEX IF NOT EXISTS idx_recommendations_batch_user_report
    ON recommendations(batch_id, user_id, recommended_report_id)
    WHERE batch_id IS NOT NULL;
