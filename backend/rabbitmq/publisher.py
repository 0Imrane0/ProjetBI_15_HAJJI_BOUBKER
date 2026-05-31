#!/usr/bin/env python3
"""
BI Adaptive - Publisher
Streams 3 Metabase tables → RabbitMQ in parallel threads:
  - recent_views  → queue: navigation_logs
  - core_user     → queue: users_sync
  - report_card   → queue: reports_sync
"""

import json
import logging
import os
import hashlib
import threading
import time
from datetime import datetime
from typing import Optional

import psycopg2
import psycopg2.extras
import pika

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("publisher")

# ─── Config ───────────────────────────────────────────────────────────────────

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")

DB_HOST     = os.getenv("DB_HOST",     "postgres")
DB_PORT     = int(os.getenv("DB_PORT", "5432"))
DB_USER     = os.getenv("DB_USER",     "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin123")
DB_NAME     = os.getenv("DB_NAME",     "bi_recommendation")

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "5"))
SIMULATE_DURATION = os.getenv("SIMULATE_DURATION", "true").lower() == "true"


# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_db():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        user=DB_USER, password=DB_PASSWORD,
        dbname=DB_NAME,
        cursor_factory=psycopg2.extras.RealDictCursor,
    )


def load_cursor(conn, stream: str) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT last_id FROM publisher_state WHERE stream = %s", (stream,))
        row = cur.fetchone()
        return row["last_id"] if row else 0


def save_cursor(conn, stream: str, last_id: int):
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE publisher_state SET last_id = %s, updated_at = NOW() WHERE stream = %s",
            (last_id, stream)
        )
    conn.commit()


def make_rabbit_channel(queue_name: str):
    """Dedicated RabbitMQ connection per thread."""
    creds  = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    params = pika.ConnectionParameters(
        host=RABBITMQ_HOST, port=RABBITMQ_PORT,
        credentials=creds,
        connection_attempts=10, retry_delay=3,
        heartbeat=600,
    )
    conn    = pika.BlockingConnection(params)
    channel = conn.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    return conn, channel


def publish(channel, queue: str, event: dict):
    channel.basic_publish(
        exchange="",
        routing_key=queue,
        body=json.dumps(event, default=str),
        properties=pika.BasicProperties(delivery_mode=2),
    )


def stable_int(*parts) -> int:
    raw = "|".join(str(part) for part in parts)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def simulated_duration(row: dict) -> int:
    """Return a deterministic fake engagement duration for demo data."""
    action = row.get("context") or "view"
    if action == "selection":
        low, high = 90, 600
    else:
        low, high = 15, 240

    span = high - low + 1
    seconds = low + stable_int(row["id"], row["user_id"], row["model_id"], action) % span

    if row.get("model") == "dashboard":
        seconds = int(seconds * 1.4)

    return min(seconds, 900)


def infer_business_category(title: str, description: Optional[str]) -> str:
    text = f"{title or ''} {description or ''}".lower()
    keywords = {
        "sales": ["sales", "order", "pipeline", "revenue", "deal"],
        "finance": ["profit", "cash", "margin", "cost", "discount"],
        "marketing": ["marketing", "campaign", "email", "social", "funnel"],
        "customer": ["customer", "churn", "satisfaction", "nps", "support"],
        "product": ["product", "adoption", "category", "feature"],
        "operations": ["inventory", "operational", "system", "performance", "quality"],
    }

    for category, terms in keywords.items():
        if any(term in text for term in terms):
            return category

    return "general"


# ─── Stream queries ───────────────────────────────────────────────────────────

def fetch_recent_views(conn, after_id: int) -> list:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                rv.id,
                rv.user_id     AS metabase_user_id,
                rv.model,
                rv.model_id    AS metabase_report_id,
                rv.timestamp,
                rv.context, 
                cu.email::text AS email,
                cu.first_name,
                cu.last_name
            FROM recent_views rv
            JOIN core_user cu ON rv.user_id = cu.id
            WHERE rv.id > %s
              
            ORDER BY rv.id ASC
        """, (after_id,))
        return cur.fetchall()


def fetch_core_users(conn, after_id: int) -> list:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                id,
                email::text AS email,
                first_name,
                last_name,
                is_superuser,
                is_active,
                date_joined,
                updated_at
            FROM core_user
            WHERE id > %s
              AND is_active = true
              AND type = 'personal'
            ORDER BY id ASC
        """, (after_id,))
        return cur.fetchall()


