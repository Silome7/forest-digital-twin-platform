import React, { useState, useEffect } from 'react';
import {
  ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, ReferenceLine
} from 'recharts';

interface Props {
  zoneId: number;
  zoneName?: string;
}

const PERIODS = [
  { label: '3 mois', value: '3m' },
  { label: '6 mois', value: '6m' },
  { label: '1 an',   value: '1y' },
  { label: '2 ans',  value: '2y' },
  { label: 'Tout',   value: 'all' },
];

const METRICS = [
  { key: 'avg_ndvi',        label: 'NDVI',            color: '#22c55e', yAxis: 'ndvi' },
  { key: 'avg_temperature', label: 'Température (°C)', color: '#f97316', yAxis: 'temp' },
  { key: 'avg_humidity',    label: 'Humidité (%)',     color: '#3b82f6', yAxis: 'temp' },
  { key: 'fire_risk_score', label: 'Fire Risk',        color: '#ef4444', yAxis: 'temp' },
  { key: 'health_index',    label: 'Health Index',     color: '#a855f7', yAxis: 'temp' },
];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: '#1e293b', border: '1px solid #334155',
      borderRadius: 8, padding: '10px 14px', fontSize: 12, color: '#f1f5f9'
    }}>
      <p style={{ fontWeight: 'bold', marginBottom: 6, color: '#94a3b8' }}>{label}</p>
      {payload.map((p: any) => (
        <div key={p.dataKey} style={{ color: p.color, marginBottom: 2 }}>
          {p.name} : <strong>{p.value?.toFixed(3)}</strong>
        </div>
      ))}
    </div>
  );
};

