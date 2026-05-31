-- ============================================================
-- BI Adaptive - Database Schema
-- ============================================================

-- ============ TABLES ============

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    metabase_user_id INTEGER UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    role VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    metabase_report_id INTEGER UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    tags VARCHAR(500),
    category VARCHAR(100),
    business_category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS navigation_logs (
    id SERIAL PRIMARY KEY,
    source_event_id INTEGER,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    report_id INTEGER NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL DEFAULT 'view',
    event_type VARCHAR(50) NOT NULL DEFAULT 'view',
    duration INTEGER DEFAULT 0,
    duration_source VARCHAR(50) DEFAULT 'unknown',
    metabase_model VARCHAR(50),
    metabase_model_id INTEGER,
    session_id VARCHAR(100),
    raw_payload JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recommended_report_id INTEGER NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    rank INTEGER,
    score FLOAT DEFAULT 0.0,
    algorithm VARCHAR(100),
    model_version VARCHAR(100),
    batch_id VARCHAR(100),
    metadata JSONB,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    clicked BOOLEAN DEFAULT FALSE
);

-- Multi-cursor state: one row per stream, survives container restarts
CREATE TABLE IF NOT EXISTS publisher_state (stream VARCHAR(50) PRIMARY KEY, last_id INTEGER DEFAULT 0, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

INSERT INTO publisher_state VALUES ('recent_views',0,NOW()),('core_user',0,NOW()),('report_card',0,NOW());


-- ============ INDEXES ============

CREATE INDEX IF NOT EXISTS idx_nav_logs_user_ts    ON navigation_logs(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_nav_logs_report     ON navigation_logs(report_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_nav_logs_source_event_id ON navigation_logs(source_event_id) WHERE source_event_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_nav_logs_event_type ON navigation_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_recommendations_user ON recommendations(user_id, generated_at DESC);
CREATE INDEX IF NOT EXISTS idx_recommendations_user_batch_rank ON recommendations(user_id, batch_id, rank);
CREATE INDEX IF NOT EXISTS idx_recommendations_batch ON recommendations(batch_id, generated_at DESC);
CREATE UNIQUE INDEX IF NOT EXISTS idx_recommendations_batch_user_report
    ON recommendations(batch_id, user_id, recommended_report_id)
    WHERE batch_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_users_metabase_id   ON users(metabase_user_id);
CREATE INDEX IF NOT EXISTS idx_reports_metabase_id ON reports(metabase_report_id);

-- ============ VIEWS ============

-- CREATE OR REPLACE VIEW v_top_reports AS
-- SELECT
--     r.id, r.title,
--     COUNT(nl.id)               AS view_count,
--     AVG(nl.duration)           AS avg_duration_sec,
--     COUNT(DISTINCT nl.user_id) AS unique_users
-- FROM reports r
-- LEFT JOIN navigation_logs nl ON r.id = nl.report_id
-- GROUP BY r.id, r.title
-- ORDER BY view_count DESC;
-- CREATE OR REPLACE VIEW v_user_report_affinity AS
-- SELECT
--     nl.user_id,
--     nl.report_id,
--     COUNT(*)          AS interaction_count,
--     AVG(nl.duration)  AS avg_duration_sec,
--     MAX(nl.timestamp) AS last_viewed
-- FROM navigation_logs nl
-- GROUP BY nl.user_id, nl.report_id;

CREATE OR REPLACE VIEW v_pipeline_monitoring_summary AS
SELECT
    (SELECT COUNT(*) FROM users) AS users,
    (SELECT COUNT(*) FROM reports) AS reports,
    (SELECT COUNT(*) FROM navigation_logs) AS navigation_logs,
    (SELECT COUNT(*) FROM navigation_logs WHERE duration > 0) AS logs_with_duration,
    (SELECT COUNT(*) FROM recommendations) AS recommendations,
    (SELECT COUNT(DISTINCT batch_id) FROM recommendations WHERE batch_id IS NOT NULL)
        AS recommendation_batches,
    (SELECT MAX(timestamp) FROM navigation_logs) AS latest_event_at,
    (SELECT MAX(generated_at) FROM recommendations) AS latest_batch_at;

CREATE OR REPLACE VIEW v_top_viewed_reports AS
SELECT
    r.id AS report_id,
    r.title,
    COALESCE(r.business_category, 'general') AS business_category,
    COUNT(nl.id) AS events,
    COUNT(DISTINCT nl.user_id) AS unique_users,
    ROUND(AVG(nl.duration)::numeric, 2) AS avg_duration
FROM reports r
JOIN navigation_logs nl ON nl.report_id = r.id
GROUP BY r.id, r.title, r.business_category
ORDER BY events DESC;

CREATE OR REPLACE VIEW v_latest_batch_recommendations AS
SELECT
    rec.batch_id,
    rec.user_id,
    rec.rank,
    rec.recommended_report_id,
    r.title,
    COALESCE(r.business_category, 'general') AS business_category,
    rec.score,
    rec.algorithm,
    rec.generated_at
FROM recommendations rec
JOIN reports r ON r.id = rec.recommended_report_id
WHERE rec.batch_id = (
    SELECT batch_id
    FROM recommendations
    WHERE batch_id IS NOT NULL
    GROUP BY batch_id
    ORDER BY MAX(generated_at) DESC
    LIMIT 1
);