def fetch_report_cards(conn, after_id: int) -> list:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                id,
                name        AS title,
                description,
                display     AS visualization_type,
                created_at,
                updated_at
            FROM report_card
            WHERE id > %s
              AND archived = false
            ORDER BY id ASC
        """, (after_id,))
        return cur.fetchall()


# ─── Row → event converters ───────────────────────────────────────────────────

def view_to_event(row: dict) -> dict:
    duration = simulated_duration(row) if SIMULATE_DURATION else 0
    return {
        "stream":             "recent_views",
        "source_event_id":    row["id"],
        "metabase_user_id":   row["metabase_user_id"],
        "metabase_report_id": row["metabase_report_id"],
        "metabase_model":     row["model"],
        "metabase_model_id":  row["metabase_report_id"],
        "model":              row["model"],
        "action":             row["context"],
        "event_type":         row["context"] or "view",
        "duration":           duration,
        "duration_source":    "simulated" if SIMULATE_DURATION else "unknown",
        "timestamp":          row["timestamp"].isoformat() if row["timestamp"] else datetime.utcnow().isoformat(),
        "user_email":         row["email"],
        "user_name":          f"{row['first_name'] or ''} {row['last_name'] or ''}".strip(),
    }


def user_to_event(row: dict) -> dict:
    return {
        "stream":           "core_user",
        "metabase_user_id": row["id"],
        "email":            row["email"],
        "name":             f"{row['first_name'] or ''} {row['last_name'] or ''}".strip(),
        "role":             "admin" if row["is_superuser"] else "user",
        "date_joined":      row["date_joined"].isoformat() if row["date_joined"] else None,
    }


def card_to_event(row: dict) -> dict:
    return {
        "stream":             "report_card",
        "metabase_report_id": row["id"],
        "title":              row["title"],
        "description":        row["description"],
        "category":           row["visualization_type"],
        "business_category":  infer_business_category(row["title"], row["description"]),
        "created_at":         row["created_at"].isoformat() if row["created_at"] else None,
    }


# ─── Generic stream worker ────────────────────────────────────────────────────

def stream_worker(stream_name: str, queue_name: str, fetch_fn, convert_fn):
    logger.info(f"[{stream_name}] 🚀 Started → queue: {queue_name}")

    # DB connection
    db_conn = None
    for attempt in range(10):
        try:
            db_conn = get_db()
            break
        except Exception as e:
            logger.warning(f"[{stream_name}] DB not ready ({attempt+1}/10): {e}")
            time.sleep(3)
    else:
        logger.critical(f"[{stream_name}] ❌ Cannot connect to DB. Exiting thread.")
        return

    mq_conn, channel = make_rabbit_channel(queue_name)
    last_id = load_cursor(db_conn, stream_name)
    total   = 0

    logger.info(f"[{stream_name}] ▶️  Resuming from id > {last_id}")

    try:
        while True:
            try:
                rows = fetch_fn(db_conn, last_id)
            except Exception as e:
                logger.error(f"[{stream_name}] ❌ Fetch error: {e}")
                time.sleep(POLL_INTERVAL)
                continue

            for row in rows:
                try:
                    event = convert_fn(row)
                    publish(channel, queue_name, event)
                    total  += 1
                    last_id = max(last_id, row["id"])
                    logger.debug(f"[{stream_name}] 📤 id={row['id']}")
                except Exception as e:
                    logger.error(f"[{stream_name}] ❌ Error on row {row.get('id')}: {e}")

            if rows:
                save_cursor(db_conn, stream_name, last_id)
                logger.info(f"[{stream_name}] 📤 {len(rows)} events (total: {total})")

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        pass
    finally:
        mq_conn.close()
        db_conn.close()
        logger.info(f"[{stream_name}] ⏹️  Stopped. Total: {total}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def run():
    logger.info("🚀 Publisher starting — 3 parallel streams")

    streams = [
        ("recent_views", "navigation_logs", fetch_recent_views, view_to_event),
        ("core_user",    "users_sync",      fetch_core_users,   user_to_event),
        ("report_card",  "reports_sync",    fetch_report_cards, card_to_event),
    ]

    threads = []
    for args in streams:
        t = threading.Thread(target=stream_worker, args=args, name=args[0], daemon=True)
        t.start()
        threads.append(t)
        logger.info(f"✅ Thread started: {args[0]}")

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        logger.info("⏹️  Publisher shutting down...")


if __name__ == "__main__":
    run()