const ZoneHistoryChart: React.FC<Props> = ({ zoneId, zoneName }) => {
  const [data, setData] = useState<any[]>([]);
  const [period, setPeriod] = useState('1y');
  const [granularity, setGranularity] = useState('monthly');
  const [activeMetrics, setActiveMetrics] = useState(['avg_ndvi', 'avg_temperature']);
  const [loading, setLoading] = useState(true);
  const token = localStorage.getItem('access_token') || localStorage.getItem('token');

  useEffect(() => {
    if (!zoneId) return;
    setLoading(true);
    fetch(`/api/zones/${zoneId}/history?period=${period}&granularity=${granularity}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(r => r.json())
      .then(d => { setData(d.data || []); setLoading(false); })
      .catch(() => setLoading(false));
  }, [zoneId, period, granularity]);

  const toggleMetric = (key: string) => {
    setActiveMetrics(prev =>
      prev.includes(key) ? prev.filter(k => k !== key) : [...prev, key]
    );
  };

  return (
    <div style={{ background: '#0f172a', borderRadius: 12, padding: 20, color: '#f1f5f9' }}>

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div>
          <h3 style={{ margin: 0, fontSize: 16, fontWeight: 'bold', color: '#4ade80' }}>
            📈 Évolution historique — {zoneName || `Zone ${zoneId}`}
          </h3>
          <p style={{ margin: '4px 0 0', fontSize: 12, color: '#64748b' }}>
            Données réelles Sentinel-2 + Open-Meteo
          </p>
        </div>

        {/* Granularité */}
        <div style={{ display: 'flex', gap: 6 }}>
          {['daily', 'weekly', 'monthly'].map(g => (
            <button key={g} onClick={() => setGranularity(g)} style={{
              padding: '4px 10px', borderRadius: 6, border: 'none', fontSize: 11,
              cursor: 'pointer', fontWeight: granularity === g ? 'bold' : 'normal',
              background: granularity === g ? '#166534' : '#1e293b',
              color: granularity === g ? '#4ade80' : '#94a3b8',
            }}>
              {g === 'daily' ? 'Jour' : g === 'weekly' ? 'Semaine' : 'Mois'}
            </button>
          ))}
        </div>
      </div>

      {/* Sélecteur période */}
      <div style={{ display: 'flex', gap: 6, marginBottom: 16 }}>
        {PERIODS.map(p => (
          <button key={p.value} onClick={() => setPeriod(p.value)} style={{
            padding: '5px 14px', borderRadius: 20, border: 'none',
            cursor: 'pointer', fontSize: 12, fontWeight: period === p.value ? 'bold' : 'normal',
            background: period === p.value ? '#15803d' : '#1e293b',
            color: period === p.value ? '#fff' : '#94a3b8',
          }}>
            {p.label}
          </button>
        ))}
      </div>

      {/* Toggle métriques */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 16, flexWrap: 'wrap' }}>
        {METRICS.map(m => (
          <button key={m.key} onClick={() => toggleMetric(m.key)} style={{
            padding: '3px 10px', borderRadius: 12, border: `1px solid ${m.color}`,
            cursor: 'pointer', fontSize: 11,
            background: activeMetrics.includes(m.key) ? m.color + '33' : 'transparent',
            color: activeMetrics.includes(m.key) ? m.color : '#64748b',
          }}>
            {m.label}
          </button>
        ))}
      </div>

      {/* Graphique */}
      {loading ? (
        <div style={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#64748b' }}>
          🌲 Chargement des données...
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={320}>
          <ComposedChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis
              dataKey="date"
              tick={{ fill: '#64748b', fontSize: 11 }}
              tickFormatter={v => v.slice(0, 7)}
            />
            <YAxis
              yAxisId="ndvi"
              domain={[0, 1]}
              tick={{ fill: '#64748b', fontSize: 11 }}
              tickFormatter={v => v.toFixed(2)}
              label={{ value: 'NDVI', angle: -90, position: 'insideLeft', fill: '#4ade80', fontSize: 11 }}
            />
            <YAxis
              yAxisId="temp"
              orientation="right"
              tick={{ fill: '#64748b', fontSize: 11 }}
              label={{ value: 'Valeur', angle: 90, position: 'insideRight', fill: '#94a3b8', fontSize: 11 }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: 12, color: '#94a3b8', paddingTop: 8 }}
            />
            <ReferenceLine yAxisId="ndvi" y={0.5} stroke="#334155" strokeDasharray="4 4" />

            {METRICS.filter(m => activeMetrics.includes(m.key)).map(m => (
              m.key === 'avg_ndvi' ? (
                <Line
                  key={m.key}
                  yAxisId="ndvi"
                  type="monotone"
                  dataKey={m.key}
                  name={m.label}
                  stroke={m.color}
                  strokeWidth={2.5}
                  dot={false}
                  activeDot={{ r: 5 }}
                />
              ) : (
                <Line
                  key={m.key}
                  yAxisId="temp"
                  type="monotone"
                  dataKey={m.key}
                  name={m.label}
                  stroke={m.color}
                  strokeWidth={1.5}
                  dot={false}
                  activeDot={{ r: 4 }}
                />
              )
            ))}
          </ComposedChart>
        </ResponsiveContainer>
      )}

      {/* Footer stats */}
      {data.length > 0 && (
        <div style={{ display: 'flex', gap: 16, marginTop: 12, paddingTop: 12, borderTop: '1px solid #1e293b' }}>
          {[
            { label: 'NDVI moyen', value: (data.reduce((s, d) => s + (d.avg_ndvi || 0), 0) / data.length).toFixed(3), color: '#22c55e' },
            { label: 'Temp. max', value: Math.max(...data.map(d => d.avg_temperature || 0)).toFixed(1) + '°C', color: '#f97316' },
            { label: 'Fire Risk moyen', value: (data.reduce((s,d) => s + (d.fire_risk_score||0), 0) / data.length).toFixed(1), color: '#ef4444' },
            { label: 'Points de données', value: data.length, color: '#94a3b8' },
          ].map((s, i) => (
            <div key={i} style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 16, fontWeight: 'bold', color: s.color }}>{s.value}</div>
              <div style={{ fontSize: 11, color: '#64748b' }}>{s.label}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ZoneHistoryChart;