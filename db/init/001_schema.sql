-- ═══════════════════════════════════════════════
-- PROMETHEUS UNBOUND — Schema
-- Runs automatically when TimescaleDB starts
-- ═══════════════════════════════════════════════

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ── Main metrics table ────────────────────────
CREATE TABLE IF NOT EXISTS metrics (
    time         TIMESTAMPTZ      NOT NULL,
    tenant_id    TEXT             NOT NULL,
    cpu          DOUBLE PRECISION,
    latency      DOUBLE PRECISION,
    error_rate   DOUBLE PRECISION
);

-- Convert to hypertable
-- This is the core TimescaleDB feature
-- It automatically partitions data by time chunks
SELECT create_hypertable('metrics', 'time', if_not_exists => TRUE);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_metrics_time
    ON metrics (time DESC);

CREATE INDEX IF NOT EXISTS idx_metrics_tenant
    ON metrics (tenant_id, time DESC);

-- ── Anomalies table ───────────────────────────
CREATE TABLE IF NOT EXISTS anomalies (
    time         TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    tenant_id    TEXT             NOT NULL,
    metric       TEXT             NOT NULL,
    value        DOUBLE PRECISION,
    zscore       DOUBLE PRECISION,
    threshold    DOUBLE PRECISION
);

SELECT create_hypertable('anomalies', 'time', if_not_exists => TRUE);

-- ── Incidents table ───────────────────────────
CREATE TABLE IF NOT EXISTS incidents (
    time         TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    tenant_id    TEXT,
    issue        TEXT,
    root_cause   TEXT,
    action_taken TEXT,
    status       TEXT             DEFAULT 'open',
    resolved_at  TIMESTAMPTZ
);

SELECT create_hypertable('incidents', 'time', if_not_exists => TRUE);

-- ── AI logs table ─────────────────────────────
CREATE TABLE IF NOT EXISTS ai_logs (
    time         TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    tenant_id    TEXT,
    context      TEXT,
    suggestion   TEXT,
    confidence   DOUBLE PRECISION,
    applied      BOOLEAN          DEFAULT FALSE
);

SELECT create_hypertable('ai_logs', 'time', if_not_exists => TRUE);
