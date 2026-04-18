import os
import psycopg2
import psycopg2.extras
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import time

DB_URL = os.getenv("DB_URL", "postgres://tsadmin:tspassword@localhost:5432/prometheusdb")

app = FastAPI(
    title="Prometheus Unbound",
    description="Self-healing AI metrics platform powered by TimescaleDB + Ghostgres",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_conn():
    return psycopg2.connect(DB_URL)

@app.get("/")
def root():
    return {
        "name": "Prometheus Unbound",
        "status": "running",
        "time": datetime.now(timezone.utc).isoformat()
    }

@app.get("/health")
def health():
    try:
        conn = get_conn()
        cur  = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM metrics")
        count = cur.fetchone()[0]
        conn.close()
        return {"status": "healthy", "total_metrics": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/{tenant_id}")
def get_metrics(tenant_id: str, limit: int = 100):
    try:
        conn = get_conn()
        cur  = psycopg2.extras.RealDictCursor(conn)
        cur.execute("""
            SELECT time, tenant_id, cpu, latency, error_rate
            FROM metrics
            WHERE tenant_id = %s
            ORDER BY time DESC
            LIMIT %s
        """, (tenant_id, limit))
        rows = cur.fetchall()
        conn.close()
        return {"tenant_id": tenant_id, "count": len(rows), "data": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/anomalies")
def get_anomalies(limit: int = 50):
    try:
        conn = get_conn()
        cur  = psycopg2.extras.RealDictCursor(conn)
        cur.execute("""
            SELECT time, tenant_id, metric, value, zscore, threshold
            FROM anomalies
            ORDER BY time DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        conn.close()
        return {"count": len(rows), "data": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/incidents")
def get_incidents(limit: int = 50):
    try:
        conn = get_conn()
        cur  = psycopg2.extras.RealDictCursor(conn)
        cur.execute("""
            SELECT time, tenant_id, issue, root_cause, action_taken, status
            FROM incidents
            ORDER BY time DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        conn.close()
        return {"count": len(rows), "data": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai-logs")
def get_ai_logs(limit: int = 50):
    try:
        conn = get_conn()
        cur  = psycopg2.extras.RealDictCursor(conn)
        cur.execute("""
            SELECT time, tenant_id, context, suggestion, confidence, applied
            FROM ai_logs
            ORDER BY time DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        conn.close()
        return {"count": len(rows), "data": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health-score/{tenant_id}")
def get_health_score(tenant_id: str):
    try:
        conn = get_conn()
        cur  = conn.cursor()

        cur.execute("""
            SELECT COUNT(*)
            FROM anomalies
            WHERE tenant_id = %s
              AND time > NOW() - INTERVAL '1 hour'
        """, (tenant_id,))
        anomaly_count = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*)
            FROM incidents
            WHERE tenant_id = %s
              AND time > NOW() - INTERVAL '1 hour'
              AND status = 'open'
        """, (tenant_id,))
        open_incidents = cur.fetchone()[0]

        score = 100
        score -= anomaly_count * 5
        score -= open_incidents * 10
        score = max(0, score)

        conn.close()
        return {
            "tenant_id": tenant_id,
            "health_score": score,
            "anomalies_last_hour": anomaly_count,
            "open_incidents": open_incidents,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
