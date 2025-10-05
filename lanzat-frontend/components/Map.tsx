import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import { useEffect, useState } from 'react';
import { FeatureCollection } from 'geojson';
import axios from 'axios';
import L from 'leaflet';
import Legend from './Legend';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface CountyProperties {
  NAME: string;
  vulnerability_score?: number;
  enhanced_vulnerability?: number;
  risk_category?: string;
  hurricane_risk?: number;
  gdp?: number;
  social_vulnerability?: number;
  population?: number;
  [key: string]: string | number | undefined;
}

interface CountyFeature {
  properties: CountyProperties;
  [key: string]: unknown;
}

interface MapProps {
  onCountySelect: (county: CountyFeature | null) => void;
  selectedCounty: CountyFeature | null;
}

export default function Map({ onCountySelect, selectedCounty }: MapProps) {
  const [countiesData, setCountiesData] = useState<FeatureCollection | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadCountiesData();
  }, []);

  const loadCountiesData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/api/counties`);
      setCountiesData(response.data);
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load county data';
      console.error('Error loading counties:', err);
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const getColor = (score: number): string => {
    if (score >= 0.8) return '#8B0000'; // Critical - Dark Red
    if (score >= 0.6) return '#DC143C'; // High - Red
    if (score >= 0.4) return '#FF8C00'; // Moderate - Orange
    if (score >= 0.2) return '#FFD700'; // Low - Yellow
    return '#FFFFE0';                   // Very Low - Light Yellow
  };

  const getCountyStyle = (feature?: CountyFeature) => {
    if (!feature) return {};

    const score = feature.properties.vulnerability_score || 0;

    return {
      fillColor: getColor(score),
      weight: selectedCounty?.properties?.NAME === feature.properties.NAME ? 3 : 1,
      opacity: 1,
      color: selectedCounty?.properties?.NAME === feature.properties.NAME ? '#000' : '#666',
      fillOpacity: 0.7
    };
  };

  const onEachCounty = (feature: CountyFeature, layer: L.Layer) => {
    const props = feature.properties;

    // Popup content
    const popupContent = `
      <div class="p-3">
        <h3 class="font-bold text-lg mb-2">${props.NAME} County</h3>
        <div class="space-y-1 text-sm">
          <p><strong>Vulnerability:</strong> ${((props.vulnerability_score || 0) * 100).toFixed(1)}%</p>
          <p><strong>Category:</strong> <span class="font-semibold">${props.risk_category || 'Unknown'}</span></p>
          <p><strong>Hurricane Risk:</strong> ${((props.hurricane_risk || 0) * 100).toFixed(1)}%</p>
          <p><strong>Population:</strong> ${props.population?.toLocaleString() || 'N/A'}</p>
          ${props.gdp ? `<p><strong>GDP:</strong> $${(props.gdp / 1000).toFixed(1)}B</p>` : ''}
        </div>
      </div>
    `;

    layer.bindPopup(popupContent);

    // Click handler
    layer.on({
      click: () => {
        onCountySelect(feature);
      },
      mouseover: (e) => {
        const layer = e.target;
        layer.setStyle({
          weight: 3,
          color: '#000',
          fillOpacity: 0.9
        });
      },
      mouseout: (e) => {
        const layer = e.target;
        layer.setStyle(getCountyStyle(feature));
      }
    });
  };

  if (loading) {
    return (
      <div className="h-full w-full flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading vulnerability data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-full w-full flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="text-red-500 text-5xl mb-4">⚠️</div>
          <h2 className="text-xl font-bold text-gray-800 mb-2">Error Loading Data</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <p className="text-sm text-gray-500 mb-4">
            Make sure the backend API is running at {API_URL}
          </p>
          <button
            onClick={loadCountiesData}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!countiesData) {
    return null;
  }

  return (
    <div className="h-full w-full relative">
      <MapContainer
        center={[27.9944, -81.7603]}
        zoom={7}
        className="h-full w-full"
        style={{ background: '#E0F2FF' }}
        scrollWheelZoom={true}
        touchZoom={true}
        doubleClickZoom={true}
        dragging={true}
        zoomControl={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <GeoJSON
          data={countiesData}
          style={getCountyStyle}
          onEachFeature={onEachCounty}
        />
      </MapContainer>

      <Legend />
    </div>
  );
}
