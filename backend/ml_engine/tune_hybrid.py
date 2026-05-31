#!/usr/bin/env python3
"""
Hybrid Model Tuning.

WHAT: Tune the weighted fusion between collaborative filtering and
content-based recommendations.
WHY: The best balance is data-dependent; too much CF loses content signal, too
much content ignores collective behavior.
HOW: Evaluate several CF backbones and CF weights with the common offline
metrics.
"""

import itertools
import logging
from pathlib import Path

import pandas as pd

try:
    from .data_preparation import DataPreparation
    from .hybrid import HybridRecommender
    from .offline_evaluation import evaluate_recommender
except ImportError:
    from data_preparation import DataPreparation
    from hybrid import HybridRecommender
    from offline_evaluation import evaluate_recommender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_hybrid_tuning():
    prep = DataPreparation()

    try:
        prep.connect()
        logs = prep.load_navigation_logs()
        reports = prep.load_reports()

        train_logs, test_logs = prep.create_temporal_train_test_split(logs)
        train_features = prep.create_interaction_features(train_logs)
        test_features = prep.create_interaction_features(test_logs)
        all_report_ids = sorted(reports["id"].unique().tolist())

        cf_models = ["svd", "knn", "baseline"]
        cf_weights = [round(weight, 1) for weight in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]]
        rows = []

        for cf_model, cf_weight in itertools.product(cf_models, cf_weights):
            logger.info(
                "\n🔎 Tuning hybrid: cf_model=%s cf_weight=%.1f",
                cf_model,
                cf_weight,
            )
            model = HybridRecommender(cf_model=cf_model, cf_weight=cf_weight)
            model.fit(train_features, reports)

            for k in [5, 10]:
                metrics = evaluate_recommender(
                    model_name=f"hybrid_{cf_model}_content",
                    model=model,
                    test_interactions=test_features,
                    all_report_ids=all_report_ids,
                    k=k,
                )
                rows.append(
                    {
                        "cf_model": cf_model,
                        "cf_weight": cf_weight,
                        "content_weight": round(1 - cf_weight, 1),
                        **metrics,
                    }
                )

        results_df = pd.DataFrame(rows).sort_values(
            ["k", "precision_at_k", "ndcg_at_k"],
            ascending=[True, False, False],
        )

        output_dir = Path(__file__).resolve().parent / "tuning_results"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / "hybrid_tuning_results.csv"
        results_df.to_csv(output_path, index=False)

        logger.info("\n🏁 Top hybrid configurations")
        logger.info(
            results_df.head(12)[
                [
                    "cf_model",
                    "cf_weight",
                    "content_weight",
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
    run_hybrid_tuning()
