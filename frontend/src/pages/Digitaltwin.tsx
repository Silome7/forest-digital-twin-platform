import React, { useState, useEffect } from 'react';
import Forest2D from '../Digital twin/Forest2D';
import Forest3D from '../Digital twin/Forest3D';
import ErrorBoundary from '../components/Common/ErrorBoundary';
import ZoneHistoryChart from '../components/Dashboard/ZoneHistoryChart';

interface Zone { id: number; name: string; location: string; }
interface Metrics {
  health_score: number; status: string; risk_level: string;
  temperature_avg: number; humidity_avg: number;
  air_quality_index: number; sensor_coverage: number;
  updated_at: string;
}

const getRiskColor = (level: string) => {
  switch (level?.toLowerCase()) {
    case 'critical': return { bg: 'bg-red-100', text: 'text-red-700', badge: 'bg-red-600', dot: '🔴' };
    case 'high':     return { bg: 'bg-orange-100', text: 'text-orange-700', badge: 'bg-orange-500', dot: '🟠' };
    case 'medium':   return { bg: 'bg-yellow-100', text: 'text-yellow-700', badge: 'bg-yellow-500', dot: '🟡' };
    default:         return { bg: 'bg-green-100', text: 'text-green-700', badge: 'bg-green-600', dot: '🟢' };
  }
};

