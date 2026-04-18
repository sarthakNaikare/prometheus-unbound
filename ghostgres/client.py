import os
import psycopg2
import json
import random
from datetime import datetime, timezone

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MOCK_MODE = not bool(ANTHROPIC_API_KEY)

def mock_response(tenant_id, metric, value, zscore):
    severity = "low"
    if abs(zscore) > 4:
        severity = "critical"
    elif abs(zscore) > 3.5:
        severity = "high"
    elif abs(zscore) > 3:
        severity = "medium"
    causes = {
        "cpu": "CPU spike likely caused by burst of requests or runaway process.",
        "latency": "Latency spike likely caused by connection pool exhaustion.",
        "error_rate": "Error spike likely caused by downstream service failure.",
    }
    actions = {
        "cpu": "Reduce ingestion rate and check for runaway queries.",
        "latency": "Check TimescaleDB connection pool and query plans.",
        "error_rate": "Check consumer logs and downstream dependencies.",
    }
    investigate = {
        "cpu": "Check pg_stat_activity for long running queries.",
        "latency": "Run EXPLAIN ANALYZE on recent slow queries.",
        "error_rate": "Check Kafka consumer lag and DLQ.",
    }
    return {
        "root_cause": causes.get(metric, "Unknown anomaly."),
        "recommended_action": actions.get(metric, "Monitor manually."),
        "investigate_next": investigate.get(metric, "Check system logs."),
        "severity": severity,
        "confidence": round(random.uniform(0.75, 0.95), 2),
        "mode": "mock",
    }

def ask_ghostgres(tenant_id, metric, value, zscore, recent_values):
    if MOCK_MODE:
        print("  [Ghostgres] Running in mock mode")
        return mock_response(tenant_id, metric, value, zscore)
    try:
        url = f"postgres://anthropic:{ANTHROPIC_API_KEY}@try.ghostgres.com/claude-sonnet-4-6"
        conn = psycopg2.connect(url)
        conn.autocommit = True
        cur = conn.cursor()
        prompt = f"Analyze this anomaly. Tenant:{tenant_id} Metric:{metric} Value:{value} Zscore:{zscore:.2f} Recent:{recent_values}. Respond in JSON with keys: root_cause, recommended_action, investigate_next, severity, confidence"
        cur.execute("SELECT %s::text", (prompt,))
        result = cur.fetchone()[0]
        cur.close()
        conn.close()
        parsed = json.loads(result)
        parsed["mode"] = "ghostgres"
        return parsed
    except Exception as e:
        print(f"  [Ghostgres] Error: {e} falling back to mock")
        return mock_response(tenant_id, metric, value, zscore)

def test_connection():
    if MOCK_MODE:
        print("No API key - running in mock mode")
        result = mock_response("tenant_beta", "cpu", 95.2, 4.7)
        print(json.dumps(result, indent=2))
        return
    print("Testing Ghostgres connection...")
    try:
        url = f"postgres://anthropic:{ANTHROPIC_API_KEY}@try.ghostgres.com/claude-sonnet-4-6"
        conn = psycopg2.connect(url)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT %s::text", ("Say hello in one sentence.",))
        result = cur.fetchone()[0]
        print(f"Response: {result}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    import sys
    if "--test" in sys.argv:
        test_connection()
