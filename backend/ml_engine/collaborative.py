#!/usr/bin/env python3
"""
Collaborative Filtering Baseline

WHAT: User-based collaborative filtering using cosine similarity.
WHY: Establish a simple, explainable recommendation baseline before trying
more advanced models such as Surprise SVD/KNN.
HOW: Build a user-report rating matrix from implicit ratings, compare users by
cosine similarity, and recommend reports liked by similar users.
"""

import logging

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

try:
    from .data_preparation import DataPreparation
except ImportError:
    from data_preparation import DataPreparation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserBasedCollaborativeFiltering:
    """
    Simple user-based collaborative filtering recommender.
    """

    def __init__(self):
        self.user_report_matrix = None
        self.user_similarity = None
        self.user_ids = []
        self.report_ids = []
        self.global_popularity = None

    def fit(self, interaction_features):
        """
        Train the baseline model from user-report interaction features.

        Args:
            interaction_features: DataFrame with user_id, report_id,
                implicit_rating.
        """
        required_columns = {"user_id", "report_id", "implicit_rating"}
        missing_columns = required_columns - set(interaction_features.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

        self.user_report_matrix = interaction_features.pivot_table(
            index="user_id",
            columns="report_id",
            values="implicit_rating",
            aggfunc="max",
            fill_value=0,
        )

        self.user_ids = list(self.user_report_matrix.index)
        self.report_ids = list(self.user_report_matrix.columns)

        self.user_similarity = pd.DataFrame(
            cosine_similarity(self.user_report_matrix),
            index=self.user_ids,
            columns=self.user_ids,
        )

        self.global_popularity = (
            interaction_features.groupby("report_id")["implicit_rating"]
            .mean()
            .sort_values(ascending=False)
        )

        logger.info("\n✅ User-Based CF fitted")
        logger.info(f"   Users: {len(self.user_ids)}")
        logger.info(f"   Reports: {len(self.report_ids)}")
        logger.info(f"   Matrix shape: {self.user_report_matrix.shape}")
        return self

    def recommend(self, user_id, n_recommendations=5, exclude_seen=True):
        """
        Recommend reports for one user.

        Args:
            user_id: Internal PostgreSQL user id.
            n_recommendations: Number of reports to return.
            exclude_seen: Do not recommend reports already seen in train data.

        Returns:
            DataFrame with user_id, report_id, score, rank, algorithm.
        """
        self._ensure_fitted()

        if user_id not in self.user_ids:
            return self._popular_recommendations(user_id, n_recommendations)

        similarities = self.user_similarity.loc[user_id].copy()
        similarities.loc[user_id] = 0

        ratings = self.user_report_matrix.copy()
        weighted_scores = similarities.values @ ratings.values
        similarity_sums = np.abs(similarities.values) @ (ratings.values > 0)
        predicted_scores = np.divide(
            weighted_scores,
            similarity_sums,
            out=np.zeros_like(weighted_scores, dtype=float),
            where=similarity_sums != 0,
        )

        scores = pd.Series(predicted_scores, index=self.report_ids)

        if exclude_seen:
            seen_reports = self.user_report_matrix.loc[user_id]
            scores = scores[seen_reports == 0]

        scores = scores.sort_values(ascending=False).head(n_recommendations)
        return self._format_recommendations(user_id, scores)

    def evaluate(self, test_interactions, k=5):
        """
        Evaluate recommendations with binary Precision@k and NDCG@k.

        A report is relevant if it appears in the user's test interactions.
        This is enough for our first offline baseline.
        """
        self._ensure_fitted()

        if test_interactions.empty:
            return {"precision_at_k": 0.0, "ndcg_at_k": 0.0, "evaluated_users": 0}

        test_by_user = (
            test_interactions.groupby("user_id")["report_id"]
            .apply(lambda values: set(values))
            .to_dict()
        )

        precisions = []
        ndcgs = []

        for user_id, relevant_reports in test_by_user.items():
            if user_id not in self.user_ids:
                continue

            recommendations = self.recommend(user_id, n_recommendations=k)
            recommended_reports = recommendations["report_id"].tolist()

            hits = [1 if report_id in relevant_reports else 0 for report_id in recommended_reports]
            precisions.append(sum(hits) / k)
            ndcgs.append(self._ndcg_at_k(hits, min(len(relevant_reports), k)))

        metrics = {
            "precision_at_k": float(np.mean(precisions)) if precisions else 0.0,
            "ndcg_at_k": float(np.mean(ndcgs)) if ndcgs else 0.0,
            "evaluated_users": len(precisions),
        }

        logger.info("\n✅ User-Based CF evaluation")
        logger.info(f"   Precision@{k}: {metrics['precision_at_k']:.4f}")
        logger.info(f"   NDCG@{k}: {metrics['ndcg_at_k']:.4f}")
        logger.info(f"   Evaluated users: {metrics['evaluated_users']}")
        return metrics

    def _popular_recommendations(self, user_id, n_recommendations):
        scores = self.global_popularity.head(n_recommendations)
        return self._format_recommendations(user_id, scores)

    def _format_recommendations(self, user_id, scores):
        recommendations = pd.DataFrame(
            {
                "user_id": user_id,
                "report_id": scores.index.astype(int),
                "score": scores.values.astype(float),
            }
        )
        recommendations["rank"] = np.arange(1, len(recommendations) + 1)
        recommendations["algorithm"] = "user_based_cf"
        return recommendations

    def _ensure_fitted(self):
        if self.user_report_matrix is None or self.user_similarity is None:
            raise RuntimeError("Model must be fitted before use")

    @staticmethod
    def _ndcg_at_k(hits, ideal_hit_count):
        if not hits or ideal_hit_count == 0:
            return 0.0

        dcg = sum(hit / np.log2(rank + 2) for rank, hit in enumerate(hits))
        ideal_dcg = sum(1 / np.log2(rank + 2) for rank in range(ideal_hit_count))
        return float(dcg / ideal_dcg) if ideal_dcg else 0.0


def run_baseline():
    """
    Train and evaluate the baseline from PostgreSQL data.
    """
    prep = DataPreparation()

    try:
        prep.connect()
        logs = prep.load_navigation_logs()
        reports = prep.load_reports()

        train_logs, test_logs = prep.create_temporal_train_test_split(logs)
        train_features = prep.create_interaction_features(train_logs)
        test_features = prep.create_interaction_features(test_logs)

        model = UserBasedCollaborativeFiltering()
        model.fit(train_features)
        metrics = model.evaluate(test_features, k=5)

        sample_user_id = int(train_features["user_id"].iloc[0])
        recommendations = model.recommend(sample_user_id, n_recommendations=5)
        recommendations = recommendations.merge(
            reports[["id", "title", "business_category"]],
            left_on="report_id",
            right_on="id",
            how="left",
        )

        logger.info(f"\n📌 Sample recommendations for user {sample_user_id}")
        logger.info(
            recommendations[
                ["rank", "report_id", "title", "business_category", "score"]
            ].to_string(index=False)
        )

        return metrics
    finally:
        prep.close()


if __name__ == "__main__":
    run_baseline()
