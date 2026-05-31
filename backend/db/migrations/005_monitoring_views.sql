-- ============================================================
-- Migration 005: Monitoring views for local demo
-- ============================================================

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
