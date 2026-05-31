#!/usr/bin/env python3

import json
import logging
import os
import threading
import time

import psycopg2
import psycopg2.extras
import pika

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("consumer")

# ─── Config ─────────────────────────────────────────────────────────

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")

DB_HOST     = os.getenv("DB_HOST", "postgres")
DB_PORT     = int(os.getenv("DB_PORT", "5432"))
DB_USER     = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin123")
DB_NAME     = os.getenv("DB_NAME", "bi_recommendation")

# ─── DB ─────────────────────────────────────────────────────────────

def get_db():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME,
        cursor_factory=psycopg2.extras.RealDictCursor,
    )

# ─── Handlers ───────────────────────────────────────────────────────

def handle_navigation_log(event: dict, conn):
    with conn.cursor() as cur:

        user_id_mb = event.get("metabase_user_id")
        report_id_mb = event.get("metabase_report_id")

        if not user_id_mb or not report_id_mb:
            logger.error(f"❌ Invalid event: {event}")
            return

        # Resolve user
        cur.execute("SELECT id FROM users WHERE metabase_user_id = %s", (user_id_mb,))
        user_row = cur.fetchone()

        if not user_row:
            cur.execute("""
                INSERT INTO users (metabase_user_id, email, name, role)
                VALUES (%s, %s, %s, 'metabase_user')
                ON CONFLICT (metabase_user_id) DO UPDATE SET email = EXCLUDED.email
                RETURNING id
            """, (
                user_id_mb,
                event.get("user_email", f"user{user_id_mb}@auto.local"),
                event.get("user_name", "")
            ))
            user_row = cur.fetchone()

        # Resolve report
        cur.execute("SELECT id FROM reports WHERE metabase_report_id = %s", (report_id_mb,))
        report_row = cur.fetchone()

        if not report_row:
            title = f"{event.get('model','card').capitalize()} {report_id_mb}"

            cur.execute("""
                INSERT INTO reports (metabase_report_id, title, category)
                VALUES (%s, %s, %s)
                ON CONFLICT (metabase_report_id) DO NOTHING
                RETURNING id
            """, (report_id_mb, title, event.get("model", "card")))

            report_row = cur.fetchone()

            if not report_row:
                cur.execute("SELECT id FROM reports WHERE metabase_report_id = %s", (report_id_mb,))
                report_row = cur.fetchone()

        # Insert log
        cur.execute("""
            INSERT INTO navigation_logs (
                source_event_id,
                user_id,
                report_id,
                action,
                event_type,
                duration,
                duration_source,
                metabase_model,
                metabase_model_id,
                raw_payload,
                timestamp
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (
            event.get("source_event_id"),
            user_row["id"],
            report_row["id"],
            event.get("action", "view"),
            event.get("event_type", event.get("action", "view")),
            event.get("duration", 0),
            event.get("duration_source", "unknown"),
            event.get("metabase_model", event.get("model")),
            event.get("metabase_model_id", event.get("metabase_report_id")),
            psycopg2.extras.Json(event),
            event.get("timestamp"),
        ))

    conn.commit()


def handle_user_sync(event: dict, conn):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO users (metabase_user_id, email, name, role, updated_at)
            VALUES (%s, %s, %s, %s, NOW())
            ON CONFLICT (metabase_user_id) DO UPDATE SET
                email = EXCLUDED.email,
                name = EXCLUDED.name,
                role = EXCLUDED.role,
                updated_at = NOW()
        """, (
            event.get("metabase_user_id"),
            event.get("email"),
            event.get("name", ""),
            event.get("role", "user"),
        ))
    conn.commit()


def handle_report_sync(event: dict, conn):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO reports (metabase_report_id, title, description, category, business_category, updated_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
            ON CONFLICT (metabase_report_id) DO UPDATE SET
                title = EXCLUDED.title,
                description = EXCLUDED.description,
                category = EXCLUDED.category,
                business_category = EXCLUDED.business_category,
                updated_at = NOW()
        """, (
            event.get("metabase_report_id"),
            event.get("title", "unknown"),
            event.get("description"),
            event.get("category"),
            event.get("business_category"),
        ))
    conn.commit()

# ─── Worker ─────────────────────────────────────────────────────────

HANDLERS = {
    "navigation_logs": handle_navigation_log,
    "users_sync": handle_user_sync,
    "reports_sync": handle_report_sync,
}

def queue_worker(queue_name: str):
    logger.info(f"[{queue_name}] 🚀 started")

    # DB connect
    for _ in range(10):
        try:
            db_conn = get_db()
            break
        except:
            time.sleep(3)
    else:
        logger.error("❌ DB connection failed")
        return

    handler = HANDLERS[queue_name]

    creds = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    params = pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=creds)

    mq_conn = pika.BlockingConnection(params)
    channel = mq_conn.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_qos(prefetch_count=1)

    def ensure_db_connection():
        nonlocal db_conn
        if db_conn.closed:
            logger.warning(f"[{queue_name}] DB connection closed, reconnecting")
            db_conn = get_db()
        return db_conn

    def on_message(ch, method, properties, body):
        nonlocal db_conn
        try:
            # 🔥 FIX HERE
            event = json.loads(body)

            if isinstance(event, str):
                event = json.loads(event)

            handler(event, ensure_db_connection())

            logger.info(f"[{queue_name}] ✅ processed")
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            logger.error(f"[{queue_name}] ❌ {e}")
            try:
                if db_conn and not db_conn.closed:
                    db_conn.rollback()
            except Exception as rollback_error:
                logger.error(f"[{queue_name}] rollback failed: {rollback_error}")

            try:
                db_conn = get_db()
            except Exception as reconnect_error:
                logger.error(f"[{queue_name}] DB reconnect failed: {reconnect_error}")

            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    channel.basic_consume(queue=queue_name, on_message_callback=on_message)
    channel.start_consuming()

# ─── Main ───────────────────────────────────────────────────────────

def run():
    queues = ["navigation_logs", "users_sync", "reports_sync"]

    for q in queues:
        threading.Thread(target=queue_worker, args=(q,), daemon=True).start()

    while True:
        time.sleep(1)

if __name__ == "__main__":
    run()
