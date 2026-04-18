-- ═══════════════════════════════════════════════
-- PROMETHEUS UNBOUND — Policies
-- Compression + Retention
-- These run automatically in the background
-- ═══════════════════════════════════════════════

-- ── Compression policy ────────────────────────
-- Compresses chunks of metrics older than 7 days
-- Reduces storage by up to 90 percent
-- Only TimescaleDB can do this automatically

ALTER TABLE metrics SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'tenant_id'
);

SELECT add_compression_policy('metrics',
    compress_after => INTERVAL '7 days',
    if_not_exists  => TRUE
);

-- ── Retention policy ──────────────────────────
-- Automatically drops data older than 30 days
-- No cron jobs needed
-- Keeps your database lean and credits safe

SELECT add_retention_policy('metrics',
    drop_after    => INTERVAL '30 days',
    if_not_exists => TRUE
);

SELECT add_retention_policy('anomalies',
    drop_after    => INTERVAL '30 days',
    if_not_exists => TRUE
);

SELECT add_retention_policy('incidents',
    drop_after    => INTERVAL '90 days',
    if_not_exists => TRUE
);

SELECT add_retention_policy('ai_logs',
    drop_after    => INTERVAL '90 days',
    if_not_exists => TRUE
);
