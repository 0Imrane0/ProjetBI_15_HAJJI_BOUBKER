import unittest

import pandas as pd

from ml_engine.data_preparation import DataPreparation


class DataPreparationTest(unittest.TestCase):
    def setUp(self):
        self.prep = DataPreparation()
        self.logs = pd.DataFrame(
            [
                {
                    "user_id": 1,
                    "report_id": 1,
                    "action": "view",
                    "duration": 60,
                    "timestamp": "2026-05-01T10:00:00Z",
                },
                {
                    "user_id": 1,
                    "report_id": 2,
                    "action": "selection",
                    "duration": 120,
                    "timestamp": "2026-05-02T10:00:00Z",
                },
                {
                    "user_id": 1,
                    "report_id": 3,
                    "action": "view",
                    "duration": 30,
                    "timestamp": "2026-05-03T10:00:00Z",
                },
                {
                    "user_id": 2,
                    "report_id": 1,
                    "action": "view",
                    "duration": 45,
                    "timestamp": "2026-05-01T11:00:00Z",
                },
                {
                    "user_id": 2,
                    "report_id": 2,
                    "action": "view",
                    "duration": 90,
                    "timestamp": "2026-05-02T11:00:00Z",
                },
                {
                    "user_id": 2,
                    "report_id": 4,
                    "action": "selection",
                    "duration": 180,
                    "timestamp": "2026-05-03T11:00:00Z",
                },
            ]
        )

    def test_temporal_split_keeps_latest_events_for_test(self):
        train_df, test_df = self.prep.create_temporal_train_test_split(
            self.logs,
            test_ratio=0.2,
            min_events_per_user=2,
        )

        self.assertEqual(len(train_df), 4)
        self.assertEqual(len(test_df), 2)
        self.assertEqual(set(test_df["report_id"]), {3, 4})

    def test_interaction_features_create_implicit_rating(self):
        features = self.prep.create_interaction_features(self.logs)

        self.assertIn("implicit_rating", features.columns)
        self.assertEqual(len(features), 6)
        self.assertGreaterEqual(features["implicit_rating"].min(), 1.0)
        self.assertLessEqual(features["implicit_rating"].max(), 5.0)
        self.assertGreater(features["selection_count"].sum(), 0)


if __name__ == "__main__":
    unittest.main()
