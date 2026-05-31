-- Backfill existing demo data after Metabase sample tables are populated.
-- Safe to run multiple times.

UPDATE reports r
SET
    title = rc.name,
    description = rc.description,
    category = rc.display,
    business_category = CASE
        WHEN LOWER(COALESCE(rc.name, '') || ' ' || COALESCE(rc.description, '')) LIKE ANY
            (ARRAY['%sales%', '%order%', '%pipeline%', '%revenue%', '%deal%'])
            THEN 'sales'
        WHEN LOWER(COALESCE(rc.name, '') || ' ' || COALESCE(rc.description, '')) LIKE ANY
            (ARRAY['%profit%', '%cash%', '%margin%', '%cost%', '%discount%'])
            THEN 'finance'
        WHEN LOWER(COALESCE(rc.name, '') || ' ' || COALESCE(rc.description, '')) LIKE ANY
            (ARRAY['%marketing%', '%campaign%', '%email%', '%social%', '%funnel%'])
            THEN 'marketing'
        WHEN LOWER(COALESCE(rc.name, '') || ' ' || COALESCE(rc.description, '')) LIKE ANY
            (ARRAY['%customer%', '%churn%', '%satisfaction%', '%nps%', '%support%'])
            THEN 'customer'
        WHEN LOWER(COALESCE(rc.name, '') || ' ' || COALESCE(rc.description, '')) LIKE ANY
            (ARRAY['%product%', '%adoption%', '%category%', '%feature%'])
            THEN 'product'
        WHEN LOWER(COALESCE(rc.name, '') || ' ' || COALESCE(rc.description, '')) LIKE ANY
            (ARRAY['%inventory%', '%operational%', '%system%', '%performance%', '%quality%'])
            THEN 'operations'
        ELSE 'general'
    END,
    updated_at = NOW()
FROM report_card rc
WHERE r.metabase_report_id = rc.id;

WITH matched_events AS (
    SELECT
        nl.id AS navigation_log_id,
        rv.id AS source_event_id,
        rv.model,
        rv.model_id,
        CASE
            WHEN COALESCE(rv.context, 'view') = 'selection'
                THEN 90 + (rv.id % 511)
            ELSE 15 + (rv.id % 226)
        END AS base_duration
    FROM navigation_logs nl
    JOIN users u ON u.id = nl.user_id
    JOIN reports r ON r.id = nl.report_id
    JOIN recent_views rv
        ON rv.user_id = u.metabase_user_id
        AND rv.model_id = r.metabase_report_id
        AND rv.context = nl.action
        AND rv.timestamp = nl.timestamp
)
UPDATE navigation_logs nl
SET
    source_event_id = matched_events.source_event_id,
    event_type = COALESCE(nl.event_type, nl.action, 'view'),
    duration = CASE
        WHEN matched_events.model = 'dashboard'
            THEN LEAST((matched_events.base_duration * 14 / 10), 900)
        ELSE matched_events.base_duration
    END,
    duration_source = 'simulated',
    metabase_model = matched_events.model,
    metabase_model_id = matched_events.model_id,
    raw_payload = jsonb_build_object(
        'stream', 'recent_views',
        'source_event_id', matched_events.source_event_id,
        'duration_source', 'simulated',
        'metabase_model', matched_events.model,
        'metabase_model_id', matched_events.model_id
    )
FROM matched_events
WHERE nl.id = matched_events.navigation_log_id;
