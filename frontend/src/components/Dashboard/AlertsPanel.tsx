import React, { useState, useEffect } from 'react';

interface Alert {
  id: number;
  alert_type: string;
  severity: string;
  title: string;
  description: string;
  recommended_action: string;
  created_at: string;
  acknowledged: boolean;
}

const getSeverityStyle = (severity: string) => {
  switch (severity?.toLowerCase()) {
    case 'critical': return { border: '#ef4444', bg: '#450a0a', icon: '🔴' };
    case 'high':     return { border: '#f97316', bg: '#431407', icon: '🟠' };
    case 'warning':  return { border: '#eab308', bg: '#422006', icon: '🟡' };
    default:         return { border: '#22c55e', bg: '#052e16', icon: '🟢' };
  }
};

const AlertsPanel: React.FC<{ zoneId: number }> = ({ zoneId }) => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [expanded, setExpanded] = useState<number | null>(null);
  const token = localStorage.getItem('access_token') || localStorage.getItem('token');

  useEffect(() => {
    if (!zoneId) return;
    fetch(`/api/zones/${zoneId}/alerts`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(r => r.json())
      .then(d => {
        // Dédupliquer par date+type et trier Critical/High en premier
        const raw = d.data || [];
        const seen = new Set();
        const deduped = raw.filter((a: Alert) => {
          const key = `${a.alert_type}-${a.severity}-${a.created_at?.slice(0,10)}`;
          if (seen.has(key)) return false;
          seen.add(key);
          return true;
        }).sort((a: Alert, b: Alert) => {
          const order: any = { Critical: 0, High: 1, Warning: 2 };
          return (order[a.severity] ?? 3) - (order[b.severity] ?? 3);
        });
        setAlerts(deduped.slice(0, 10));
      })
      .catch(() => setAlerts([]));
  }, [zoneId]);

  const unacked = alerts.filter(a => !a.acknowledged).length;

  return (
    <div className="p-4 border-b border-gray-800">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs text-gray-400 uppercase tracking-wider">
          ⚠️ Alertes actives
        </span>
        {unacked > 0 && (
          <span className="bg-red-600 text-white text-xs px-2 py-0.5 rounded-full font-bold">
            {unacked}
          </span>
        )}
      </div>

      {alerts.length === 0 ? (
        <div className="text-xs text-gray-500 text-center py-2">🟢 Aucune alerte active</div>
      ) : (
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {alerts.map(alert => {
            const style = getSeverityStyle(alert.severity);
            const isOpen = expanded === alert.id;
            return (
              <div
                key={alert.id}
                onClick={() => setExpanded(isOpen ? null : alert.id)}
                style={{ borderLeft: `3px solid ${style.border}`, background: style.bg }}
                className="rounded-r-lg p-2 cursor-pointer hover:opacity-90 transition-opacity"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white">
                    {style.icon} {alert.alert_type}
                  </span>
                  <span className="text-xs text-gray-400">
                    {new Date(alert.created_at).toLocaleDateString('fr-FR')}
                  </span>
                </div>
                <p className="text-xs text-gray-300 mt-0.5 truncate">{alert.title}</p>

                {isOpen && (
                  <div className="mt-2 pt-2 border-t border-gray-700 space-y-1">
                    <p className="text-xs text-gray-300">{alert.description}</p>
                    <p className="text-xs text-emerald-400">
                      💡 {alert.recommended_action}
                    </p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default AlertsPanel;