# Ghostgres Integration

## What is Ghostgres

Ghostgres is a psql-compatible endpoint where Claude AI
is the query engine. You connect to it exactly like a
normal Postgres database but instead of SQL you send
natural language and get AI reasoning back.

## Connection

psql postgres://anthropic:YOUR_KEY@try.ghostgres.com/claude-sonnet-4-6

## How We Use It

1. Anomaly engine detects a spike in TimescaleDB
2. Decision engine reads the anomaly
3. Decision engine connects to Ghostgres
4. Sends anomaly context as a natural language prompt
5. Ghostgres returns structured JSON root cause analysis
6. Decision engine acts on the suggestion
7. Full incident logged to TimescaleDB

## Example Prompt

Tenant tenant_alpha has a CPU spike.
Value: 95.2 percent
Z-score: 4.7
Recent values: 42, 44, 41, 43, 95, 94, 96

## Example Response

{
  "root_cause": "sudden CPU spike after normal baseline",
  "recommended_action": "reduce ingestion rate",
  "investigate_next": "check Kafka consumer lag",
  "severity": "high",
  "confidence": 0.85
}

## Why This Matters

Without Ghostgres the decision engine uses hardcoded
if/else rules. With Ghostgres it reasons over the actual
time-series context and gives human-quality analysis.
This is what makes Prometheus Unbound self-healing
rather than just self-monitoring.
