#!/usr/bin/env python3
"""
Batch recommendation service.

WHAT: Precompute recommendations for all users and store them in PostgreSQL.
WHY: Demo/API reads become fast, reproducible, and auditable.
HOW: Train the current recommendation model, generate top-N for every user,
then insert one ranked row per user/report into the recommendations table.
"""

import json
import logging
import os
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

import psycopg2
from psycopg2.extras import Json, RealDictCursor, execute_values

try:
    from .recommendation_service import recommendation_service
except ImportError:
    from recommendation_service import recommendation_service

logger = logging.getLogger(__name__)


class BatchRecommendationService:
    """
    Store generated recommendations in PostgreSQL.
    """

    def __init__(self):
        self.db_config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", 5432)),
            "user": os.getenv("DB_USER", "admin"),
            "password": os.getenv("DB_PASSWORD", "admin123"),
            "dbname": os.getenv("DB_NAME", "bi_recommendation"),
        }
        self.last_batch = None
        self._lock = Lock()

    def generate_for_all_users(self, n_recommendations=5):
        """
        Train the current model and store top-N recommendations for every user.
        """
        n_recommendations = int(n_recommendations)
        generated_at = datetime.now(timezone.utc)
        batch_id = f"batch_{generated_at.strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}"

        with self._lock:
            model_status = recommendation_service.train()
            user_ids = self._load_user_ids()
            rows = []

            for user_id in user_ids:
                recommendations = recommendation_service.recommend(
                    user_id=user_id,
                    n_recommendations=n_recommendations,
                )
                for item in recommendations:
                    rows.append(
                        (
                            int(user_id),
                            int(item["report_id"]),
                            int(item["rank"]),
                            float(item["score"]),
                            item.get("algorithm") or "hybrid_knn_content",
                            self._model_version(model_status),
                            batch_id,
                            Json(
                                {
                                    "metabase_report_id": item.get("metabase_report_id"),
                                    "title": item.get("title"),
                                    "business_category": item.get("business_category"),
                                }
                            ),
                            generated_at,
                            False,
                        )
                    )

            inserted = self._insert_recommendations(rows)
            self.last_batch = {
                "batch_id": batch_id,
                "generated_at": generated_at.isoformat(),
                "requested_top_n": n_recommendations,
                "users": len(user_ids),
                "recommendations_inserted": inserted,
                "model": model_status,
            }
            logger.info("Batch recommendations generated: %s", self.last_batch)
            return self.last_batch

    def get_latest_for_user(self, user_id, n_recommendations=5):
        """
        Read the latest stored top-N recommendations for one user.
        """
        latest_batch_id = self._latest_batch_id()
        if latest_batch_id is None:
            return {
                "user_id": int(user_id),
                "batch_id": None,
                "count": 0,
                "recommendations": [],
            }

        query = """
            SELECT
                rec.rank,
                rec.recommended_report_id AS report_id,
                rep.metabase_report_id,
                rep.title,
                COALESCE(rep.description, '') AS description,
                COALESCE(rep.category, '') AS category,
                COALESCE(rep.business_category, 'general') AS business_category,
                rec.score,
                rec.algorithm,
                rec.model_version,
                rec.batch_id,
                rec.generated_at,
                rec.clicked
            FROM recommendations rec
            JOIN reports rep ON rep.id = rec.recommended_report_id
            WHERE rec.user_id = %s
              AND rec.batch_id = %s
            ORDER BY rec.rank ASC
            LIMIT %s
        """
        with self._connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (int(user_id), latest_batch_id, int(n_recommendations)))
                rows = cur.fetchall()

        recommendations = []
        for row in rows:
            item = dict(row)
            item["generated_at"] = item["generated_at"].isoformat()
            item["score"] = float(item["score"])
            recommendations.append(item)

        return {
            "user_id": int(user_id),
            "batch_id": latest_batch_id,
            "count": len(recommendations),
            "recommendations": recommendations,
        }

    def status(self):
        """
        Return the latest persisted batch summary.
        """
        query = """
            SELECT
                batch_id,
                MAX(generated_at) AS generated_at,
                COUNT(*) AS recommendations,
                COUNT(DISTINCT user_id) AS users,
                MAX(model_version) AS model_version
            FROM recommendations
            WHERE batch_id IS NOT NULL
            GROUP BY batch_id
            ORDER BY generated_at DESC
            LIMIT 1
        """
        with self._connect() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query)
                latest = cur.fetchone()

        if latest:
            latest = dict(latest)
            latest["generated_at"] = latest["generated_at"].isoformat()

        return {
            "last_runtime_batch": self.last_batch,
            "latest_stored_batch": latest,
        }

    def _connect(self):
        return psycopg2.connect(**self.db_config)

    def _load_user_ids(self):
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM users ORDER BY id")
                return [row[0] for row in cur.fetchall()]

    def _insert_recommendations(self, rows):
        if not rows:
            return 0

        query = """
            INSERT INTO recommendations (
                user_id,
                recommended_report_id,
                rank,
                score,
                algorithm,
                model_version,
                batch_id,
                metadata,
                generated_at,
                clicked
            )
            VALUES %s
            ON CONFLICT DO NOTHING
        """
        with self._connect() as conn:
            with conn.cursor() as cur:
                execute_values(cur, query, rows, page_size=500)
            conn.commit()
        return len(rows)

    @staticmethod
    def _model_version(model_status):
        summary = model_status.get("training_summary") or {}
        payload = {
            "algorithm": summary.get("algorithm", "hybrid_knn_content"),
            "cf_model": summary.get("cf_model", "knn"),
            "cf_weight": summary.get("cf_weight", 0.6),
            "content_weight": summary.get("content_weight", 0.4),
        }
        return json.dumps(payload, sort_keys=True)

    def _latest_batch_id(self):
        query = """
            SELECT batch_id
            FROM recommendations
            WHERE batch_id IS NOT NULL
            GROUP BY batch_id
            ORDER BY MAX(generated_at) DESC
            LIMIT 1
        """
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                row = cur.fetchone()
        return row[0] if row else None


batch_recommendation_service = BatchRecommendationService()
