#!/usr/bin/env python3
"""
Recommendation Service for the FastAPI layer.

WHAT: Own the lifecycle of the trained recommendation model.
WHY: API routes should stay thin; training, caching, and formatting belong in a
service layer.
HOW: Train the tuned hybrid model on all available interactions and expose
top-N recommendations with report metadata.
"""

import logging
from datetime import datetime, timezone
from threading import Lock

try:
    from .data_preparation import DataPreparation
    from .hybrid import HybridRecommender
except ImportError:
    from data_preparation import DataPreparation
    from hybrid import HybridRecommender

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    In-memory model service.

    The model is trained lazily by /train or the first recommendation request.
    For this project stage, in-memory serving is enough and easy to explain.
    """

    def __init__(self):
        self.model = None
        self.reports = None
        self.last_trained_at = None
        self.training_summary = None
        self._lock = Lock()

    @property
    def is_ready(self):
        return self.model is not None and self.reports is not None

    def train(self):
        """
        Train the tuned hybrid recommender on all available data.
        """
        with self._lock:
            prep = DataPreparation()

            try:
                prep.connect()
                logs = prep.load_navigation_logs()
                reports = prep.load_reports()

                if logs.empty:
                    raise ValueError("No navigation logs available for training")
                if reports.empty:
                    raise ValueError("No reports available for training")

                interaction_features = prep.create_interaction_features(logs)
                if interaction_features.empty:
                    raise ValueError("No interaction features could be generated")

                model = HybridRecommender()
                model.fit(interaction_features, reports)

                self.model = model
                self.reports = reports.copy()
                self.last_trained_at = datetime.now(timezone.utc)
                self.training_summary = {
                    "algorithm": "hybrid_knn_content",
                    "cf_model": "knn",
                    "cf_weight": 0.6,
                    "content_weight": 0.4,
                    "events": int(len(logs)),
                    "users": int(logs["user_id"].nunique()),
                    "reports": int(reports["id"].nunique()),
                    "interaction_pairs": int(len(interaction_features)),
                    "trained_at": self.last_trained_at.isoformat(),
                }

                logger.info("Recommendation model trained: %s", self.training_summary)
                return self.status()

            finally:
                prep.close()

    def recommend(self, user_id, n_recommendations=5):
        """
        Return top-N recommendations for an internal PostgreSQL user id.
        """
        if not self.is_ready:
            self.train()

        user_id = int(user_id)
        n_recommendations = int(n_recommendations)

        recommendations = self.model.recommend(
            user_id,
            n_recommendations=n_recommendations,
            exclude_seen=True,
        )

        if recommendations.empty:
            return []

        report_metadata = self.reports[
            [
                "id",
                "metabase_report_id",
                "title",
                "description",
                "category",
                "business_category",
            ]
        ]
        recommendations = recommendations.merge(
            report_metadata,
            left_on="report_id",
            right_on="id",
            how="left",
        )

        return [
            {
                "rank": int(row["rank"]),
                "report_id": int(row["report_id"]),
                "metabase_report_id": self._optional_int(row.get("metabase_report_id")),
                "title": row.get("title") or "",
                "description": row.get("description") or "",
                "category": row.get("category") or "",
                "business_category": row.get("business_category") or "general",
                "score": float(row["score"]),
                "algorithm": row.get("algorithm") or "hybrid_knn_content",
            }
            for _, row in recommendations.iterrows()
        ]

    def status(self):
        """
        Return model readiness and training metadata.
        """
        return {
            "ready": self.is_ready,
            "last_trained_at": self.last_trained_at.isoformat()
            if self.last_trained_at
            else None,
            "training_summary": self.training_summary,
        }

    @staticmethod
    def _optional_int(value):
        if value is None:
            return None
        try:
            if value != value:
                return None
            return int(value)
        except (TypeError, ValueError):
            return None


recommendation_service = RecommendationService()
