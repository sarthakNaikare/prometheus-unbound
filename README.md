cat > /tmp/write_readme.py << 'PYEOF'
lines = [
    "# Prometheus Unbound\n",
    "\n",
    "> A self-healing AI metrics platform powered by TimescaleDB + Ghostgres\n",
    "\n",
    "## What this is\n",
    "\n",
    "Prometheus Unbound detects anomalies in real-time metrics,\n",
    "reasons over them using Ghostgres (TimescaleDB's AI layer),\n",
    "and automatically takes corrective action — all without human intervention.\n",
    "\n",
    "## The trio\n",
    "\n",
    "This is the third in a series of production-grade TimescaleDB projects:\n",
    "\n",
    "1. Stellar Observatory — ingestion pipeline + NASA SDSS dataset + Grafana\n",
    "2. Resonance — 5 live data streams + anomaly detection + React Three Fiber\n",
    "3. Prometheus Unbound — self-healing AI platform + Ghostgres reasoning engine\n",
    "\n",
    "Each project builds on the last. This one answers the question:\n",
    "what happens AFTER you detect an anomaly? Who decides what to do?\n",
    "\n",
    "## Architecture\n",
    "\n",
    "Generator -> Kafka -> Consumer -> TimescaleDB\n",
    "                                      |\n",
    "                              Anomaly Engine (z-score)\n",
    "                                      |\n",
    "                          Ghostgres AI (root cause)\n",
    "                                      |\n",
    "                            Decision Engine (action)\n",
    "                                      |\n",
    "                         TimescaleDB (incident log)\n",
    "                                      |\n",
    "                                   Grafana\n",
    "\n",
    "## TimescaleDB features used\n",
    "\n",
    "| Feature | Purpose | Why not plain Postgres |\n",
    "|---|---|---|\n",
    "| Hypertable | Time partitioning | Automatic chunk management |\n",
    "| Continuous aggregates | 1min + 1hour rollups | Live refresh without re-scanning |\n",
    "| time_bucket() | Dashboard queries | Native time binning |\n",
    "| Compression policy | Compress after 7 days | 90% storage reduction |\n",
    "| Retention policy | Drop after 30 days | Automatic cleanup |\n",
    "| Ghostgres | AI root cause analysis | Claude via psql protocol |\n",
    "\n",
    "## Ghostgres integration\n",
    "\n",
    "Ghostgres is TimescaleDB's new AI reasoning layer.\n",
    "It exposes a psql-compatible endpoint where Claude is the query engine.\n",
    "\n",
    "When an anomaly is detected, the system connects to Ghostgres and asks:\n",
    "what caused this, what should we do, how confident are you?\n",
    "\n",
    "The response is structured JSON stored in TimescaleDB for full auditability.\n",
    "\n",
    "Requires Anthropic API credits to activate. Falls back to mock mode automatically.\n",
    "\n",
    "## Quick start\n",
    "\n",
    "git clone https://github.com/sarthak8055/prometheus-unbound\n",
    "cd prometheus-unbound\n",
    "cp .env.example .env\n",
    "docker-compose up -d\n",
    "source venv/bin/activate\n",
    "pip install -r producer/requirements.txt\n",
    "python3 producer/generator.py\n",
    "\n",
    "## Services\n",
    "\n",
    "- Grafana: http://localhost:3000\n",
    "- FastAPI: http://localhost:8000/docs\n",
    "- TimescaleDB: localhost:5432\n",
    "- Kafka: localhost:9092\n",
    "\n",
    "## Screenshots\n",
    "\n",
    "See docs/screenshots/ for full system screenshots.\n",
    "\n",
    "## Built by\n",
    "\n",
    "Sarthak — backend engineer passionate about time-series data,\n",
    "distributed systems, and AI-assisted observability.\n",
    "\n",
    "Applying for: Database Support Engineer - Weekend (India) at Tiger Data\n",
]

with open("README.md", "w") as f:
    f.writelines(lines)
print("Done")
PYEOF
# Prometheus Unbound

> A self-healing AI metrics platform powered by TimescaleDB + Ghostgres

## What this is

Prometheus Unbound detects anomalies in real-time metrics,
reasons over them using Ghostgres (TimescaleDB's AI layer),
and automatically takes corrective action without human intervention.

## The trio

This is the third in a series of production-grade TimescaleDB projects:

1. Stellar Observatory — ingestion pipeline + NASA SDSS dataset + Grafana
2. Resonance — 5 live data streams + anomaly detection + React Three Fiber
3. Prometheus Unbound — self-healing AI platform + Ghostgres reasoning engine

## Architecture

Generator -> Kafka -> Consumer -> TimescaleDB
                                      |
                              Anomaly Engine (z-score)
                                      |
                          Ghostgres AI (root cause)
                                      |
                            Decision Engine (action)
                                      |
                         TimescaleDB (incident log)
                                      |
                                   Grafana

## TimescaleDB features used

- Hypertable: automatic time partitioning
- Continuous aggregates: live 1min and 1hour rollups
- Compression policy: compress after 7 days
- Retention policy: drop after 30 days
- Ghostgres: AI root cause analysis via psql protocol

## Quick start

git clone https://github.com/sarthak8055/prometheus-unbound
cd prometheus-unbound
cp .env.example .env
docker-compose up -d
source venv/bin/activate
pip install -r producer/requirements.txt
python3 producer/generator.py

## Services

- Grafana: http://localhost:3000
- FastAPI: http://localhost:8000/docs
- TimescaleDB: localhost:5432
- Kafka: localhost:9092
