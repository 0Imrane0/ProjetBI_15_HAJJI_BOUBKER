#!/usr/bin/env python3
"""
Data Preparation Module

WHAT: Handles data loading, exploration, and preparation for ML models
WHY: Clean, well-structured data is essential for accurate recommendations
HOW: Connects to PostgreSQL, loads navigation logs, creates user-report matrix

Tasks:
1. Connect to database
2. Load navigation_logs and reports tables
3. Explore data (statistics, distributions, quality checks)
4. Create user-report interaction matrix
5. Handle missing values and outliers

Author: Person A (Data & AI Engineer)
"""

import os
import logging
import pandas as pd
import numpy as np
import psycopg2
from psycopg2.extras import RealDictCursor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataPreparation:
    """
    Handles all data preparation tasks for the recommendation system.
    """
    
    def __init__(self):
        """Initialize database connection parameters from environment."""
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'user': os.getenv('DB_USER', 'admin'),
            'password': os.getenv('DB_PASSWORD', 'admin123'),
            'dbname': os.getenv('DB_NAME', 'bi_recommendation')
        }
        self.conn = None
    
    def connect(self):
        """
        Establish connection to PostgreSQL database.
        
        WHY: We need data from the database to train models
        """
        try:
            self.conn = psycopg2.connect(**self.db_config)
            logger.info("✅ Connected to database successfully")
            return self.conn
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    def load_navigation_logs(self):
        """
        Load user-report interactions from navigation_logs table.
        
        Returns:
            pandas.DataFrame: Columns: user_id, report_id, duration, timestamp
        
        WHAT: Historical user interactions with reports
        WHY: This is our training data - who viewed what and for how long
        HOW: SQL query to PostgreSQL
        """
        query = """
            SELECT 
                user_id,
                report_id,
                duration,
                duration_source,
                timestamp,
                action,
                event_type,
                metabase_model
            FROM navigation_logs
            ORDER BY timestamp DESC
        """
        
        df = pd.read_sql(query, self.conn)
        logger.info(f"✅ Loaded {len(df)} navigation logs")
        return df
    
    def load_reports(self):
        """
        Load report metadata from reports table.
        
        Returns:
            pandas.DataFrame: Columns: id, title, description, tags, category
        
        WHAT: Report information (titles, descriptions, tags)
        WHY: Needed for content-based filtering
        HOW: SQL query to PostgreSQL
        """
        query = """
            SELECT 
                id,
                metabase_report_id,
                title,
                description,
                tags,
                category,
                business_category
            FROM reports
            ORDER BY id
        """
        
        df = pd.read_sql(query, self.conn)
        logger.info(f"✅ Loaded {len(df)} reports")
        return df
    
    def explore_data(self, df):
        """
        Perform exploratory data analysis.
        
        Args:
            df: DataFrame to explore
        
        WHAT: Understanding the data structure and quality
        WHY: Identify issues before training (missing values, outliers)
        HOW: Statistical analysis and visualization
        """
        logger.info("\n" + "="*50)
        logger.info("📊 DATA EXPLORATION")
        logger.info("="*50)
        
        # Basic info
        logger.info(f"\n🔢 Shape: {df.shape}")
        logger.info(f"📋 Columns: {list(df.columns)}")
        
        # Data types
        logger.info("\n📝 Data Types:")
        logger.info(df.dtypes)
        
        # Missing values
        logger.info("\n❓ Missing Values:")
        logger.info(df.isnull().sum())
        
        # Basic statistics
        logger.info("\n📈 Statistics:")
        logger.info(df.describe())
        
        # Unique counts
        if 'user_id' in df.columns:
            logger.info(f"\n👥 Unique Users: {df['user_id'].nunique()}")
        if 'report_id' in df.columns:
            logger.info(f"📄 Unique Reports: {df['report_id'].nunique()}")
        
        return df
    
    def create_user_report_matrix(self, df):
        """
        Create user-report interaction matrix.
        
        Args:
            df: Navigation logs DataFrame
        
        Returns:
            pandas.DataFrame: Matrix where rows=users, columns=reports, values=duration
        
        WHAT: A matrix showing how much each user engaged with each report
        WHY: Required input for collaborative filtering
        HOW: Pivot table aggregation
        
        Example:
                 report_1  report_2  report_3
        user_1      120        85         0
        user_2      200         0        45
        user_3        0       150       180
        """
        matrix = df.pivot_table(
            index='user_id',
            columns='report_id',
            values='duration',
            aggfunc='sum',  # If user viewed same report multiple times, sum duration
            fill_value=0    # Fill missing values with 0 (not viewed)
        )
        
        logger.info(f"\n✅ User-Report Matrix created: {matrix.shape}")
        logger.info(f"   Users: {matrix.shape[0]}, Reports: {matrix.shape[1]}")
        logger.info(f"   Sparsity: {(matrix == 0).sum().sum() / (matrix.shape[0] * matrix.shape[1]) * 100:.2f}%")
        
        return matrix

    def create_temporal_train_test_split(
        self,
        df,
        test_ratio=0.2,
        min_events_per_user=5,
    ):
        """
        Split interactions by user timeline.

        WHAT: Keep the oldest interactions for training and the most recent
        interactions for testing.
        WHY: Recommendation models should learn from the past and be evaluated
        on future-like behavior, not on random leaked interactions.
        HOW: For each user, sort events by timestamp and reserve the last 20%
        by default for test.
        """
        required_columns = {"user_id", "report_id", "timestamp"}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

        if df.empty:
            logger.warning("⚠️ Empty dataframe received for train/test split")
            return df.copy(), df.copy()

        work_df = df.copy()
        work_df["timestamp"] = pd.to_datetime(work_df["timestamp"])
        work_df = work_df.sort_values(["user_id", "timestamp"])

        train_parts = []
        test_parts = []

        for _, user_df in work_df.groupby("user_id", sort=False):
            if len(user_df) < min_events_per_user:
                train_parts.append(user_df)
                continue

            test_size = max(1, int(np.ceil(len(user_df) * test_ratio)))
            split_index = len(user_df) - test_size
            train_parts.append(user_df.iloc[:split_index])
            test_parts.append(user_df.iloc[split_index:])

        train_df = pd.concat(train_parts, ignore_index=True) if train_parts else work_df.iloc[0:0]
        test_df = pd.concat(test_parts, ignore_index=True) if test_parts else work_df.iloc[0:0]

        logger.info("\n✅ Temporal train/test split created")
        logger.info(f"   Train events: {len(train_df)} ({len(train_df) / len(work_df) * 100:.2f}%)")
        logger.info(f"   Test events: {len(test_df)} ({len(test_df) / len(work_df) * 100:.2f}%)")
        logger.info(f"   Train users: {train_df['user_id'].nunique() if not train_df.empty else 0}")
        logger.info(f"   Test users: {test_df['user_id'].nunique() if not test_df.empty else 0}")

        return train_df, test_df

    def create_interaction_features(self, df, reference_time=None):
        """
        Build user-report interaction features.

        WHAT: Aggregate raw events into one row per user/report pair.
        WHY: Models need a compact signal that says how strong each user-report
        relationship is.
        HOW: Combine frequency, duration, action strength, and recency.
        """
        required_columns = {"user_id", "report_id", "action", "duration", "timestamp"}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

        if df.empty:
            logger.warning("⚠️ Empty dataframe received for interaction features")
            return pd.DataFrame()

        work_df = df.copy()
        work_df["timestamp"] = pd.to_datetime(work_df["timestamp"])
        work_df["duration"] = work_df["duration"].fillna(0).clip(lower=0)
        work_df["action_weight"] = work_df["action"].map(
            {"view": 1.0, "selection": 2.5}
        ).fillna(1.0)

        if reference_time is None:
            reference_time = work_df["timestamp"].max()
        reference_time = pd.to_datetime(reference_time)

        features = work_df.groupby(["user_id", "report_id"]).agg(
            view_count=("report_id", "size"),
            selection_count=("action", lambda actions: (actions == "selection").sum()),
            total_duration=("duration", "sum"),
            avg_duration=("duration", "mean"),
            action_weight_sum=("action_weight", "sum"),
            first_viewed=("timestamp", "min"),
            last_viewed=("timestamp", "max"),
        ).reset_index()

        features["recency_days"] = (
            reference_time - features["last_viewed"]
        ).dt.total_seconds() / 86400
        features["recency_days"] = features["recency_days"].clip(lower=0)
        features["recency_boost"] = np.exp(-features["recency_days"] / 14)
        features["selection_rate"] = (
            features["selection_count"] / features["view_count"]
        ).fillna(0)

        raw_score = (
            np.log1p(features["view_count"])
            + 0.35 * np.log1p(features["total_duration"])
            + 0.8 * features["selection_count"]
            + features["recency_boost"]
        )
        if raw_score.max() > raw_score.min():
            features["implicit_rating"] = 1 + 4 * (
                (raw_score - raw_score.min()) / (raw_score.max() - raw_score.min())
            )
        else:
            features["implicit_rating"] = 1.0

        logger.info("\n✅ Interaction features created")
        logger.info(f"   Rows: {len(features)} user-report pairs")
        logger.info(
            f"   Rating range: {features['implicit_rating'].min():.2f} - "
            f"{features['implicit_rating'].max():.2f}"
        )
        return features

    def create_user_features(self, logs_df, reports_df):
        """
        Build user-level features.

        WHAT: Summarize each user's behavior.
        WHY: Useful for segmentation, hybrid ranking, and debugging recommendations.
        HOW: Aggregate activity volume, diversity, duration, selection rate, and
        favorite business category.
        """
        if logs_df.empty:
            logger.warning("⚠️ Empty logs received for user features")
            return pd.DataFrame()

        work_df = logs_df.copy()
        work_df["timestamp"] = pd.to_datetime(work_df["timestamp"])
        work_df["duration"] = work_df["duration"].fillna(0).clip(lower=0)

        user_features = work_df.groupby("user_id").agg(
            event_count=("report_id", "size"),
            unique_reports=("report_id", "nunique"),
            total_duration=("duration", "sum"),
            avg_duration=("duration", "mean"),
            selection_count=("action", lambda actions: (actions == "selection").sum()),
            first_seen=("timestamp", "min"),
            last_seen=("timestamp", "max"),
        ).reset_index()
        user_features["selection_rate"] = (
            user_features["selection_count"] / user_features["event_count"]
        ).fillna(0)
        user_features["activity_span_days"] = (
            user_features["last_seen"] - user_features["first_seen"]
        ).dt.total_seconds() / 86400

        if not reports_df.empty and "business_category" in reports_df.columns:
            report_categories = reports_df[["id", "business_category"]].rename(
                columns={"id": "report_id"}
            )
            category_events = work_df.merge(report_categories, on="report_id", how="left")
            category_events["business_category"] = category_events[
                "business_category"
            ].fillna("general")
            favorite_category = (
                category_events.groupby(["user_id", "business_category"])
                .size()
                .reset_index(name="category_events")
                .sort_values(["user_id", "category_events"], ascending=[True, False])
                .drop_duplicates("user_id")
                [["user_id", "business_category"]]
                .rename(columns={"business_category": "favorite_category"})
            )
            user_features = user_features.merge(favorite_category, on="user_id", how="left")
        else:
            user_features["favorite_category"] = "general"

        logger.info("\n✅ User features created")
        logger.info(f"   Users: {len(user_features)}")
        return user_features

    def create_report_features(self, logs_df, reports_df):
        """
        Build report-level features.

        WHAT: Summarize popularity and engagement for each report.
        WHY: Useful for popularity baselines, cold-start handling, and hybrid models.
        HOW: Combine usage statistics with report metadata.
        """
        if reports_df.empty:
            logger.warning("⚠️ Empty reports received for report features")
            return pd.DataFrame()

        work_df = logs_df.copy()
        work_df["timestamp"] = pd.to_datetime(work_df["timestamp"])
        work_df["duration"] = work_df["duration"].fillna(0).clip(lower=0)

        report_features = work_df.groupby("report_id").agg(
            event_count=("user_id", "size"),
            unique_users=("user_id", "nunique"),
            total_duration=("duration", "sum"),
            avg_duration=("duration", "mean"),
            selection_count=("action", lambda actions: (actions == "selection").sum()),
            last_seen=("timestamp", "max"),
        ).reset_index()
        report_features["selection_rate"] = (
            report_features["selection_count"] / report_features["event_count"]
        ).fillna(0)
        report_features["popularity_score"] = np.log1p(report_features["event_count"])

        metadata = reports_df.rename(columns={"id": "report_id"})
        report_features = metadata.merge(report_features, on="report_id", how="left")
        numeric_columns = [
            "event_count",
            "unique_users",
            "total_duration",
            "avg_duration",
            "selection_count",
            "selection_rate",
            "popularity_score",
        ]
        report_features[numeric_columns] = report_features[numeric_columns].fillna(0)
        report_features["business_category"] = report_features[
            "business_category"
        ].fillna("general")

        logger.info("\n✅ Report features created")
        logger.info(f"   Reports: {len(report_features)}")
        return report_features
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("✅ Database connection closed")


