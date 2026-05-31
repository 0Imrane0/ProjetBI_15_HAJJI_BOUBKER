#!/usr/bin/env python3
"""
Content-Based Filtering Model.

WHAT: Recommend reports similar to the reports a user already engaged with.
WHY: Collaborative filtering needs behavior from many users; content-based
filtering can use report metadata and is useful for cold-start reports.
HOW: Convert report title/description/category into TF-IDF vectors, build a
weighted user profile from seen reports, then rank unseen reports by cosine
similarity to that profile.
"""

import logging

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from .data_preparation import DataPreparation
except ImportError:
    from data_preparation import DataPreparation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentBasedRecommender:
    """
    TF-IDF content-based recommender for Metabase reports.
    """

    def __init__(
        self,
        ngram_range=(1, 3),
        max_features=100,
        min_df=1,
        sublinear_tf=False,
    ):
        self.ngram_range = ngram_range
        self.max_features = max_features
        self.min_df = min_df
        self.sublinear_tf = sublinear_tf
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=ngram_range,
            max_features=max_features,
            min_df=min_df,
            sublinear_tf=sublinear_tf,
        )
        self.reports = None
        self.report_ids = []
        self.report_matrix = None
        self.report_index = {}
        self.user_profiles = {}
        self.train_interactions = None
        self.global_popularity = None

    def fit(self, interaction_features, reports_df):
        """
        Train the content-based model.

        Args:
            interaction_features: user-report features with implicit_rating.
            reports_df: report metadata from PostgreSQL.
        """
        required_interaction_columns = {"user_id", "report_id", "implicit_rating"}
        missing_interaction_columns = required_interaction_columns - set(
            interaction_features.columns
        )
        if missing_interaction_columns:
            raise ValueError(
                f"Missing interaction columns: {sorted(missing_interaction_columns)}"
            )

        required_report_columns = {"id", "title", "description", "category"}
        missing_report_columns = required_report_columns - set(reports_df.columns)
        if missing_report_columns:
            raise ValueError(f"Missing report columns: {sorted(missing_report_columns)}")

        self.reports = reports_df.copy()
        self.reports["content_text"] = self.reports.apply(self._build_content_text, axis=1)
        self.report_ids = self.reports["id"].astype(int).tolist()
        self.report_index = {
            report_id: idx for idx, report_id in enumerate(self.report_ids)
        }
        self.report_matrix = self.vectorizer.fit_transform(self.reports["content_text"])
        self.train_interactions = interaction_features.copy()
        self.global_popularity = (
            interaction_features.groupby("report_id")["implicit_rating"]
            .mean()
            .sort_values(ascending=False)
        )

        self._build_user_profiles(interaction_features)

        logger.info("\n✅ Content-Based model fitted")
        logger.info(f"   Reports: {len(self.report_ids)}")
        logger.info(f"   TF-IDF features: {len(self.vectorizer.get_feature_names_out())}")
        logger.info(f"   User profiles: {len(self.user_profiles)}")
        return self

    def recommend(self, user_id, n_recommendations=5, exclude_seen=True):
        """
        Recommend reports for a user based on content similarity.
        """
        self._ensure_fitted()

        if user_id not in self.user_profiles:
            return self._popular_recommendations(user_id, n_recommendations)

        profile = self.user_profiles[user_id]
        scores = cosine_similarity(profile, self.report_matrix).ravel()
        scores = pd.Series(scores, index=self.report_ids)

        if exclude_seen:
            seen_reports = set(
                self.train_interactions.loc[
                    self.train_interactions["user_id"] == user_id,
                    "report_id",
                ]
            )
            scores = scores.drop(labels=list(seen_reports), errors="ignore")

        scores = scores.sort_values(ascending=False).head(n_recommendations)
        return self._format_recommendations(user_id, scores)

    def evaluate(self, test_interactions, all_report_ids=None, k=5):
        """
        Evaluate recommendations with Precision@k and NDCG@k.
        """
        self._ensure_fitted()
        if all_report_ids is None:
            all_report_ids = self.report_ids

        test_by_user = (
            test_interactions.groupby("user_id")["report_id"]
            .apply(lambda values: set(values))
            .to_dict()
        )

        precisions = []
        ndcgs = []
        recommended_catalog = set()

        for user_id, relevant_reports in test_by_user.items():
            recommendations = self.recommend(user_id, n_recommendations=k)
            recommended_reports = recommendations["report_id"].tolist()
            recommended_catalog.update(recommended_reports)
            hits = [1 if report_id in relevant_reports else 0 for report_id in recommended_reports]
            precisions.append(sum(hits) / k)
            ndcgs.append(self._ndcg_at_k(hits, min(len(relevant_reports), k)))

        metrics = {
            "precision_at_k": float(np.mean(precisions)) if precisions else 0.0,
            "ndcg_at_k": float(np.mean(ndcgs)) if ndcgs else 0.0,
            "catalog_coverage_at_k": len(recommended_catalog) / len(all_report_ids),
            "evaluated_users": len(precisions),
        }
        logger.info("\n✅ Content-Based evaluation")
        logger.info(f"   Precision@{k}: {metrics['precision_at_k']:.4f}")
        logger.info(f"   NDCG@{k}: {metrics['ndcg_at_k']:.4f}")
        logger.info(f"   Coverage@{k}: {metrics['catalog_coverage_at_k']:.4f}")
        return metrics

    def _build_user_profiles(self, interaction_features):
        for user_id, user_interactions in interaction_features.groupby("user_id"):
            vectors = []
            weights = []

            for _, row in user_interactions.iterrows():
                report_id = int(row["report_id"])
                if report_id not in self.report_index:
                    continue
                vectors.append(self.report_matrix[self.report_index[report_id]])
                weights.append(float(row["implicit_rating"]))

            if not vectors:
                continue

            stacked_vectors = np.vstack([vector.toarray() for vector in vectors])
            weights_array = np.array(weights)
            weighted_profile = np.average(
                stacked_vectors,
                axis=0,
                weights=weights_array,
            ).reshape(1, -1)
            norm = np.linalg.norm(weighted_profile)
            if norm > 0:
                weighted_profile = weighted_profile / norm

            self.user_profiles[int(user_id)] = weighted_profile

    @staticmethod
    def _build_content_text(row):
        fields = [
            row.get("title", ""),
            row.get("description", ""),
            row.get("tags", ""),
            row.get("category", ""),
            row.get("business_category", ""),
        ]
        return " ".join(str(field) for field in fields if pd.notna(field)).lower()

    def _popular_recommendations(self, user_id, n_recommendations):
        scores = self.global_popularity.head(n_recommendations)
        return self._format_recommendations(user_id, scores)

    @staticmethod
    def _format_recommendations(user_id, scores):
        recommendations = pd.DataFrame(
            {
                "user_id": user_id,
                "report_id": scores.index.astype(int),
                "score": scores.values.astype(float),
            }
        )
        recommendations["rank"] = np.arange(1, len(recommendations) + 1)
        recommendations["algorithm"] = "content_based_tfidf"
        return recommendations

    def _ensure_fitted(self):
        if self.report_matrix is None or self.reports is None:
            raise RuntimeError("Model must be fitted before use")

    @staticmethod
    def _ndcg_at_k(hits, ideal_hit_count):
        if not hits or ideal_hit_count == 0:
            return 0.0

        dcg = sum(hit / np.log2(rank + 2) for rank, hit in enumerate(hits))
        ideal_dcg = sum(1 / np.log2(rank + 2) for rank in range(ideal_hit_count))
        return float(dcg / ideal_dcg) if ideal_dcg else 0.0


def run_content_based():
    prep = DataPreparation()

    try:
        prep.connect()
        logs = prep.load_navigation_logs()
        reports = prep.load_reports()

        train_logs, test_logs = prep.create_temporal_train_test_split(logs)
        train_features = prep.create_interaction_features(train_logs)
        test_features = prep.create_interaction_features(test_logs)

        model = ContentBasedRecommender()
        model.fit(train_features, reports)
        metrics_5 = model.evaluate(test_features, reports["id"].tolist(), k=5)
        metrics_10 = model.evaluate(test_features, reports["id"].tolist(), k=10)

        sample_user_id = int(train_features["user_id"].iloc[0])
        recommendations = model.recommend(sample_user_id, n_recommendations=5)
        recommendations = recommendations.merge(
            reports[["id", "title", "business_category"]],
            left_on="report_id",
            right_on="id",
            how="left",
        )

        logger.info(f"\n📌 Content-Based sample recommendations for user {sample_user_id}")
        logger.info(
            recommendations[
                ["rank", "report_id", "title", "business_category", "score"]
            ].to_string(index=False)
        )
        return {"k5": metrics_5, "k10": metrics_10}
    finally:
        prep.close()


if __name__ == "__main__":
    run_content_based()
