# Prometheus Unbound — Architecture

## Overview

Prometheus Unbound is a self-healing AI metrics platform
built on TimescaleDB and Ghostgres.

When an anomaly is detected the system does not just alert.
It reasons over the data using Ghostgres, decides what action
to take, acts on it, and logs the entire incident lifecycle.

## Data Flow

Generator -> Kafka -> Consumer -> TimescaleDB
                                      |
                              Anomaly Engine
                                      |
                               Ghostgres AI
                                      |
                            Decision Engine
                                      |
                         incidents + ai_logs
                                      |
                                   Grafana

## TimescaleDB Features Used

- Hypertable: automatic time partitioning
- Continuous aggregates: live 1min and 1hour rollups
- Compression policy: compress after 7 days
- Retention policy: drop after 30 days
- time_bucket: time binning for dashboards

## How To Run

make start
make producer
make consumer
make anomaly