# ============ Example Usage ============

if __name__ == "__main__":
    """
    Test the data preparation pipeline.
    
    Run this to verify everything works:
        python backend/ml_engine/data_preparation.py
    """
    
    prep = DataPreparation()
    
    try:
        # Connect to database
        prep.connect()
        
        # Load navigation logs
        nav_logs = prep.load_navigation_logs()
        prep.explore_data(nav_logs)
        
        # Load reports
        reports = prep.load_reports()
        prep.explore_data(reports)
        
        # Create matrix
        if len(nav_logs) > 0:
            train_df, test_df = prep.create_temporal_train_test_split(nav_logs)
            logger.info(
                f"\n📌 Split ready: train={len(train_df)} rows, test={len(test_df)} rows"
            )
            interaction_features = prep.create_interaction_features(train_df)
            user_features = prep.create_user_features(train_df, reports)
            report_features = prep.create_report_features(train_df, reports)
            matrix = prep.create_user_report_matrix(nav_logs)
            logger.info(
                "\n📌 Features ready: "
                f"interactions={len(interaction_features)}, "
                f"users={len(user_features)}, reports={len(report_features)}"
            )
            logger.info("\n🎉 Data preparation completed successfully!")
        else:
            logger.warning("⚠️ No navigation logs found. Populate data first.")
    
    except Exception as e:
        logger.error(f"❌ Error: {e}")
    
    finally:
        prep.close()
