# ═══════════════════════════════════════════════
# PROMETHEUS UNBOUND — Ghostgres Prompt Templates
# All AI prompts live here in one place
# ═══════════════════════════════════════════════

ANOMALY_ANALYSIS_PROMPT = """
You are analyzing a time-series metrics anomaly in a production system.

ANOMALY DETAILS:
- Tenant    : {tenant_id}
- Metric    : {metric}
- Value     : {value}
- Z-score   : {zscore}
- Timestamp : {timestamp}

RECENT VALUES (last 10 readings):
{recent_values}

Respond in this exact JSON format:
{{
    "root_cause": "what likely caused this",
    "recommended_action": "what to do right now",
    "investigate_next": "what to check next",
    "severity": "low or medium or high or critical",
    "confidence": 0.0
}}

JSON only. No extra text.
"""

QUERY_OPTIMIZATION_PROMPT = """
You are a TimescaleDB expert.

This query is running slowly:
{query}

Execution plan:
{explain_output}

Suggest optimizations in this exact JSON format:
{{
    "problem": "what is causing the slowness",
    "suggestion": "how to fix it",
    "optimized_query": "the improved query if applicable",
    "confidence": 0.0
}}

JSON only. No extra text.
"""

HEALTH_SUMMARY_PROMPT = """
You are summarizing the health of a multi-tenant metrics platform.

CURRENT HEALTH SCORES:
{health_scores}

RECENT INCIDENTS:
{recent_incidents}

ANOMALY COUNT (last hour):
{anomaly_count}

Write a short 3 sentence plain English health summary.
Focus on the most critical issues first.
"""
