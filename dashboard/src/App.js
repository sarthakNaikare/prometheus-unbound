import React, { useState, useEffect } from 'react';
import './App.css';

const API = 'http://localhost:8000';
const TENANTS = ['tenant_alpha', 'tenant_beta', 'tenant_gamma'];
const DOTS = {
  tenant_alpha: 'dot-alpha',
  tenant_beta: 'dot-beta',
  tenant_gamma: 'dot-gamma',
};

function getHealthColor(score) {
  if (score >= 70) return 'health-high';
  if (score >= 40) return 'health-mid';
  return 'health-low';
}

function timeAgo(ts) {
  const diff = Math.floor((Date.now() - new Date(ts)) / 1000);
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  return `${Math.floor(diff / 3600)}h ago`;
}

function StatCard({ title, value, sub, color }) {
  return (
    <div className="card">
      <div className="card-title">{title}</div>
      <div className="metric-value" style={{ color: color || '#f1f5f9' }}>
        {value}
      </div>
      {sub && <div className="metric-sub">{sub}</div>}
    </div>
  );
}

function TenantCard({ tenant, metrics, health }) {
  const latest = metrics?.[0];
  const score = health?.health_score ?? 100;
  return (
    <div className="tenant-card">
      <div className="tenant-name">
        <span className={`tenant-dot ${DOTS[tenant]}`}></span>
        {tenant}
        <span style={{ marginLeft: 'auto', fontSize: '24px', fontWeight: 800 }}
          className={getHealthColor(score)}>
          {score}
        </span>
      </div>
      {latest ? (
        <>
          <div className="metric-row">
            <span className="metric-label">CPU</span>
            <span className="metric-val">{latest.cpu?.toFixed(1)}%</span>
          </div>
          <div className="bar-container">
            <div className="bar-fill" style={{
              width: `${latest.cpu}%`,
              background: latest.cpu > 80 ? '#ef4444' : '#3b82f6'
            }} />
          </div>
          <div className="metric-row" style={{ marginTop: 12 }}>
            <span className="metric-label">Latency</span>
            <span className="metric-val">{latest.latency?.toFixed(0)}ms</span>
          </div>
          <div className="bar-container">
            <div className="bar-fill" style={{
              width: `${Math.min(latest.latency / 10, 100)}%`,
              background: latest.latency > 400 ? '#ef4444' : '#8b5cf6'
            }} />
          </div>
          <div className="metric-row" style={{ marginTop: 12 }}>
            <span className="metric-label">Error rate</span>
            <span className="metric-val">{latest.error_rate?.toFixed(2)}%</span>
          </div>
          <div className="metric-row">
            <span className="metric-label">Anomalies (1hr)</span>
            <span className="metric-val" style={{ color: '#f97316' }}>
              {health?.anomalies_last_hour ?? 0}
            </span>
          </div>
          <div className="metric-row">
            <span className="metric-label">Open incidents</span>
            <span className="metric-val" style={{ color: '#ef4444' }}>
              {health?.open_incidents ?? 0}
            </span>
          </div>
        </>
      ) : (
        <div className="empty-state">No data yet</div>
      )}
    </div>
  );
}

function AnomalyFeed({ anomalies }) {
  if (!anomalies?.length) return <div className="empty-state">No anomalies detected</div>;
  return anomalies.slice(0, 8).map((a, i) => (
    <div className="anomaly-item" key={i}>
      <span className={`anomaly-badge badge-${a.zscore > 4 ? 'critical' : a.zscore > 3.5 ? 'high' : 'medium'}`}>
        z={a.zscore?.toFixed(2)}
      </span>
      <div className="anomaly-info">
        <div className="anomaly-tenant">{a.tenant_id}</div>
        <div className="anomaly-detail">{a.metric} = {a.value?.toFixed(2)}</div>
      </div>
      <div style={{ fontSize: 11, color: '#64748b' }}>{timeAgo(a.time)}</div>
    </div>
  ));
}

function IncidentFeed({ incidents }) {
  if (!incidents?.length) return <div className="empty-state">No incidents logged</div>;
  return incidents.slice(0, 6).map((inc, i) => (
    <div className="incident-item" key={i}>
      <div className="incident-header">
        <span className="incident-tenant">{inc.tenant_id}</span>
        <span className="incident-time">{timeAgo(inc.time)}</span>
      </div>
      <div className="incident-cause">{inc.root_cause}</div>
      <div className="incident-action">Action: {inc.action_taken}</div>
    </div>
  ));
}

