#!/usr/bin/env python3
"""
Content-Based Hyperparameter Tuning.

WHAT: Tune TF-IDF parameters for the content-based recommender.
WHY: Text representation choices can affect ranking quality.
HOW: Try a small grid of n-grams, feature limits, and TF scaling.
"""

import itertools
import logging
from pathlib import Path

import pandas as pd

try:
    from .content_based import ContentBasedRecommender
    from .data_preparation import DataPreparation
    from .offline_evaluation import evaluate_recommender
except ImportError:
    from content_based import ContentBasedRecommender
    from data_preparation import DataPreparation
    from offline_evaluation import evaluate_recommender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _parameter_grid(grid):
    keys = list(grid.keys())
    for values in itertools.product(*(grid[key] for key in keys)):
        yield dict(zip(keys, values))


def run_content_tuning():
    prep = DataPreparation()

    try:
        prep.connect()
        logs = prep.load_navigation_logs()
        reports = prep.load_reports()

        train_logs, test_logs = prep.create_temporal_train_test_split(logs)
        train_features = prep.create_interaction_features(train_logs)
        test_features = prep.create_interaction_features(test_logs)
        all_report_ids = sorted(reports["id"].unique().tolist())

        grid = {
            "ngram_range": [(1, 1), (1, 2), (1, 3)],
            "max_features": [100, 300, 500, None],
            "sublinear_tf": [False, True],
        }

        rows = []
        for params in _parameter_grid(grid):
            model = ContentBasedRecommender(**params)
            model.fit(train_features, reports)
            metrics_5 = evaluate_recommender(
                "content_based_tfidf",
                model,
                test_features,
                all_report_ids,
                k=5,
            )
            metrics_10 = evaluate_recommender(
                "content_based_tfidf",
                model,
                test_features,
                all_report_ids,
                k=10,
            )
            rows.extend(
                [
                    {**params, **metrics_5},
                    {**params, **metrics_10},
                ]
            )

        results_df = pd.DataFrame(rows).sort_values(
            ["k", "precision_at_k", "ndcg_at_k"],
            ascending=[True, False, False],
        )

        output_dir = Path(__file__).resolve().parent / "tuning_results"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / "content_based_tuning_results.csv"
        results_df.to_csv(output_path, index=False)

        logger.info("\n🏁 Top content-based configurations")
        logger.info(
            results_df.head(10)[
                [
                    "ngram_range",
                    "max_features",
                    "sublinear_tf",
                    "k",
                    "precision_at_k",
                    "ndcg_at_k",
                    "catalog_coverage_at_k",
                ]
            ].to_string(index=False)
        )
        logger.info("\n📄 Full tuning results saved to %s", output_path)

        return results_df
    finally:
        prep.close()


if __name__ == "__main__":
    run_content_tuning()