const DigitalTwin: React.FC = () => {
  const [zones, setZones] = useState<Zone[]>([]);
  const [selectedZone, setSelectedZone] = useState<number | null>(null);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [zoneMetrics, setZoneMetrics] = useState<any[]>([]);
  const [view, setView] = useState<'2d' | '3d' | 'chart'>('2d');
  const [loading, setLoading] = useState(true);
  const token = localStorage.getItem('access_token') || localStorage.getItem('token');
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    fetch('/api/zones', { headers })
      .then(r => r.json())
      .then(d => {
        const list = d.data || [];
        setZones(list);
        if (list.length > 0) setSelectedZone(list[0].id);
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    if (!selectedZone) return;
    fetch(`/api/zones/${selectedZone}/status`, { headers })
      .then(r => r.json()).then(d => setMetrics(d.data || null));
    fetch(`/api/zones/${selectedZone}/metrics?limit=30`, { headers })
      .then(r => r.json()).then(d => setZoneMetrics(d.data || []));
  }, [selectedZone]);

  const risk = getRiskColor(metrics?.risk_level || 'normal');
  const lastMetric = zoneMetrics[0];

  return (
    <div className="flex h-screen bg-gray-950 text-white overflow-hidden" style={{ marginTop: '-24px' }}>

      {/* PANNEAU GAUCHE */}
      <div className="w-80 bg-gray-900 border-r border-gray-800 flex flex-col overflow-y-auto">

        <div className="p-4 border-b border-gray-800">
          <h1 className="text-lg font-bold text-emerald-400">🌲 Forest Digital Twin</h1>
          <p className="text-xs text-gray-400 mt-1">Monitoring en temps réel</p>
        </div>

        <div className="p-4 border-b border-gray-800">
          <label className="text-xs text-gray-400 uppercase tracking-wider mb-2 block">Zone forestière</label>
          {loading ? <div className="text-gray-500 text-sm">Chargement...</div> : (
            <select
              value={selectedZone || ''}
              onChange={e => setSelectedZone(Number(e.target.value))}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-white"
            >
              {zones.map(z => (
                <option key={z.id} value={z.id}>🌲 {z.name}</option>
              ))}
            </select>
          )}
        </div>

        {metrics && (
          <div className="p-4 border-b border-gray-800">
            <div className={`flex items-center justify-between rounded-lg p-3 ${risk.bg}`}>
              <div>
                <div className={`text-xs font-bold uppercase ${risk.text}`}>Niveau de risque</div>
                <div className={`text-lg font-bold ${risk.text}`}>{risk.dot} {metrics.risk_level || 'Normal'}</div>
              </div>
              <div className={`text-right ${risk.text}`}>
                <div className="text-2xl font-bold">{metrics.health_score?.toFixed(0)}</div>
                <div className="text-xs">Health Score</div>
              </div>
            </div>
          </div>
        )}

        <div className="p-4 space-y-3">
          <div className="text-xs text-gray-400 uppercase tracking-wider mb-2">Données capteurs</div>
          {[
            { icon: '🌡️', label: 'Température',       value: metrics?.temperature_avg?.toFixed(1) + ' °C', color: 'text-orange-400' },
            { icon: '💧', label: 'Humidité',           value: metrics?.humidity_avg?.toFixed(1) + ' %',     color: 'text-blue-400' },
            { icon: '🌿', label: 'NDVI',               value: lastMetric?.avg_ndvi?.toFixed(3) || 'N/A',    color: 'text-green-400' },
            { icon: '🔥', label: 'Fire Risk Score',    value: lastMetric?.fire_risk_score?.toFixed(1) || 'N/A', color: 'text-red-400' },
            { icon: '📡', label: 'Couverture capteurs',value: metrics?.sensor_coverage ? metrics.sensor_coverage + ' %' : 'N/A', color: 'text-purple-400' },
          ].map((kpi, i) => (
            <div key={i} className="flex items-center justify-between bg-gray-800 rounded-lg px-3 py-2">
              <span className="text-sm text-gray-300">{kpi.icon} {kpi.label}</span>
              <span className={`text-sm font-bold ${kpi.color}`}>{kpi.value}</span>
            </div>
          ))}
        </div>

        {metrics?.updated_at && (
          <div className="p-4 mt-auto border-t border-gray-800">
            <p className="text-xs text-gray-500">
              🕐 Mis à jour : {new Date(metrics.updated_at).toLocaleString('fr-FR')}
            </p>
          </div>
        )}
      </div>

      {/* ZONE PRINCIPALE */}
      <div className="flex-1 flex flex-col overflow-hidden">

        {/* Toolbar */}
        <div className="flex items-center justify-between px-4 py-2 bg-gray-900 border-b border-gray-800">
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-300">
              {zones.find(z => z.id === selectedZone)?.name || '...'}
            </span>
            {metrics && (
              <span className={`text-xs px-2 py-0.5 rounded-full text-white ${risk.badge}`}>
                {metrics.status || 'Active'}
              </span>
            )}
          </div>
          <div className="flex space-x-1">
            <button
              onClick={() => setView('2d')}
              className={`px-4 py-1.5 rounded text-sm font-medium transition-all ${view === '2d' ? 'bg-emerald-600 text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'}`}
            >
              🗺️ 2D
            </button>
            <button
              onClick={() => setView('3d')}
              className={`px-4 py-1.5 rounded text-sm font-medium transition-all ${view === '3d' ? 'bg-emerald-600 text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'}`}
            >
              🌐 3D
            </button>
            <button
              onClick={() => setView('chart')}
              className={`px-4 py-1.5 rounded text-sm font-medium transition-all ${view === 'chart' ? 'bg-emerald-600 text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'}`}
            >
              📈 Historique
            </button>
          </div>
        </div>

        {/* Contenu principal */}
        <div className="flex-1 overflow-y-auto">
          <ErrorBoundary>
            {view === '2d' && selectedZone && (
              <div className="h-full">
                <Forest2D forestId={selectedZone} metrics={lastMetric} riskLevel={metrics?.risk_level || 'normal'} />
              </div>
            )}
            {view === '3d' && selectedZone && (
              <div className="h-full">
                <Forest3D forestId={selectedZone} metrics={lastMetric} riskLevel={metrics?.risk_level || 'normal'} />
              </div>
            )}
            {view === 'chart' && selectedZone && (
              <div className="p-6">
                <ZoneHistoryChart
                  zoneId={selectedZone}
                  zoneName={zones.find(z => z.id === selectedZone)?.name}
                />
              </div>
            )}
          </ErrorBoundary>
        </div>
      </div>
    </div>
  );
};

export default DigitalTwin;