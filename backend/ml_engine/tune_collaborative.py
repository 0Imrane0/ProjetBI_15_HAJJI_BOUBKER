#!/usr/bin/env python3
"""
Collaborative Filtering Hyperparameter Tuning.

WHAT: Compare the handmade user-based CF baseline with tuned Surprise SVD/KNN.
WHY: Default parameters are rarely optimal; tuning tells us whether advanced
models can beat the simple baseline.
HOW: Run a small deterministic grid search and rank models by Precision@5, then
NDCG@5.
"""

import itertools
import logging
from pathlib import Path

import pandas as pd

try:
    from .collaborative import UserBasedCollaborativeFiltering
    from .data_preparation import DataPreparation
    from .surprise_models import SurpriseRecommender
except ImportError:
    from collaborative import UserBasedCollaborativeFiltering
    from data_preparation import DataPreparation
    from surprise_models import SurpriseRecommender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _parameter_grid(grid):
    keys = list(grid.keys())
    for values in itertools.product(*(grid[key] for key in keys)):
        yield dict(zip(keys, values))


def tune_svd(train_features, test_features):
    grid = {
        "n_factors": [10, 20, 40],
        "n_epochs": [20, 35],
        "lr_all": [0.003, 0.007],
        "reg_all": [0.02, 0.08],
    }
    results = []

    for params in _parameter_grid(grid):
        model = SurpriseRecommender(algorithm="svd", **params)
        model.fit(train_features)
        metrics = model.evaluate(test_features, k=5)
        results.append(
            {
                "model": "surprise_svd",
                **params,
                **metrics,
            }
        )

    return results


def tune_knn(train_features, test_features):
    grid = {
        "k": [10, 20, 30, 40],
        "min_k": [1, 2, 5],
        "similarity": ["cosine", "msd"],
        "user_based": [True, False],
    }
    results = []

    for params in _parameter_grid(grid):
        model = SurpriseRecommender(algorithm="knn", **params)
        model.fit(train_features)
        metrics = model.evaluate(test_features, k=5)
        results.append(
            {
                "model": "surprise_knn",
                **params,
                **metrics,
            }
        )

    return results


def run_tuning():
    prep = DataPreparation()

    try:
        prep.connect()
        logs = prep.load_navigation_logs()
        prep.load_reports()

        train_logs, test_logs = prep.create_temporal_train_test_split(logs)
        train_features = prep.create_interaction_features(train_logs)
        test_features = prep.create_interaction_features(test_logs)

        baseline = UserBasedCollaborativeFiltering()
        baseline.fit(train_features)
        baseline_metrics = baseline.evaluate(test_features, k=5)

        results = [
            {
                "model": "baseline_user_based_cf",
                "precision_at_k": baseline_metrics["precision_at_k"],
                "ndcg_at_k": baseline_metrics["ndcg_at_k"],
                "evaluated_users": baseline_metrics["evaluated_users"],
            }
        ]

        logger.info("\n🔎 Tuning Surprise SVD")
        results.extend(tune_svd(train_features, test_features))

        logger.info("\n🔎 Tuning Surprise KNN")
        results.extend(tune_knn(train_features, test_features))

        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values(
            ["precision_at_k", "ndcg_at_k"],
            ascending=[False, False],
        ).reset_index(drop=True)

        output_dir = Path(__file__).resolve().parent / "tuning_results"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / "collaborative_tuning_results.csv"
        results_df.to_csv(output_path, index=False)

        logger.info("\n🏁 Top collaborative filtering configurations")
        logger.info(
            results_df.head(10)[
                ["model", "precision_at_k", "ndcg_at_k", "evaluated_users"]
            ].to_string(index=False)
        )
        logger.info("\n📄 Full tuning results saved to %s", output_path)

        return results_df
    finally:
        prep.close()


if __name__ == "__main__":
    run_tuning()
