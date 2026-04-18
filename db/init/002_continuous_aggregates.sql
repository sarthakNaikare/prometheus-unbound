-- Continuous Aggregates

CREATE MATERIALIZED VIEW IF NOT EXISTS metrics_1min
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 minute', time)  AS bucket,
    tenant_id,
    AVG(cpu)                        AS avg_cpu,
    MAX(cpu)                        AS max_cpu,
    MIN(cpu)                        AS min_cpu,
    AVG(latency)                    AS avg_latency,
    MAX(latency)                    AS max_latency,
    MIN(latency)                    AS min_latency,
    AVG(error_rate)                 AS avg_error_rate,
    COUNT(*)                        AS sample_count
FROM metrics
GROUP BY bucket, tenant_id
WITH NO DATA;

SELECT add_continuous_aggregate_policy('metrics_1min',
    start_offset      => INTERVAL '10 minutes',
    end_offset        => INTERVAL '1 minute',
    schedule_interval => INTERVAL '1 minute',
    if_not_exists     => TRUE
);

CREATE MATERIALIZED VIEW IF NOT EXISTS metrics_1hour
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time)    AS bucket,
    tenant_id,
    AVG(cpu)                        AS avg_cpu,
    MAX(cpu)                        AS max_cpu,
    AVG(latency)                    AS avg_latency,
    MAX(latency)                    AS max_latency,
    AVG(error_rate)                 AS avg_error_rate,
    COUNT(*)                        AS sample_count
FROM metrics
GROUP BY bucket, tenant_id
WITH NO DATA;

SELECT add_continuous_aggregate_policy('metrics_1hour',
    start_offset      => INTERVAL '4 hours',
    end_offset        => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists     => TRUE
);
