import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, GeoJSON } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Correction pour les icônes de marqueurs Leaflet avec Webpack/Vite
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
let DefaultIcon = L.icon({ iconUrl: icon, shadowUrl: iconShadow, iconSize: [25, 41], iconAnchor: [12, 41] });
L.Marker.prototype.options.icon = DefaultIcon;

interface Props {
  forestId: number;
}

const Forest2D: React.FC<Props> = ({ forestId }) => {
  const [geoData, setGeoData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // 1. Récupération des polygones PostGIS depuis ton API
  useEffect(() => {
    const fetchGeoData = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/zones/geojson', {
            headers: {
                // Si ton API est protégée par JWT, ajoute le token ici
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        const data = await response.json();
        setGeoData(data);
      } catch (error) {
        console.error("Erreur lors de la récupération du GeoJSON:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchGeoData();
  }, [forestId]);

  // 2. Coordonnées par défaut (Centre du Rif/Maroc)
  const centerPosition: [number, number] = [35.17, -5.27]; 

  return (
    <div className="h-full w-full relative">
      {loading && (
        <div className="absolute inset-0 z-[1000] flex items-center justify-center bg-white bg-opacity-50">
          <span className="text-emerald-600 font-semibold">Chargement du socle géospatial...</span>
        </div>
      )}
      
      <MapContainer center={centerPosition} zoom={10} className="h-full w-full">
        {/* 3. Fond de carte Satellite pour l'aspect Jumeau Numérique */}
        <TileLayer
          url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
          attribution='&copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS'
        />

        {/* 4. Affichage des zones (Polygones PostGIS) */}
        {geoData && (
          <GeoJSON 
            data={geoData} 
            style={{
              color: '#34d399',      // Vert émeraude
              weight: 2,
              fillOpacity: 0.3,
              fillColor: '#10b981'
            }}
            onEachFeature={(feature, layer) => {
              layer.bindPopup(`<strong>Zone:</strong> ${feature.properties.name}`);
            }}
          />
        )}
      </MapContainer>
    </div>
  );
};

export default Forest2D;
