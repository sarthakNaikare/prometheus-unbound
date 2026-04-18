#!/bin/bash
echo "Resetting database..."
docker-compose down -v
docker-compose up -d timescaledb
echo "Waiting for TimescaleDB to start..."
sleep 10
echo "Database reset complete"
