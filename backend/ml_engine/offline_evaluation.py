#!/usr/bin/env python3
"""
Offline Recommendation Evaluation.

WHAT: Compare recommendation models on held-out future interactions.
WHY: We need objective metrics before exposing recommendations through the API.
HOW: Train on the temporal train split, recommend top-k reports, and measure
Precision@k, Recall@k, HitRate@k, NDCG@k, and catalog coverage.
"""

import logging
from pathlib import Path

import numpy as np
import pandas as pd

try:
    from .collaborative import UserBasedCollaborativeFiltering
    from .content_based import ContentBasedRecommender
    from .data_preparation import DataPreparation
    from .hybrid import HybridRecommender
    from .surprise_models import SurpriseRecommender
except ImportError:
    from collaborative import UserBasedCollaborativeFiltering
    from content_based import ContentBasedRecommender
    from data_preparation import DataPreparation
    from hybrid import HybridRecommender
    from surprise_models import SurpriseRecommender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ndcg_at_k(hits, ideal_hit_count):
    if not hits or ideal_hit_count == 0:
        return 0.0

    dcg = sum(hit / np.log2(rank + 2) for rank, hit in enumerate(hits))
    ideal_dcg = sum(1 / np.log2(rank + 2) for rank in range(ideal_hit_count))
    return float(dcg / ideal_dcg) if ideal_dcg else 0.0


def evaluate_recommender(model_name, model, test_interactions, all_report_ids, k):
    """
    Evaluate one fitted recommender at top-k.
    """
    if test_interactions.empty:
        return {
            "model": model_name,
            "k": k,
            "precision_at_k": 0.0,
            "recall_at_k": 0.0,
            "hit_rate_at_k": 0.0,
            "ndcg_at_k": 0.0,
            "catalog_coverage_at_k": 0.0,
            "evaluated_users": 0,
        }

    test_by_user = (
        test_interactions.groupby("user_id")["report_id"]
        .apply(lambda values: set(values))
        .to_dict()
    )

    precisions = []
    recalls = []
    hit_rates = []
    ndcgs = []
    recommended_catalog = set()

    for user_id, relevant_reports in test_by_user.items():
        recommendations = model.recommend(user_id, n_recommendations=k)
        recommended_reports = recommendations["report_id"].tolist()
        recommended_catalog.update(recommended_reports)

        hits = [1 if report_id in relevant_reports else 0 for report_id in recommended_reports]
        hit_count = sum(hits)

        precisions.append(hit_count / k)
        recalls.append(hit_count / len(relevant_reports) if relevant_reports else 0.0)
        hit_rates.append(1.0 if hit_count > 0 else 0.0)
        ndcgs.append(ndcg_at_k(hits, min(len(relevant_reports), k)))

    return {
        "model": model_name,
        "k": k,
        "precision_at_k": float(np.mean(precisions)),
        "recall_at_k": float(np.mean(recalls)),
        "hit_rate_at_k": float(np.mean(hit_rates)),
        "ndcg_at_k": float(np.mean(ndcgs)),
        "catalog_coverage_at_k": len(recommended_catalog) / len(all_report_ids),
        "evaluated_users": len(precisions),
    }


def build_recommender_models():
    return {
        "baseline_user_based_cf": UserBasedCollaborativeFiltering(),
        "tuned_surprise_svd": SurpriseRecommender(algorithm="svd"),
        "tuned_surprise_knn": SurpriseRecommender(algorithm="knn"),
        "content_based_tfidf": ContentBasedRecommender(),
        "hybrid_knn_content": HybridRecommender(),
    }


def run_offline_evaluation(k_values=(5, 10)):
    prep = DataPreparation()

    try:
        prep.connect()
        logs = prep.load_navigation_logs()
        reports = prep.load_reports()

        train_logs, test_logs = prep.create_temporal_train_test_split(logs)
        train_features = prep.create_interaction_features(train_logs)
        test_features = prep.create_interaction_features(test_logs)
        all_report_ids = sorted(reports["id"].unique().tolist())

        rows = []
        models = build_recommender_models()

        for model_name, model in models.items():
            logger.info("\n🧪 Fitting %s", model_name)
            if isinstance(model, HybridRecommender):
                model.fit(train_features, reports)
            elif isinstance(model, ContentBasedRecommender):
                model.fit(train_features, reports)
            else:
                model.fit(train_features)

            for k in k_values:
                metrics = evaluate_recommender(
                    model_name=model_name,
                    model=model,
                    test_interactions=test_features,
                    all_report_ids=all_report_ids,
                    k=k,
                )
                rows.append(metrics)

        results_df = pd.DataFrame(rows).sort_values(
            ["k", "precision_at_k", "ndcg_at_k"],
            ascending=[True, False, False],
        )

        output_dir = Path(__file__).resolve().parent / "evaluation_results"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / "offline_evaluation_results.csv"
        results_df.to_csv(output_path, index=False)

        logger.info("\n🏁 Offline Recommendation Evaluation")
        logger.info(
            results_df[
                [
                    "model",
                    "k",
                    "precision_at_k",
                    "recall_at_k",
                    "hit_rate_at_k",
                    "ndcg_at_k",
                    "catalog_coverage_at_k",
                    "evaluated_users",
                ]
            ].to_string(index=False)
        )
        logger.info("\n📄 Evaluation results saved to %s", output_path)

        return results_df
    finally:
        prep.close()


if __name__ == "__main__":
    run_offline_evaluation()
