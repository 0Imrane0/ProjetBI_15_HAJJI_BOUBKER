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
                timestamp,
                action
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
                category
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
            matrix = prep.create_user_report_matrix(nav_logs)
            logger.info("\n🎉 Data preparation completed successfully!")
        else:
            logger.warning("⚠️ No navigation logs found. Populate data first.")
    
    except Exception as e:
        logger.error(f"❌ Error: {e}")
    
    finally:
        prep.close()
