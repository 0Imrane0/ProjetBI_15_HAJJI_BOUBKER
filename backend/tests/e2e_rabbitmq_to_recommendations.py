#!/usr/bin/env python3
"""
Synthetic E2E check for Phase 6.

This simulates a Metabase navigation event by publishing one message to
RabbitMQ, waits for the consumer to persist it in PostgreSQL, then regenerates
stored recommendations through the API.
"""

import json
import os
import sys
import time
from datetime import datetime, timezone

import pika
import psycopg2
import requests


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "postgres"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD", "admin123"),
    "dbname": os.getenv("DB_NAME", "bi_recommendation"),
}
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")


def fail(message):
    print(f"[FAIL] {message}")
    sys.exit(1)


def fetch_seed_entities():
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, metabase_user_id FROM users ORDER BY id LIMIT 1")
            user = cur.fetchone()
            cur.execute("SELECT id, metabase_report_id FROM reports ORDER BY id LIMIT 1")
            report = cur.fetchone()
            cur.execute("SELECT COALESCE(MAX(source_event_id), 0) + 1 FROM navigation_logs")
            source_event_id = cur.fetchone()[0]
    if not user or not report:
        fail("Need at least one user and one report for E2E check")
    return user, report, int(source_event_id)


def publish_navigation_event(payload):
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    params = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials,
    )
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue="navigation_logs", durable=True)
    channel.basic_publish(
        exchange="",
        routing_key="navigation_logs",
        body=json.dumps(payload),
        properties=pika.BasicProperties(delivery_mode=2),
    )
    connection.close()


def wait_for_event(source_event_id, timeout_seconds=30):
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) FROM navigation_logs WHERE source_event_id = %s",
                    (source_event_id,),
                )
                count = cur.fetchone()[0]
        if count == 1:
            return True
        time.sleep(1)
    return False


def post_json(path):
    response = requests.post(f"{API_BASE_URL}{path}", timeout=120)
    if response.status_code >= 400:
        fail(f"POST {path} returned {response.status_code}: {response.text}")
    return response.json()


def get_json(path):
    response = requests.get(f"{API_BASE_URL}{path}", timeout=30)
    if response.status_code >= 400:
        fail(f"GET {path} returned {response.status_code}: {response.text}")
    return response.json()


def main():
    user, report, source_event_id = fetch_seed_entities()
    internal_user_id, metabase_user_id = user
    _, metabase_report_id = report

    payload = {
        "source_event_id": source_event_id,
        "metabase_user_id": metabase_user_id,
        "metabase_report_id": metabase_report_id,
        "action": "selection",
        "event_type": "synthetic_e2e_selection",
        "duration": 240,
        "duration_source": "synthetic_e2e",
        "metabase_model": "card",
        "metabase_model_id": metabase_report_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    publish_navigation_event(payload)
    if not wait_for_event(source_event_id):
        fail("Consumer did not persist the synthetic RabbitMQ event in time")

    batch = post_json("/batch/recommendations/generate?n=5")
    stored = get_json(f"/stored-recommendations/{internal_user_id}?n=5")
    if stored["count"] != 5:
        fail("Expected 5 stored recommendations after E2E batch generation")

    print("[PASS] Synthetic E2E RabbitMQ -> PostgreSQL -> API -> Reco passed")
    print(
        {
            "source_event_id": source_event_id,
            "batch_id": batch["batch_id"],
            "user_id": internal_user_id,
            "stored_count": stored["count"],
        }
    )


if __name__ == "__main__":
    main()
