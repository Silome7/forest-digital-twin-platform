import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, GeoJSON, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

interface Props {
  forestId: number;
  metrics?: any;
  riskLevel?: string;
}

function MapUpdater({ geoData, zoneId }: { geoData: any; zoneId: number }) {
  const map = useMap();
  useEffect(() => {
    if (!geoData?.features?.length) return;
    const selected = geoData.features.filter(
      (f: any) => f.properties?.id === zoneId && f.geometry
    );
    if (selected.length > 0) {
      const layer = L.geoJSON({ type: 'FeatureCollection' as const, features: selected } as any);
      const bounds = layer.getBounds();
      if (bounds.isValid()) map.fitBounds(bounds, { padding: [60, 60] });
    }
  }, [geoData, zoneId, map]);
  return null;
}

const getRiskFillColor = (riskLevel: string) => {
  switch (riskLevel?.toLowerCase()) {
    case 'critical': return '#FF0000';
    case 'high':     return '#FF6600';
    case 'medium':   return '#FFD700';
    default:         return '#27AE60';
  }
};

const Forest2D: React.FC<Props> = ({ forestId, metrics, riskLevel = 'normal' }) => {
  const [geoData, setGeoData] = useState<any>(null);
  const [sensors, setSensors] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const token = localStorage.getItem('access_token') || localStorage.getItem('token');

  useEffect(() => {
    setLoading(true);
    const headers = { Authorization: `Bearer ${token}` };

    fetch('/api/zones/geojson', { headers })
      .then(res => res.json())
      .then(data => { setGeoData(data); setLoading(false); })
      .catch(() => { setError('Impossible de charger les zones'); setLoading(false); });

    fetch(`/api/zones/${forestId}/sensors`, { headers })
      .then(res => res.json())
      .then(data => setSensors(data.data || []))
      .catch(() => setSensors([]));

  }, [forestId, token]);

  const getZoneStyle = (feature: any) => {
    const isSelected = feature?.properties?.id === forestId;
    const fillColor = isSelected ? getRiskFillColor(riskLevel) : '#2ECC71';
    return {
      color: isSelected ? fillColor : '#27AE60',
      weight: isSelected ? 3 : 1.5,
      fillColor,
      fillOpacity: isSelected ? 0.5 : 0.15,
    };
  };

  const onEachZone = (feature: any, layer: any) => {
    if (!feature.properties) return;
    const isSelected = feature.properties.id === forestId;
    const temp = metrics?.avg_temperature?.toFixed(1) ?? 'N/A';
    const humidity = metrics?.avg_humidity?.toFixed(1) ?? 'N/A';
    const ndvi = metrics?.avg_ndvi?.toFixed(3) ?? 'N/A';
    const fire = metrics?.fire_risk_score?.toFixed(1) ?? 'N/A';

    layer.bindPopup(`
      <div style="font-family:sans-serif; min-width:180px; line-height:1.6">
        <strong style="font-size:14px">${isSelected ? '📍' : '🌲'} ${feature.properties.name}</strong>
        ${feature.properties.location ? `<br/>📌 ${feature.properties.location}` : ''}
        ${isSelected ? `
          <hr style="margin:6px 0; border-color:#eee"/>
          <div>🌡️ Température : <b>${temp} °C</b></div>
          <div>💧 Humidité : <b>${humidity} %</b></div>
          <div>🌿 NDVI : <b>${ndvi}</b></div>
          <div>🔥 Fire Risk : <b>${fire}</b></div>
        ` : ''}
      </div>
    `);

    layer.on('mouseover', () => layer.setStyle({ fillOpacity: isSelected ? 0.7 : 0.3 }));
    layer.on('mouseout', () => layer.setStyle({ fillOpacity: isSelected ? 0.5 : 0.15 }));
    if (isSelected) setTimeout(() => layer.openPopup(), 300);
  };

  if (loading) return (
    <div className="h-full w-full flex items-center justify-center" style={{ background: '#0a1628' }}>
      <div className="text-center text-white">
        <div className="text-4xl mb-2 animate-pulse">🌲</div>
        <p className="text-gray-400">Chargement de la carte satellite...</p>
      </div>
    </div>
  );

  if (error) return (
    <div className="h-full w-full flex items-center justify-center bg-red-950">
      <p className="text-red-400">⚠️ {error}</p>
    </div>
  );

  return (
    <MapContainer
      center={[35.2, -5.0]}
      zoom={7}
      className="h-full w-full"
    >
      {/* Fond satellite Esri */}
      <TileLayer
        url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
        attribution="&copy; Esri"
      />
      {/* Labels CartoDB */}
      <TileLayer
        url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager_only_labels/{z}/{x}/{y}{r}.png"
        attribution="&copy; CartoDB"
        opacity={0.8}
      />

      {geoData && (
        <>
          <GeoJSON
            key={`${forestId}-${riskLevel}`}
            data={geoData}
            style={getZoneStyle}
            onEachFeature={onEachZone}
          />
          <MapUpdater geoData={geoData} zoneId={forestId} />
        </>
      )}

      {/* Capteurs */}
      {sensors.map((sensor: any) =>
        sensor.latitude && sensor.longitude ? (
          <Marker key={sensor.id} position={[sensor.latitude, sensor.longitude]}>
            <Popup>
              <div style={{ fontFamily: 'sans-serif', lineHeight: '1.6' }}>
                <strong>📡 {sensor.name}</strong><br />
                Type : {sensor.type}<br />
                Statut :{' '}
                <span style={{ color: sensor.status === 'active' ? '#16a34a' : '#ea580c', fontWeight: 'bold' }}>
                  {sensor.status}
                </span><br />
                Batterie : {sensor.battery_level ?? 'N/A'}%
              </div>
            </Popup>
          </Marker>
        ) : null
      )}
    </MapContainer>
  );
};

export default Forest2D;