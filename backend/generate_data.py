#!/usr/bin/env python3
"""
BI Adaptive - Fake Data Generator
Generates 100 realistic Metabase users across 6 clusters
and inserts fake recent_views directly into PostgreSQL.
"""

import os
import random
import string
from datetime import datetime, timedelta

import psycopg2
import psycopg2.extras

# ─── Config ───────────────────────────────────────────────────────────────────

# Détection automatique: si on tourne en Docker, utiliser "postgres", sinon "localhost"
DOCKER_ENV = os.getenv("DOCKER_ENV", "false").lower() == "true"
DB_HOST = os.getenv("DB_HOST", "postgres" if DOCKER_ENV else "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin123")
DB_NAME = os.getenv("DB_NAME", "bi_recommendation")

TOTAL_USERS = 100
USERS_PER_CLUSTER = 17  # ~17 per cluster (last cluster gets remainder)
MIN_VIEWS = 50
MAX_VIEWS = 150
DAYS_BACK = 30
NOISE_RATIO = 0.30  # 30% random reports outside preferred

ALL_REPORT_IDS = list(range(1, 41))  # report_card ids 1-40

# ─── Clusters ─────────────────────────────────────────────────────────────────

CLUSTERS = [
    {
        "name": "Sales Manager",
        "role": "sales_manager",
        "reports": [2, 6, 9, 12, 13, 15, 17, 19, 21, 31, 39],  # revenue, orders, funnel
        "contexts": {"view": 0.80, "selection": 0.20},
        "models": {"card": 0.70, "dashboard": 0.30},
    },
    {
        "name": "Product Analyst",
        "role": "product_analyst",
        "reports": [
            3,
            4,
            7,
            8,
            18,
            20,
            22,
            24,
            38,
            40,
        ],  # products, categories, ratings
        "contexts": {"view": 0.85, "selection": 0.15},
        "models": {"card": 0.90, "dashboard": 0.10},
    },
    {
        "name": "Marketing Analyst",
        "role": "marketing_analyst",
        "reports": [3, 5, 10, 11, 28, 30, 35, 36],  # customer behavior, sources, age
        "contexts": {"view": 0.85, "selection": 0.15},
        "models": {"card": 0.85, "dashboard": 0.15},
    },
    {
        "name": "Finance Executive",
        "role": "finance_executive",
        "reports": [
            9,
            14,
            15,
            16,
            17,
            25,
            27,
            34,
            39,
        ],  # KPIs, subscriptions, discounts
        "contexts": {"view": 0.75, "selection": 0.25},
        "models": {"card": 0.65, "dashboard": 0.35},
    },
    {
        "name": "Operations Manager",
        "role": "operations_manager",
        "reports": [19, 20, 24, 26, 27, 29, 37, 39, 12],  # quantities, trends, totals
        "contexts": {"view": 0.90, "selection": 0.10},
        "models": {"card": 0.95, "dashboard": 0.05},
    },
    {
        "name": "Data Analyst",
        "role": "data_analyst",
        "reports": [1, 5, 25, 32, 33, 35, 40, 10, 8],  # raw tables, deep dives
        "contexts": {"view": 0.95, "selection": 0.05},
        "models": {"card": 0.98, "dashboard": 0.02},
    },
]


# ─── Helpers ──────────────────────────────────────────────────────────────────


def random_email(first: str, last: str, idx: int) -> str:
    return f"{first.lower()}.{last.lower()}{idx}@company.com"


def random_name():
    firstnames = [
        "Alice",
        "Bob",
        "Charlie",
        "Diana",
        "Eve",
        "Frank",
        "Grace",
        "Hank",
        "Iris",
        "Jack",
        "Karen",
        "Leo",
        "Mia",
        "Nate",
        "Olivia",
        "Paul",
        "Quinn",
        "Rachel",
        "Sam",
        "Tina",
        "Uma",
        "Victor",
        "Wendy",
        "Xavier",
        "Yara",
        "Zoe",
        "Adam",
        "Bella",
        "Carlos",
        "Daisy",
    ]
    lastnames = [
        "Smith",
        "Johnson",
        "Williams",
        "Brown",
        "Jones",
        "Garcia",
        "Miller",
        "Davis",
        "Wilson",
        "Moore",
        "Taylor",
        "Anderson",
        "Thomas",
        "Jackson",
        "White",
        "Harris",
        "Martin",
        "Thompson",
        "Young",
        "Allen",
    ]
    return random.choice(firstnames), random.choice(lastnames)


