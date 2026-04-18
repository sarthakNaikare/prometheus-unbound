import os
import time
import psycopg2
import statistics
from datetime import datetime, timezone

DB_URL = os.getenv("DB_URL", "postgres://tsadmin:tspassword@localhost:5432/prometheusdb")
THRESHOLD = float(os.getenv("ANOMALY_ZSCORE_THRESHOLD", "3.0"))
INTERVAL = float(os.getenv("HEALTH_CHECK_INTERVAL_SECONDS", "30"))

def get_db_connection():
    while True:
        try:
            conn = psycopg2.connect(DB_URL)
            print("Connected to TimescaleDB")
            return conn
        except Exception as e:
            print(f"DB connection failed: {e} retrying in 5s")
            time.sleep(5)

def get_recent_metrics(cur, tenant_id, metric_name, window_minutes=5):
    query = f"SELECT {metric_name} FROM metrics WHERE tenant_id = %s AND time > NOW() - INTERVAL %s ORDER BY time DESC"
    cur.execute(query, (tenant_id, f"{window_minutes} minutes"))
    rows = cur.fetchall()
    return [row[0] for row in rows if row[0] is not None]

def compute_zscore(values):
    if len(values) < 10:
        return None
    mean = statistics.mean(values)
    stdev = statistics.stdev(values)
    if stdev == 0:
        return None
    return (values[0] - mean) / stdev

def log_anomaly(cur, conn, tenant_id, metric, value, zscore):
    cur.execute("INSERT INTO anomalies (time, tenant_id, metric, value, zscore, threshold) VALUES (%s, %s, %s, %s, %s, %s)", (datetime.now(timezone.utc), tenant_id, metric, value, zscore, THRESHOLD))
    conn.commit()

def check_tenant(cur, conn, tenant_id):
    for metric in ["cpu", "latency", "error_rate"]:
        values = get_recent_metrics(cur, tenant_id, metric)
        if not values:
            continue
        zscore = compute_zscore(values)
        if zscore is None:
            continue
        if abs(zscore) > THRESHOLD:
            print(f"ANOMALY DETECTED")
            print(f"  Tenant : {tenant_id}")
            print(f"  Metric : {metric}")
            print(f"  Value  : {values[0]}")
            print(f"  Zscore : {zscore:.2f}")
            print("-" * 40)
            log_anomaly(cur, conn, tenant_id, metric, values[0], zscore)

def main():
    print("Starting anomaly detector")
    print(f"Threshold : {THRESHOLD}")
    print(f"Interval  : {INTERVAL}s")
    print("-" * 40)
    conn = get_db_connection()
    cur = conn.cursor()
    tenants = os.getenv("TENANTS", "tenant_alpha,tenant_beta,tenant_gamma").split(",")
    while True:
        print(f"[{datetime.now()}] Checking {len(tenants)} tenants...")
        for tenant in tenants:
            try:
                check_tenant(cur, conn, tenant)
            except Exception as e:
                print(f"Error checking {tenant}: {e}")
                conn = get_db_connection()
                cur = conn.cursor()
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
