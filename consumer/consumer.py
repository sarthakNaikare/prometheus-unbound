import os
import json
import time
import psycopg2
import psycopg2.extras
from kafka import KafkaConsumer
from datetime import datetime

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
KAFKA_TOPIC     = os.getenv("KAFKA_TOPIC", "metrics")
KAFKA_GROUP_ID  = os.getenv("KAFKA_GROUP_ID", "prometheus-consumer")
DB_URL          = os.getenv("DB_URL", "postgres://tsadmin:tspassword@localhost:5432/prometheusdb")

def get_db_connection():
    while True:
        try:
            conn = psycopg2.connect(DB_URL)
            print("Connected to TimescaleDB")
            return conn
        except Exception as e:
            print(f"DB connection failed: {e} — retrying in 5s")
            time.sleep(5)

def insert_metric(cur, metric):
    cur.execute("""
        INSERT INTO metrics (time, tenant_id, cpu, latency, error_rate)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        metric["time"],
        metric["tenant_id"],
        metric["cpu"],
        metric["latency"],
        metric["error_rate"],
    ))

def main():
    print("Starting Kafka consumer")
    print(f"Kafka  : {KAFKA_BOOTSTRAP}")
    print(f"Topic  : {KAFKA_TOPIC}")
    print(f"Group  : {KAFKA_GROUP_ID}")
    print("-" * 40)

    conn = get_db_connection()
    cur  = conn.cursor()

    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id=KAFKA_GROUP_ID,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
    )

    print("Listening for messages...")

    for message in consumer:
        try:
            metric = message.value
            insert_metric(cur, metric)
            conn.commit()
            print(f"Inserted: {metric['tenant_id']} | cpu={metric['cpu']}% latency={metric['latency']}ms")

        except Exception as e:
            print(f"Error inserting metric: {e}")
            conn.rollback()
            conn = get_db_connection()
            cur  = conn.cursor()

if __name__ == "__main__":
    main()
