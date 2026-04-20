# 🔥 Prometheus Unbound

<div align="center">

> *When monitoring is not enough — the system heals itself.*

![TimescaleDB](https://img.shields.io/badge/TimescaleDB-FDB515?style=for-the-badge&logo=timescale&logoColor=black)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Kafka](https://img.shields.io/badge/Apache_Kafka-231F20?style=for-the-badge&logo=apache-kafka&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

**A production-grade, self-healing AI metrics platform built on TimescaleDB + Ghostgres**

</div>

---

## 🧠 What is this?

Prometheus Unbound detects anomalies in real-time metrics, reasons over them using **Ghostgres** (TimescaleDB's brand new AI layer), and automatically takes corrective action — all without human intervention.

When an anomaly fires, the system asks Claude:
- 🔍 What caused this?
- ⚡ What should we do right now?
- 🔎 What should we investigate next?

Then it **acts on the answer** and logs the entire incident lifecycle in TimescaleDB.

---

## 🗺️ The Trio — a progressive journey

| # | Project | Challenge | Stack |
|---|---|---|---|
| 1 | [⭐ Stellar Observatory](https://github.com/sarthakNaikare/stellar-observatory-timescaledb) | Ingest 100K+ NASA SDSS observations in real-time | TimescaleDB + Kafka + FastAPI + Grafana |
| 2 | [🎵 Resonance](https://github.com/sarthakNaikare/resonance) | 5 live streams + anomaly detection in 3D | TimescaleDB + React Three Fiber + CAggs |
| 3 | **🔥 Prometheus Unbound** | **Self-heal using AI reasoning** | **TimescaleDB + Ghostgres + Decision Engine** |

> Each project is a step up. This one is where TimescaleDB and AI meet.

---

## 🏗️ Architecture
┌─────────────────────────────────┐
│      🏭 Metric Generator        │
│  3 tenants · 1Hz · with spikes  │
└──────────────┬──────────────────┘
│
┌──────▼──────┐
│  📨 Kafka   │
└──────┬───────┘
│
┌──────▼────────┐
│  📥 Consumer  │
│  retry + DLQ  │
└──────┬─────────┘
│
┌──────────▼───────────┐
│  🐘 TimescaleDB      │
│  ✅ hypertables       │
│  ✅ continuous aggs   │
│  ✅ compression        │
│  ✅ retention          │
└──────────┬────────────┘
│
┌──────────▼───────────┐
│  🔬 Anomaly Engine   │
│  z-score · 30s poll  │
└──────────┬────────────┘
│
┌──────────▼───────────┐
│  👻 Ghostgres        │  ← TimescaleDB's NEW AI layer
│  Claude via psql     │    Claude IS the query engine
└──────────┬────────────┘
│
┌──────────▼───────────┐
│  ⚡ Decision Engine  │
│  root cause · act    │
└──────────┬────────────┘
│
┌────────────┼────────────┐
│            │            │
incidents   ai_logs   health score
│            │            │
└────────────┴──────┬─────┘
│
┌──────▼──────┐
│  📊 Grafana │
│  🚀 FastAPI │
└─────────────┘
---

## 🐘 TimescaleDB — the hero of this system

| Feature | Where used | Why not plain Postgres |
|---|---|---|
| 🗂️ **Hypertable** | metrics, anomalies, incidents, ai_logs | Automatic time partitioning. Recent queries never scan old chunks. |
| 📊 **Continuous aggregates** | metrics_1min, metrics_1hour | Live materialized views. Grafana hits pre-aggregated data. |
| ⏱️ **time_bucket()** | All dashboard queries | Native time binning. No workarounds. |
| 🗜️ **Compression policy** | metrics > 7 days | Up to 90% storage reduction. Fully automatic. |
| 🗑️ **Retention policy** | All tables | Auto-drop after 30 days. No cron jobs. |
| 👻 **Ghostgres** | Root cause engine | Claude AI via psql. The AI IS the database layer. |

---

## 👻 Ghostgres — what makes this different

Ghostgres is TimescaleDB's newest addition. A psql-compatible endpoint where Claude AI is the query engine.

```python
# Connect exactly like a normal Postgres database
conn = psycopg2.connect(
    "postgres://anthropic:KEY@try.ghostgres.com/claude-sonnet-4-6"
)

# Ask Claude via SQL
cur.execute("SELECT %s::text", (your_anomaly_context,))
response = cur.fetchone()[0]  # Structured JSON from Claude
```

**Example Ghostgres response:**
```json
{
  "root_cause": "CPU spike caused by burst of requests on tenant_beta",
  "recommended_action": "Reduce ingestion rate and check for runaway queries",
  "investigate_next": "Check pg_stat_activity for long running queries",
  "severity": "high",
  "confidence": 0.91
}
```

> 💡 Requires Anthropic API credits. Falls back to intelligent mock mode automatically.

---

## ⚡ Self-healing flow
📊 Generator produces metrics for 3 tenants every second
📥 Consumer inserts into TimescaleDB hypertable
🔬 Anomaly engine checks z-scores every 30 seconds
🚨 Z-score > 3.0 triggers Ghostgres reasoning
🧠 Decision engine reads AI suggestion and acts
📝 Incident logged with full audit trail
💯 Health score updated per tenant
📊 Grafana reflects everything in real time
---

## 🚀 Quick start

```bash
git clone https://github.com/sarthakNaikare/prometheus-unbound
cd prometheus-unbound
cp .env.example .env
docker-compose up -d
source venv/bin/activate
pip install -r producer/requirements.txt

# Terminal 1
python3 producer/generator.py

# Terminal 2
python3 consumer/consumer.py

# Terminal 3
python3 anomaly_engine/detector.py

# Terminal 4
PYTHONPATH=$(pwd) python3 decision_engine/engine.py
```

---

## 🧪 Chaos testing

```bash
# Spike CPU for tenant_beta
python3 chaos/simulator.py cpu tenant_beta

# Spike latency for tenant_alpha
python3 chaos/simulator.py latency tenant_alpha

# Random chaos
python3 chaos/simulator.py random
```

---

## 🌐 API endpoints

| Endpoint | Description |
|---|---|
| `GET /health` | System health + metrics count |
| `GET /metrics/{tenant_id}` | Recent metrics per tenant |
| `GET /anomalies` | All detected anomalies |
| `GET /incidents` | Incident log with AI root causes |
| `GET /ai-logs` | All Ghostgres AI suggestions |
| `GET /health-score/{tenant_id}` | Real-time health score |

> 📖 Interactive docs: `http://localhost:8000/docs`

---

## 📸 Screenshots

| Dashboard | Anomaly Detection | Decision Engine |
|---|---|---|
| ![dashboard](screenshots/23_grafana_dashboard_complete.png.png) | ![anomaly](screenshots/12_anomaly_detected.png.png) | ![decision](screenshots/16_decision_engine_mock_mode.png.png) |

---

## 👨‍💻 Built by Sarthak Naikare

Backend engineer passionate about time-series data, distributed systems, and AI-assisted observability.

🔗 Previous projects: [Stellar Observatory](https://github.com/sarthakNaikare/stellar-observatory-timescaledb) · [Resonance](https://github.com/sarthakNaikare/resonance)

💼 Interested in: **Database Support Engineer - Weekend (India)** at Tiger Data

## 🖥️ Live Dashboard

Prometheus Unbound includes a real-time React dashboard that polls the FastAPI every 5 seconds.

![Live Dashboard](screenshots/24_react_dashboard_live.png)

**Dashboard features:**
- 📊 Total metrics count from TimescaleDB
- 🚨 Live anomaly feed with z-scores
- 💯 Per-tenant health scores
- 📝 Incident log with AI root causes
- 👻 Ghostgres AI suggestions with confidence scores
- 🔴 Live CPU, latency and error rate bars per tenant

**To run the dashboard:**

```bash
cd dashboard
PORT=3000 npm start
```

Then open http://localhost:3000
