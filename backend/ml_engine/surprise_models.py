#!/usr/bin/env python3
"""
Surprise-based Collaborative Filtering Models.

WHAT: Train SVD and KNN recommenders with the Surprise library.
WHY: Compare our hand-made baseline with standard recommender algorithms.
HOW: Use implicit_rating as a 1-5 rating, then evaluate top-k recommendations.
"""

import logging

import numpy as np
import pandas as pd

try:
    from surprise import Dataset, KNNBasic, Reader, SVD
except ImportError as exc:
    raise ImportError(
        "scikit-surprise is required for this module. "
        "Install backend/requirements.txt or rebuild the backend image."
    ) from exc

try:
    from .data_preparation import DataPreparation
except ImportError:
    from data_preparation import DataPreparation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SurpriseRecommender:
    """
    Wrapper around Surprise SVD or KNNBasic for top-k recommendations.
    """

    def __init__(self, algorithm="svd", **algorithm_params):
        self.algorithm_name = algorithm
        self.algorithm_params = algorithm_params
        self.model = self._build_model(algorithm, algorithm_params)
        self.trainset = None
        self.train_interactions = None
        self.report_ids = []
        self.global_popularity = None

    def fit(self, interaction_features):
        required_columns = {"user_id", "report_id", "implicit_rating"}
        missing_columns = required_columns - set(interaction_features.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

        training_df = interaction_features[
            ["user_id", "report_id", "implicit_rating"]
        ].copy()
        training_df["implicit_rating"] = training_df["implicit_rating"].clip(1, 5)

        reader = Reader(rating_scale=(1, 5))
        dataset = Dataset.load_from_df(
            training_df[["user_id", "report_id", "implicit_rating"]],
            reader,
        )

        self.trainset = dataset.build_full_trainset()
        self.model.fit(self.trainset)
        self.train_interactions = training_df
        self.report_ids = sorted(training_df["report_id"].unique().tolist())
        self.global_popularity = (
            training_df.groupby("report_id")["implicit_rating"]
            .mean()
            .sort_values(ascending=False)
        )

        logger.info("\n✅ Surprise %s fitted", self.algorithm_name.upper())
        logger.info("   Train rows: %s", len(training_df))
        logger.info("   Users: %s", training_df["user_id"].nunique())
        logger.info("   Reports: %s", training_df["report_id"].nunique())
        return self

    def recommend(self, user_id, n_recommendations=5, exclude_seen=True):
        self._ensure_fitted()

        if not self._knows_user(user_id):
            scores = self.global_popularity.head(n_recommendations)
            return self._format_recommendations(user_id, scores)

        seen_reports = set()
        if exclude_seen:
            seen_reports = set(
                self.train_interactions.loc[
                    self.train_interactions["user_id"] == user_id,
                    "report_id",
                ]
            )

        candidate_reports = [
            report_id for report_id in self.report_ids if report_id not in seen_reports
        ]
        predictions = [
            (report_id, self.model.predict(user_id, report_id).est)
            for report_id in candidate_reports
        ]
        scores = pd.Series(
            {report_id: score for report_id, score in predictions}
        ).sort_values(ascending=False)

        return self._format_recommendations(user_id, scores.head(n_recommendations))

    def evaluate(self, test_interactions, k=5):
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
            if not self._knows_user(user_id):
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

        logger.info("\n✅ Surprise %s evaluation", self.algorithm_name.upper())
        logger.info("   Precision@%s: %.4f", k, metrics["precision_at_k"])
        logger.info("   NDCG@%s: %.4f", k, metrics["ndcg_at_k"])
        logger.info("   Evaluated users: %s", metrics["evaluated_users"])
        return metrics

    def _build_model(self, algorithm, params):
        if algorithm == "svd":
            return SVD(
                n_factors=params.get("n_factors", 10),
                n_epochs=params.get("n_epochs", 20),
                lr_all=params.get("lr_all", 0.003),
                reg_all=params.get("reg_all", 0.08),
                random_state=params.get("random_state", 42),
            )

        if algorithm == "knn":
            sim_options = {
                "name": params.get("similarity", "cosine"),
                "user_based": params.get("user_based", True),
            }
            return KNNBasic(
                k=params.get("k", 20),
                min_k=params.get("min_k", 1),
                sim_options=sim_options,
                verbose=False,
            )

        raise ValueError("algorithm must be 'svd' or 'knn'")

    def _knows_user(self, user_id):
        try:
            self.trainset.to_inner_uid(user_id)
            return True
        except ValueError:
            return False

    def _ensure_fitted(self):
        if self.trainset is None or self.train_interactions is None:
            raise RuntimeError("Model must be fitted before use")

    def _format_recommendations(self, user_id, scores):
        recommendations = pd.DataFrame(
            {
                "user_id": user_id,
                "report_id": scores.index.astype(int),
                "score": scores.values.astype(float),
            }
        )
        recommendations["rank"] = np.arange(1, len(recommendations) + 1)
        recommendations["algorithm"] = f"surprise_{self.algorithm_name}"
        return recommendations

    @staticmethod
    def _ndcg_at_k(hits, ideal_hit_count):
        if not hits or ideal_hit_count == 0:
            return 0.0

        dcg = sum(hit / np.log2(rank + 2) for rank, hit in enumerate(hits))
        ideal_dcg = sum(1 / np.log2(rank + 2) for rank in range(ideal_hit_count))
        return float(dcg / ideal_dcg) if ideal_dcg else 0.0


def run_surprise_models():
    prep = DataPreparation()

    try:
        prep.connect()
        logs = prep.load_navigation_logs()
        reports = prep.load_reports()

        train_logs, test_logs = prep.create_temporal_train_test_split(logs)
        train_features = prep.create_interaction_features(train_logs)
        test_features = prep.create_interaction_features(test_logs)

        results = {}
        for algorithm in ["svd", "knn"]:
            model = SurpriseRecommender(algorithm=algorithm)
            model.fit(train_features)
            metrics = model.evaluate(test_features, k=5)
            results[algorithm] = metrics

            sample_user_id = int(train_features["user_id"].iloc[0])
            recommendations = model.recommend(sample_user_id, n_recommendations=5)
            recommendations = recommendations.merge(
                reports[["id", "title", "business_category"]],
                left_on="report_id",
                right_on="id",
                how="left",
            )
            logger.info("\n📌 %s sample recommendations for user %s", algorithm.upper(), sample_user_id)
            logger.info(
                recommendations[
                    ["rank", "report_id", "title", "business_category", "score"]
                ].to_string(index=False)
            )

        return results
    finally:
        prep.close()


if __name__ == "__main__":
    run_surprise_models()
