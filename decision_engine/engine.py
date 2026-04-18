import os
import time
import psycopg2
import json
from datetime import datetime, timezone
from ghostgres.client import ask_ghostgres

DB_URL   = os.getenv("DB_URL", "postgres://tsadmin:tspassword@localhost:5432/prometheusdb")
INTERVAL = float(os.getenv("HEALTH_CHECK_INTERVAL_SECONDS", "30"))

def get_db_connection():
    while True:
        try:
            conn = psycopg2.connect(DB_URL)
            print("Connected to TimescaleDB")
            return conn
        except Exception as e:
            print(f"DB connection failed: {e} — retrying in 5s")
            time.sleep(5)

def get_unhandled_anomalies(cur):
    cur.execute("""
        SELECT a.time, a.tenant_id, a.metric, a.value, a.zscore
        FROM anomalies a
        LEFT JOIN incidents i
          ON a.tenant_id = i.tenant_id
         AND a.time = i.time
        WHERE i.time IS NULL
        ORDER BY a.time DESC
        LIMIT 10
    """)
    return cur.fetchall()

def get_recent_values(cur, tenant_id, metric, limit=10):
    cur.execute(f"""
        SELECT {metric}
        FROM metrics
        WHERE tenant_id = %s
        ORDER BY time DESC
        LIMIT %s
    """, (tenant_id, limit))
    rows = cur.fetchall()
    return [row[0] for row in rows if row[0] is not None]

def log_incident(cur, conn, anomaly, suggestion):
    cur.execute("""
        INSERT INTO incidents
            (time, tenant_id, issue, root_cause, action_taken, status)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        anomaly["time"],
        anomaly["tenant_id"],
        f"{anomaly['metric']} anomaly — zscore {anomaly['zscore']:.2f}",
        suggestion.get("root_cause", "unknown"),
        suggestion.get("recommended_action", "none"),
        "open",
    ))

    cur.execute("""
        INSERT INTO ai_logs
            (time, tenant_id, context, suggestion, confidence, applied)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        datetime.now(timezone.utc),
        anomaly["tenant_id"],
        f"{anomaly['metric']}={anomaly['value']} zscore={anomaly['zscore']:.2f}",
        json.dumps(suggestion),
        suggestion.get("confidence", 0.0),
        True,
    ))
    conn.commit()

def take_action(suggestion):
    action = suggestion.get("recommended_action", "").lower()
    severity = suggestion.get("severity", "low")

    print(f"  Severity : {severity}")
    print(f"  Action   : {action}")
    print(f"  Next     : {suggestion.get('investigate_next', '')}")

    if severity == "critical":
        print("  AUTO-ACTION: Reducing ingestion rate")
    elif severity == "high":
        print("  AUTO-ACTION: Flagging tenant for review")
    else:
        print("  AUTO-ACTION: Logged for monitoring")

def main():
    print("Starting decision engine")
    print(f"Interval : {INTERVAL}s")
    print("-" * 40)

    conn = get_db_connection()
    cur  = conn.cursor()

    while True:
        try:
            anomalies = get_unhandled_anomalies(cur)

            if not anomalies:
                print(f"[{datetime.now()}] No new anomalies")
            else:
                print(f"[{datetime.now()}] Processing {len(anomalies)} anomalies")

            for row in anomalies:
                time_val, tenant_id, metric, value, zscore = row

                print(f"Analyzing: {tenant_id} | {metric}={value} zscore={zscore:.2f}")

                recent = get_recent_values(cur, tenant_id, metric)

                suggestion = ask_ghostgres(
                    tenant_id=tenant_id,
                    metric=metric,
                    value=value,
                    zscore=zscore,
                    recent_values=recent,
                )

                if suggestion:
                    print(f"  Root cause: {suggestion.get('root_cause')}")
                    take_action(suggestion)
                    log_incident(cur, conn, {
                        "time": time_val,
                        "tenant_id": tenant_id,
                        "metric": metric,
                        "value": value,
                        "zscore": zscore,
                    }, suggestion)
                else:
                    print("  Ghostgres unavailable — using fallback")
                    log_incident(cur, conn, {
                        "time": time_val,
                        "tenant_id": tenant_id,
                        "metric": metric,
                        "value": value,
                        "zscore": zscore,
                    }, {
                        "root_cause": "unknown — ghostgres unavailable",
                        "recommended_action": "manual review required",
                        "confidence": 0.0,
                        "severity": "low",
                    })

        except Exception as e:
            print(f"Error in decision engine: {e}")
            conn = get_db_connection()
            cur  = conn.cursor()

        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
