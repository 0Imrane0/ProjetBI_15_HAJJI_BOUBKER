#!/usr/bin/env python3
"""
Create Metabase Reports Script
Crée automatiquement les rapports (report_card) dans PostgreSQL
pour que generate_data.py puisse les référencer.

Ce script insère 40 rapports avec:
- Titres réalistes
- Catégories (Finance, Sales, Analytics, etc.)
- Descriptions
"""

import os
from datetime import datetime

import psycopg2
from psycopg2.extras import execute_values

# Configuration - Auto-détecte si on est en Docker ou en local
DOCKER_ENV = os.getenv("DOCKER_ENV", "false").lower() == "true"
DB_HOST = os.getenv("DB_HOST", "postgres" if DOCKER_ENV else "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin123")
DB_NAME = os.getenv("DB_NAME", "bi_recommendation")

# ─── Rapports à créer (40 rapports) ───────────────────────────────────────────

REPORTS = [
    # 1-10: Finance & Revenue
    (1, "Revenue Dashboard", "Total revenue by period", "table", False),
    (
        2,
        "Revenue by Region",
        "Break down of revenue by geographic region",
        "bar",
        False,
    ),
    (3, "Product Performance", "Sales performance by product category", "line", False),
    (4, "Customer Lifetime Value", "CLV analysis and trends", "scatter", False),
    (5, "Monthly Revenue Trend", "Revenue over time with forecasts", "area", False),
    (6, "Revenue Forecast", "Predicted revenue for next quarter", "line", False),
    (
        7,
        "Sales by Category",
        "Sales distribution across product categories",
        "pie",
        False,
    ),
    (8, "Top Customers", "Biggest spenders and growth opportunities", "table", False),
    (9, "Profit Margin Analysis", "Profit margins by product and region", "bar", False),
    (10, "Cash Flow Report", "Cash inflow and outflow analysis", "waterfall", False),
    # 11-20: Sales & Orders
    (11, "Sales Funnel", "Conversion rates through sales pipeline", "funnel", False),
    (12, "Orders by Date", "Order volume trends over time", "line", False),
    (13, "Average Order Value", "AOV trends and analysis", "line", False),
    (14, "Sales Rep Performance", "Individual sales performance metrics", "bar", False),
    (15, "Regional Sales", "Sales breakdown by region and period", "table", False),
    (16, "Customer Acquisition Cost", "CAC trends and channel analysis", "bar", False),
    (17, "Repeat Purchase Rate", "Customer retention and repeat orders", "line", False),
    (18, "Order Status Dashboard", "Real-time order status tracking", "pie", False),
    (19, "Sales Growth YoY", "Year-over-year sales comparison", "bar", False),
    (20, "Pipeline Health", "Deal pipeline and forecasted revenue", "funnel", False),
    # 21-30: Customer & Marketing
    (21, "Customer Segments", "Customer segmentation and clustering", "scatter", False),
    (
        22,
        "Customer Churn Prediction",
        "At-risk customers identification",
        "table",
        False,
    ),
    (23, "NPS Score Trend", "Net Promoter Score evolution", "line", False),
    (24, "Marketing ROI", "Return on investment by campaign", "bar", False),
    (25, "Campaign Performance", "Email and ad campaign metrics", "table", False),
    (
        26,
        "Customer Geographic Distribution",
        "Geographic heatmap of customers",
        "map",
        False,
    ),
    (27, "Support Ticket Analysis", "Support volume and resolution time", "bar", False),
    (28, "Customer Satisfaction", "CSAT scores and feedback summary", "gauge", False),
    (29, "Email Campaign Analytics", "Open rates, clicks, conversions", "line", False),
    (
        30,
        "Social Media Engagement",
        "Followers, likes, engagement rates",
        "area",
        False,
    ),
    # 31-40: Analytics & Operations
    (31, "Page Views & Bounce Rate", "Website traffic and engagement", "line", False),
    (32, "User Behavior Funnel", "User journey and drop-off analysis", "funnel", False),
    (33, "Event Analytics", "Tracking key product events", "bar", False),
    (34, "Data Quality Report", "Data completeness and anomalies", "table", False),
    (35, "System Performance", "API latency and error rates", "line", False),
    (36, "Inventory Status", "Stock levels and reorder alerts", "gauge", False),
    (37, "Operational Metrics", "KPIs for operations team", "table", False),
    (
        38,
        "Marketing Funnel",
        "AARRR metrics (Awareness, Acquisition, etc.)",
        "funnel",
        False,
    ),
    (39, "Product Adoption", "Feature usage and adoption rates", "bar", False),
    (40, "Executive Summary", "Key metrics dashboard for leadership", "table", False),
]

# ─── Connection ───────────────────────────────────────────────────────────────


def get_db():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME,
    )


# ─── Main ─────────────────────────────────────────────────────────────────────


def create_reports():
    """Crée les 40 rapports dans la table report_card de Metabase"""

    print("\n" + "=" * 70)
    print("🚀 CREATING METABASE REPORTS")
    print("=" * 70)

    try:
        conn = get_db()
        print("✅ Connected to PostgreSQL")

        with conn.cursor() as cur:
            # Préparer les données pour insertion
            values = [
                (
                    report[0],  # id
                    report[1],  # name (title)
                    report[2],  # description
                    report[3],  # display (visualization type)
                    report[4],  # archived
                    datetime.utcnow(),  # created_at
                    datetime.utcnow(),  # updated_at
                )
                for report in REPORTS
            ]

            # Insérer les rapports
            execute_values(
                cur,
                """
                INSERT INTO report_card (id, name, description, display, archived, created_at, updated_at)
                VALUES %s
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    display = EXCLUDED.display,
                    updated_at = EXCLUDED.updated_at
                """,
                values,
            )
            conn.commit()

            # Vérifier l'insertion
            cur.execute("SELECT COUNT(*) FROM report_card")
            count = cur.fetchone()[0]

            print(f"\n✅ Successfully created {len(REPORTS)} reports")
            print(f"📊 Total reports in database: {count}")

            # Afficher un exemple
            print("\n📋 Sample reports created:")
            cur.execute("SELECT id, name, display FROM report_card LIMIT 5")
            for row in cur.fetchall():
                print(f"   {row[0]:2d}. {row[1]:30s} ({row[2]})")

        conn.close()

        print("\n" + "=" * 70)
        print("✅ DONE! You can now run generate_data.py")
        print("=" * 70 + "\n")
        return True

    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        return False


if __name__ == "__main__":
    success = create_reports()
    exit(0 if success else 1)
