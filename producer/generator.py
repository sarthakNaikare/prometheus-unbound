import os
import json
import time
import random
from datetime import datetime, timezone
from kafka import KafkaProducer

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
KAFKA_TOPIC     = os.getenv("KAFKA_TOPIC", "metrics")
TENANTS         = os.getenv("TENANTS", "tenant_alpha,tenant_beta,tenant_gamma").split(",")
INTERVAL        = float(os.getenv("INGESTION_INTERVAL_SECONDS", "1"))

PROFILES = {
    "tenant_alpha": {"cpu_base": 40, "latency_base": 100, "error_base": 0.5},
    "tenant_beta":  {"cpu_base": 60, "latency_base": 200, "error_base": 1.0},
    "tenant_gamma": {"cpu_base": 30, "latency_base": 80,  "error_base": 0.2},
}

def generate_metric(tenant_id):
    profile = PROFILES.get(tenant_id, PROFILES["tenant_alpha"])
    spike = random.random() < 0.05

    cpu = profile["cpu_base"] + random.uniform(-10, 10)
    if spike:
        cpu += random.uniform(30, 50)

    latency = profile["latency_base"] + random.uniform(-20, 20)
    if spike:
        latency += random.uniform(200, 500)

    error_rate = profile["error_base"] + random.uniform(-0.1, 0.1)
    if spike:
        error_rate += random.uniform(2, 5)

    return {
        "time":       datetime.now(timezone.utc).isoformat(),
        "tenant_id":  tenant_id,
        "cpu":        round(max(0, min(100, cpu)), 2),
        "latency":    round(max(0, latency), 2),
        "error_rate": round(max(0, error_rate), 2),
    }

def main():
    print("Starting metric generator")
    print(f"Kafka  : {KAFKA_BOOTSTRAP}")
    print(f"Topic  : {KAFKA_TOPIC}")
    print(f"Tenants: {TENANTS}")
    print("-" * 40)

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        retries=5
    )

    while True:
        for tenant in TENANTS:
            metric = generate_metric(tenant)
            producer.send(KAFKA_TOPIC, value=metric)
            print(f"[{metric['time']}] {tenant} | cpu={metric['cpu']}% latency={metric['latency']}ms error={metric['error_rate']}")

        producer.flush()
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
