# Prometheus Unbound

> A self-healing AI metrics platform powered by TimescaleDB + Ghostgres

## What this is

Prometheus Unbound detects anomalies in real-time metrics, reasons over them using Ghostgres (TimescaleDB's AI layer), and automatically takes corrective action without human intervention.

## The Trio

This is the third in a series of production-grade TimescaleDB projects:

- **Stellar Observatory** — ingestion pipeline + NASA SDSS dataset + Grafana
- **Resonance** — 5 live data streams + anomaly detection + React Three Fiber  
- **Prometheus Unbound** — self-healing AI platform + Ghostgres reasoning engine

Each project builds on the last. This one answers: what happens AFTER you detect an anomaly?

## Architecture
Generator -> Kafka -> Consumer -> TimescaleDB
|
Anomaly Engine (z-score)
|
Ghostgres AI (root cause)
|
Decision Engine (action)
|
Grafana
## TimescaleDB Features Used

| Feature | Purpose |
|---|---|
| Hypertable | Automatic time partitioning |
| Continuous aggregates | Live 1min and 1hour rollups |
| Compression policy | 90% storage reduction after 7 days |
| Retention policy | Auto cleanup after 30 days |
| Ghostgres | AI root cause analysis via psql |

## Quick Start

```bash
git clone https://github.com/sarthak8055/prometheus-unbound
cd prometheus-unbound
cp .env.example .env
docker-compose up -d
source venv/bin/activate
pip install -r producer/requirements.txt
python3 producer/generator.py
```

## Services

- Grafana: http://localhost:3000
- FastAPI: http://localhost:8000/docs
- TimescaleDB: localhost:5432
- Kafka: localhost:9092
