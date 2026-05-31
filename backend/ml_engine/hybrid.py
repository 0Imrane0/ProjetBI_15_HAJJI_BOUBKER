#!/usr/bin/env python3
"""
Hybrid Recommendation Model.

WHAT: Combine collaborative filtering and content-based recommendations.
WHY: CF captures collective behavior, while content-based uses report metadata.
Together they can balance precision, ranking quality, coverage, and cold-start
robustness.
HOW: Generate candidate scores from both models, normalize them per user, then
compute a weighted average.
"""

import logging

import numpy as np
import pandas as pd

try:
    from .collaborative import UserBasedCollaborativeFiltering
    from .content_based import ContentBasedRecommender
    from .data_preparation import DataPreparation
    from .surprise_models import SurpriseRecommender
except ImportError:
    from collaborative import UserBasedCollaborativeFiltering
    from content_based import ContentBasedRecommender
    from data_preparation import DataPreparation
    from surprise_models import SurpriseRecommender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HybridRecommender:
    """
    Weighted hybrid recommender.

    cf_weight=1.0 means pure collaborative filtering.
    cf_weight=0.0 means pure content-based filtering.
    """

    def __init__(self, cf_model="knn", cf_weight=0.6):
        self.cf_model_name = cf_model
        self.cf_weight = cf_weight
        self.cf_model = self._build_cf_model(cf_model)
        self.content_model = ContentBasedRecommender()
        self.report_ids = []

    def fit(self, interaction_features, reports_df):
        self.cf_model.fit(interaction_features)
        self.content_model.fit(interaction_features, reports_df)
        self.report_ids = sorted(reports_df["id"].astype(int).tolist())

        logger.info("\n✅ Hybrid model fitted")
        logger.info(f"   CF model: {self.cf_model_name}")
        logger.info(f"   CF weight: {self.cf_weight:.2f}")
        logger.info(f"   Reports: {len(self.report_ids)}")
        return self

    def recommend(self, user_id, n_recommendations=5, exclude_seen=True):
        candidate_count = max(len(self.report_ids), n_recommendations)

        cf_recs = self.cf_model.recommend(
            user_id,
            n_recommendations=candidate_count,
            exclude_seen=exclude_seen,
        )
        content_recs = self.content_model.recommend(
            user_id,
            n_recommendations=candidate_count,
            exclude_seen=exclude_seen,
        )

        combined = pd.merge(
            cf_recs[["report_id", "score"]].rename(columns={"score": "cf_score"}),
            content_recs[["report_id", "score"]].rename(columns={"score": "content_score"}),
            on="report_id",
            how="outer",
        ).fillna(0)

        combined["cf_score_norm"] = self._normalize_scores(combined["cf_score"])
        combined["content_score_norm"] = self._normalize_scores(combined["content_score"])
        combined["score"] = (
            self.cf_weight * combined["cf_score_norm"]
            + (1 - self.cf_weight) * combined["content_score_norm"]
        )

        combined = combined.sort_values("score", ascending=False).head(n_recommendations)
        recommendations = combined[["report_id", "score"]].copy()
        recommendations.insert(0, "user_id", user_id)
        recommendations["rank"] = np.arange(1, len(recommendations) + 1)
        recommendations["algorithm"] = f"hybrid_{self.cf_model_name}_content"
        return recommendations

    @staticmethod
    def _normalize_scores(scores):
        min_score = scores.min()
        max_score = scores.max()
        if max_score == min_score:
            return pd.Series(np.ones(len(scores)), index=scores.index)
        return (scores - min_score) / (max_score - min_score)

    @staticmethod
    def _build_cf_model(cf_model):
        if cf_model == "svd":
            return SurpriseRecommender(algorithm="svd")
        if cf_model == "knn":
            return SurpriseRecommender(algorithm="knn")
        if cf_model == "baseline":
            return UserBasedCollaborativeFiltering()
        raise ValueError("cf_model must be one of: svd, knn, baseline")


def run_hybrid_demo():
    prep = DataPreparation()

    try:
        prep.connect()
        logs = prep.load_navigation_logs()
        reports = prep.load_reports()

        train_logs, test_logs = prep.create_temporal_train_test_split(logs)
        train_features = prep.create_interaction_features(train_logs)
        test_features = prep.create_interaction_features(test_logs)

        model = HybridRecommender()
        model.fit(train_features, reports)

        try:
            from .offline_evaluation import evaluate_recommender
        except ImportError:
            from offline_evaluation import evaluate_recommender

        metrics_5 = evaluate_recommender(
            "hybrid_svd_content",
            model,
            test_features,
            reports["id"].tolist(),
            k=5,
        )
        metrics_10 = evaluate_recommender(
            "hybrid_svd_content",
            model,
            test_features,
            reports["id"].tolist(),
            k=10,
        )

        sample_user_id = int(train_features["user_id"].iloc[0])
        recommendations = model.recommend(sample_user_id, n_recommendations=5)
        recommendations = recommendations.merge(
            reports[["id", "title", "business_category"]],
            left_on="report_id",
            right_on="id",
            how="left",
        )
        logger.info(f"\n📌 Hybrid sample recommendations for user {sample_user_id}")
        logger.info(
            recommendations[
                ["rank", "report_id", "title", "business_category", "score"]
            ].to_string(index=False)
        )
        return {"k5": metrics_5, "k10": metrics_10}
    finally:
        prep.close()


if __name__ == "__main__":
    run_hybrid_demo()