def random_working_timestamp(days_back: int) -> datetime:
    """Random timestamp within working hours (8am-7pm), no weekends."""
    now = datetime.utcnow()
    while True:
        delta = timedelta(
            days=random.randint(0, days_back),
            hours=random.randint(8, 19),
            minutes=random.randint(0, 59),
        )
        ts = now - delta
        if ts.weekday() < 5:  # Mon-Fri only
            return ts


def pick_report(cluster: dict) -> tuple:
    """Pick a report_id and model based on cluster preferences + noise."""
    if random.random() < NOISE_RATIO:
        report_id = random.choice(ALL_REPORT_IDS)
    else:
        report_id = random.choice(cluster["reports"])

    model = random.choices(
        list(cluster["models"].keys()), weights=list(cluster["models"].values())
    )[0]
    context = random.choices(
        list(cluster["contexts"].keys()), weights=list(cluster["contexts"].values())
    )[0]

    # dashboards only have id 1 in your data — keep model consistent
    if model == "dashboard":
        report_id = 1

    return report_id, model, context


# ─── DB ───────────────────────────────────────────────────────────────────────


def get_db():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME,
        cursor_factory=psycopg2.extras.RealDictCursor,
    )


def get_next_metabase_user_id(conn) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM core_user")
        row = cur.fetchone()
        return list(row.values())[0]


def insert_core_user(conn, mb_id: int, email: str, first: str, last: str) -> int:
    """Insert a fake user into Metabase's core_user table."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO core_user (
                id, email, first_name, last_name,
                password, password_salt,
                date_joined, is_superuser, is_active,
                is_qbnewb, is_datasetnewb, type
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s,
                NOW(), false, true,
                false, false, 'personal'
            )
            ON CONFLICT (id) DO NOTHING
            RETURNING id
        """,
            (
                mb_id,
                email,
                first,
                last,
                "".join(random.choices(string.ascii_letters, k=60)),
                "".join(random.choices(string.ascii_letters, k=20)),
            ),
        )
        result = cur.fetchone()
    conn.commit()
    return mb_id


def insert_recent_view(
    conn, user_id: int, model: str, model_id: int, context: str, ts: datetime
):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO recent_views (user_id, model, model_id, timestamp, context)
            VALUES (%s, %s, %s, %s, %s)
        """,
            (user_id, model, model_id, ts, context),
        )
    conn.commit()


# ─── Main ─────────────────────────────────────────────────────────────────────


def run():
    conn = get_db()
    print("✅ Connected to PostgreSQL")

    next_id = get_next_metabase_user_id(conn)
    total_users = 0
    total_views = 0

    for cluster_idx, cluster in enumerate(CLUSTERS):
        # Last cluster absorbs remainder
        count = (
            USERS_PER_CLUSTER
            if cluster_idx < 5
            else (TOTAL_USERS - USERS_PER_CLUSTER * 5)
        )
        print(f"\n👥 Cluster: {cluster['name']} ({count} users)")

        for i in range(count):
            first, last = random_name()
            email = random_email(first, last, next_id)
            mb_id = next_id
            next_id += 1

            insert_core_user(conn, mb_id, email, first, last)
            total_users += 1

            # Generate views for this user
            num_views = random.randint(MIN_VIEWS, MAX_VIEWS)
            for _ in range(num_views):
                report_id, model, context = pick_report(cluster)
                ts = random_working_timestamp(DAYS_BACK)
                insert_recent_view(conn, mb_id, model, report_id, context, ts)
                total_views += 1

            print(f"  ✔ {first} {last} ({email}) — {num_views} views")

    conn.close()
    print(
        f"\n🎉 Done! {total_users} users, {total_views} views inserted into recent_views."
    )
    print(
        "Now reset publisher cursors and restart the pipeline to sync into your tables."
    )


if __name__ == "__main__":
    run()