function AIFeed({ logs }) {
  if (!logs?.length) return <div className="empty-state">No AI suggestions yet</div>;
  return logs.slice(0, 6).map((log, i) => {
    let suggestion = {};
    try { suggestion = JSON.parse(log.suggestion); } catch (e) {}
    return (
      <div className="ai-item" key={i}>
        <div className="ai-header">
          <span className="ai-tenant">{log.tenant_id}</span>
          <span className="ai-confidence">
            {log.confidence ? `${(log.confidence * 100).toFixed(0)}% confidence` : ''}
          </span>
        </div>
        <div className="ai-suggestion">
          {suggestion.recommended_action || log.suggestion?.slice(0, 100)}
        </div>
      </div>
    );
  });
}

export default function App() {
  const [health, setHealth] = useState({});
  const [metrics, setMetrics] = useState({});
  const [anomalies, setAnomalies] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [aiLogs, setAiLogs] = useState([]);
  const [systemHealth, setSystemHealth] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  async function fetchAll() {
    try {
      const [sysRes, anomRes, incRes, aiRes] = await Promise.all([
        fetch(`${API}/health`),
        fetch(`${API}/anomalies?limit=20`),
        fetch(`${API}/incidents?limit=20`),
        fetch(`${API}/ai-logs?limit=20`),
      ]);
      setSystemHealth(await sysRes.json());
      setAnomalies((await anomRes.json()).data || []);
      setIncidents((await incRes.json()).data || []);
      setAiLogs((await aiRes.json()).data || []);

      const healthData = {};
      const metricsData = {};
      for (const tenant of TENANTS) {
        const [hRes, mRes] = await Promise.all([
          fetch(`${API}/health-score/${tenant}`),
          fetch(`${API}/metrics/${tenant}?limit=1`),
        ]);
        healthData[tenant] = await hRes.json();
        metricsData[tenant] = (await mRes.json()).data || [];
      }
      setHealth(healthData);
      setMetrics(metricsData);
      setLastUpdate(new Date().toLocaleTimeString());
    } catch (e) {
      console.error('API error:', e);
    }
  }

  useEffect(() => {
    fetchAll();
    const interval = setInterval(fetchAll, 5000);
    return () => clearInterval(interval);
  }, []);

  const totalMetrics = systemHealth?.total_metrics ?? 0;
  const totalAnomalies = anomalies.length;
  const totalIncidents = incidents.length;
  const avgHealth = Object.values(health).length
    ? Math.round(Object.values(health).reduce((a, b) => a + (b.health_score || 0), 0) / Object.values(health).length)
    : 100;

  return (
    <div className="app">
      <div className="header">
        <div className="header-left">
          <h1>🔥 Prometheus Unbound</h1>
          <p>Self-healing AI metrics platform · TimescaleDB + Ghostgres</p>
        </div>
        <div>
          <span className="status-dot"></span>
          <span style={{ fontSize: 13, color: '#64748b' }}>
            Live · updates every 5s · {lastUpdate}
          </span>
        </div>
      </div>

      <div className="grid-4">
        <StatCard title="Total metrics" value={totalMetrics.toLocaleString()} sub="rows in TimescaleDB" />
        <StatCard title="Anomalies detected" value={totalAnomalies} sub="last 50 checks" color="#f97316" />
        <StatCard title="Incidents logged" value={totalIncidents} sub="self-healing actions" color="#ef4444" />
        <StatCard title="Avg health score" value={avgHealth} sub="across all tenants" color={avgHealth >= 70 ? '#22c55e' : avgHealth >= 40 ? '#f59e0b' : '#ef4444'} />
      </div>

      <div className="section-title">📊 Tenant health — live</div>
      <div className="grid-3">
        {TENANTS.map(tenant => (
          <TenantCard
            key={tenant}
            tenant={tenant}
            metrics={metrics[tenant]}
            health={health[tenant]}
          />
        ))}
      </div>

      <div className="grid-3">
        <div className="card">
          <div className="section-title">🚨 Recent anomalies</div>
          <AnomalyFeed anomalies={anomalies} />
        </div>
        <div className="card">
          <div className="section-title">📝 Incident log</div>
          <IncidentFeed incidents={incidents} />
        </div>
        <div className="card">
          <div className="section-title">👻 Ghostgres AI suggestions</div>
          <AIFeed logs={aiLogs} />
        </div>
      </div>
    </div>
  );
}
