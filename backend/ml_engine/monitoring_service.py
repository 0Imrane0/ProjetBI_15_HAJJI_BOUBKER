#!/usr/bin/env python3
"""
Monitoring service for local demo visibility.

WHAT: Return compact health and activity metrics from PostgreSQL.
WHY: The demo needs a quick way to prove that data flows, batches are generated,
and recommendations exist.
HOW: Read aggregate metrics and top reports directly from the project tables.
"""

import os

import psycopg2
from psycopg2.extras import RealDictCursor


class MonitoringService:
    def __init__(self):
        self.db_config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", 5432)),
            "user": os.getenv("DB_USER", "admin"),
            "password": os.getenv("DB_PASSWORD", "admin123"),
            "dbname": os.getenv("DB_NAME", "bi_recommendation"),
        }

    def summary(self):
        with psycopg2.connect(**self.db_config) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT
                        (SELECT COUNT(*) FROM users) AS users,
                        (SELECT COUNT(*) FROM reports) AS reports,
                        (SELECT COUNT(*) FROM navigation_logs) AS navigation_logs,
                        (SELECT COUNT(*) FROM navigation_logs WHERE duration > 0)
                            AS logs_with_duration,
                        (SELECT COUNT(*) FROM recommendations) AS recommendations,
                        (SELECT COUNT(DISTINCT batch_id)
                            FROM recommendations
                            WHERE batch_id IS NOT NULL) AS recommendation_batches,
                        (SELECT MAX(timestamp) FROM navigation_logs) AS latest_event_at,
                        (SELECT MAX(generated_at) FROM recommendations) AS latest_batch_at
                    """
                )
                totals = dict(cur.fetchone())

                cur.execute(
                    """
                    SELECT
                        r.id AS report_id,
                        r.title,
                        COALESCE(r.business_category, 'general') AS business_category,
                        COUNT(nl.id) AS events
                    FROM reports r
                    JOIN navigation_logs nl ON nl.report_id = r.id
                    GROUP BY r.id, r.title, r.business_category
                    ORDER BY events DESC
                    LIMIT 5
                    """
                )
                top_viewed_reports = [dict(row) for row in cur.fetchall()]

                cur.execute(
                    """
                    SELECT
                        r.id AS report_id,
                        r.title,
                        COALESCE(r.business_category, 'general') AS business_category,
                        COUNT(rec.id) AS recommendations
                    FROM reports r
                    JOIN recommendations rec ON rec.recommended_report_id = r.id
                    WHERE rec.batch_id = (
                        SELECT batch_id
                        FROM recommendations
                        WHERE batch_id IS NOT NULL
                        GROUP BY batch_id
                        ORDER BY MAX(generated_at) DESC
                        LIMIT 1
                    )
                    GROUP BY r.id, r.title, r.business_category
                    ORDER BY recommendations DESC
                    LIMIT 5
                    """
                )
                top_recommended_reports = [dict(row) for row in cur.fetchall()]

        for key in ["latest_event_at", "latest_batch_at"]:
            if totals.get(key):
                totals[key] = totals[key].isoformat()

        return {
            "totals": totals,
            "top_viewed_reports": top_viewed_reports,
            "top_recommended_reports": top_recommended_reports,
        }


monitoring_service = MonitoringService()
