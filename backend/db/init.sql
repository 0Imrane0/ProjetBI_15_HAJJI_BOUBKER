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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS navigation_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    report_id INTEGER NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL DEFAULT 'view',
    duration INTEGER DEFAULT 0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recommended_report_id INTEGER NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    score FLOAT DEFAULT 0.0,
    algorithm VARCHAR(50),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    clicked BOOLEAN DEFAULT FALSE
);

-- Multi-cursor state: one row per stream, survives container restarts
CREATE TABLE IF NOT EXISTS publisher_state (stream VARCHAR(50) PRIMARY KEY, last_id INTEGER DEFAULT 0, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

INSERT INTO publisher_state VALUES ('recent_views',0,NOW()),('core_user',0,NOW()),('report_card',0,NOW());


-- ============ INDEXES ============

CREATE INDEX IF NOT EXISTS idx_nav_logs_user_ts    ON navigation_logs(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_nav_logs_report     ON navigation_logs(report_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_user ON recommendations(user_id, generated_at DESC);
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