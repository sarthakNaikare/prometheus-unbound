import os
import time
import random
import psycopg2
from datetime import datetime, timezone

DB_URL = os.getenv("DB_URL", "postgres://tsadmin:tspassword@localhost:5432/prometheusdb")

def get_conn():
    return psycopg2.connect(DB_URL)

def spike_cpu(tenant_id, duration=60):
    """
    Inserts artificially high CPU values
    to trigger the anomaly detector
    """
    print(f"CHAOS: Spiking CPU for {tenant_id} for {duration}s")
    conn = get_conn()
    cur  = conn.cursor()

    end = time.time() + duration
    while time.time() < end:
        cur.execute("""
            INSERT INTO metrics (time, tenant_id, cpu, latency, error_rate)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            datetime.now(timezone.utc),
            tenant_id,
            random.uniform(90, 100),
            random.uniform(10, 50),
            random.uniform(0, 1),
        ))
        conn.commit()
        print(f"  Inserted high CPU for {tenant_id}")
        time.sleep(1)

    conn.close()
    print(f"CHAOS: CPU spike ended for {tenant_id}")

def spike_latency(tenant_id, duration=60):
    """
    Inserts artificially high latency values
    to trigger the anomaly detector
    """
    print(f"CHAOS: Spiking latency for {tenant_id} for {duration}s")
    conn = get_conn()
    cur  = conn.cursor()

    end = time.time() + duration
    while time.time() < end:
        cur.execute("""
            INSERT INTO metrics (time, tenant_id, cpu, latency, error_rate)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            datetime.now(timezone.utc),
            tenant_id,
            random.uniform(10, 50),
            random.uniform(800, 2000),
            random.uniform(0, 1),
        ))
        conn.commit()
        print(f"  Inserted high latency for {tenant_id}")
        time.sleep(1)

    conn.close()
    print(f"CHAOS: Latency spike ended for {tenant_id}")

def spike_errors(tenant_id, duration=60):
    """
    Inserts artificially high error rates
    to trigger the anomaly detector
    """
    print(f"CHAOS: Spiking error rate for {tenant_id} for {duration}s")
    conn = get_conn()
    cur  = conn.cursor()

    end = time.time() + duration
    while time.time() < end:
        cur.execute("""
            INSERT INTO metrics (time, tenant_id, cpu, latency, error_rate)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            datetime.now(timezone.utc),
            tenant_id,
            random.uniform(10, 50),
            random.uniform(10, 50),
            random.uniform(8, 15),
        ))
        conn.commit()
        print(f"  Inserted high error rate for {tenant_id}")
        time.sleep(1)

    conn.close()
    print(f"CHAOS: Error spike ended for {tenant_id}")

def random_chaos(duration=120):
    """
    Randomly picks a tenant and metric
    and spikes it — simulates real world chaos
    """
    tenants = os.getenv(
        "TENANTS",
        "tenant_alpha,tenant_beta,tenant_gamma"
    ).split(",")

    tenant = random.choice(tenants)
    chaos  = random.choice([spike_cpu, spike_latency, spike_errors])

    print(f"CHAOS: Random chaos starting")
    print(f"  Tenant : {tenant}")
    print(f"  Type   : {chaos.__name__}")
    print("-" * 40)

    chaos(tenant, duration)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 simulator.py random")
        print("  python3 simulator.py cpu tenant_alpha")
        print("  python3 simulator.py latency tenant_beta")
        print("  python3 simulator.py errors tenant_gamma")
    elif sys.argv[1] == "random":
        random_chaos()
    elif sys.argv[1] == "cpu":
        spike_cpu(sys.argv[2])
    elif sys.argv[1] == "latency":
        spike_latency(sys.argv[2])
    elif sys.argv[1] == "errors":
        spike_errors(sys.argv[2])
