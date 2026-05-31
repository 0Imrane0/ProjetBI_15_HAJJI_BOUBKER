import unittest

import numpy as np
import pandas as pd

from ml_engine.collaborative import UserBasedCollaborativeFiltering
from ml_engine.content_based import ContentBasedRecommender
from ml_engine.hybrid import HybridRecommender
from ml_engine.offline_evaluation import evaluate_recommender


def sample_interactions():
    return pd.DataFrame(
        [
            {"user_id": 1, "report_id": 1, "implicit_rating": 5.0},
            {"user_id": 1, "report_id": 2, "implicit_rating": 4.0},
            {"user_id": 1, "report_id": 3, "implicit_rating": 2.0},
            {"user_id": 2, "report_id": 1, "implicit_rating": 4.5},
            {"user_id": 2, "report_id": 2, "implicit_rating": 4.0},
            {"user_id": 2, "report_id": 4, "implicit_rating": 5.0},
            {"user_id": 3, "report_id": 3, "implicit_rating": 5.0},
            {"user_id": 3, "report_id": 4, "implicit_rating": 4.5},
            {"user_id": 3, "report_id": 5, "implicit_rating": 4.0},
            {"user_id": 4, "report_id": 2, "implicit_rating": 3.0},
            {"user_id": 4, "report_id": 5, "implicit_rating": 5.0},
            {"user_id": 4, "report_id": 6, "implicit_rating": 4.0},
            {"user_id": 5, "report_id": 1, "implicit_rating": 2.0},
            {"user_id": 5, "report_id": 4, "implicit_rating": 4.0},
            {"user_id": 5, "report_id": 6, "implicit_rating": 5.0},
        ]
    )


def sample_reports():
    return pd.DataFrame(
        [
            {
                "id": 1,
                "metabase_report_id": 101,
                "title": "Sales overview",
                "description": "Monthly revenue and order trends",
                "tags": "sales,revenue",
                "category": "line",
                "business_category": "sales",
            },
            {
                "id": 2,
                "metabase_report_id": 102,
                "title": "Customer subscriptions",
                "description": "Active customers and subscription growth",
                "tags": "customer,subscription",
                "category": "area",
                "business_category": "customer",
            },
            {
                "id": 3,
                "metabase_report_id": 103,
                "title": "Inventory status",
                "description": "Products in stock and reorder alerts",
                "tags": "product,stock",
                "category": "bar",
                "business_category": "product",
            },
            {
                "id": 4,
                "metabase_report_id": 104,
                "title": "Discount impact",
                "description": "Discount amount and margin evolution",
                "tags": "finance,discount",
                "category": "smartscalar",
                "business_category": "finance",
            },
            {
                "id": 5,
                "metabase_report_id": 105,
                "title": "Product category mix",
                "description": "Orders by product family",
                "tags": "product,category",
                "category": "pie",
                "business_category": "product",
            },
            {
                "id": 6,
                "metabase_report_id": 106,
                "title": "Revenue forecast",
                "description": "Expected revenue by quarter",
                "tags": "finance,revenue",
                "category": "line",
                "business_category": "finance",
            },
        ]
    )


class MLModelTest(unittest.TestCase):
    def setUp(self):
        self.interactions = sample_interactions()
        self.reports = sample_reports()

    def assert_valid_recommendations(self, recommendations, expected_count):
        self.assertEqual(len(recommendations), expected_count)
        self.assertEqual(recommendations["rank"].tolist(), list(range(1, expected_count + 1)))
        self.assertTrue(np.isfinite(recommendations["score"]).all())
        self.assertIn("algorithm", recommendations.columns)

    def test_user_based_cf_returns_ranked_unseen_reports(self):
        model = UserBasedCollaborativeFiltering().fit(self.interactions)
        recommendations = model.recommend(1, n_recommendations=2)

        self.assert_valid_recommendations(recommendations, 2)
        self.assertTrue(set(recommendations["report_id"]).isdisjoint({1, 2, 3}))

    def test_content_based_returns_ranked_unseen_reports(self):
        model = ContentBasedRecommender().fit(self.interactions, self.reports)
        recommendations = model.recommend(1, n_recommendations=2)

        self.assert_valid_recommendations(recommendations, 2)
        self.assertTrue(set(recommendations["report_id"]).isdisjoint({1, 2, 3}))

    def test_hybrid_returns_ranked_unseen_reports(self):
        model = HybridRecommender(cf_model="knn", cf_weight=0.6).fit(
            self.interactions,
            self.reports,
        )
        recommendations = model.recommend(1, n_recommendations=2)

        self.assert_valid_recommendations(recommendations, 2)
        self.assertTrue(set(recommendations["report_id"]).isdisjoint({1, 2, 3}))
        self.assertTrue(recommendations["algorithm"].str.startswith("hybrid_").all())

    def test_offline_metrics_are_bounded(self):
        model = UserBasedCollaborativeFiltering().fit(self.interactions)
        test_interactions = pd.DataFrame(
            [
                {"user_id": 1, "report_id": 4, "implicit_rating": 5.0},
                {"user_id": 2, "report_id": 5, "implicit_rating": 4.0},
            ]
        )

        metrics = evaluate_recommender(
            "unit_cf",
            model,
            test_interactions,
            all_report_ids=self.reports["id"].tolist(),
            k=2,
        )

        for key in [
            "precision_at_k",
            "recall_at_k",
            "hit_rate_at_k",
            "ndcg_at_k",
            "catalog_coverage_at_k",
        ]:
            self.assertGreaterEqual(metrics[key], 0.0)
            self.assertLessEqual(metrics[key], 1.0)
        self.assertEqual(metrics["evaluated_users"], 2)


if __name__ == "__main__":
    unittest.main()
