import { useEffect, useState } from 'react';
import axios from 'axios';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface SelectedCountyProperties {
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

interface SelectedCounty {
  properties: SelectedCountyProperties;
  [key: string]: unknown;
}

interface DashboardProps {
  selectedCounty: SelectedCounty | null;
  onCountySelect: (county: SelectedCounty | null) => void;
}

interface County {
  name: string;
  vulnerability_score: number;
  hurricane_risk: number;
  gdp: number;
  social_vulnerability: number;
  population: number;
  risk_category: string;
}

interface CriticalRuralZone {
  name: string;
  enhanced_vulnerability: number;
  rural_status: string;
  median_home_value: number;
  gdp: number;
  population_density: number;
  fema_risk_zone: string;
}

interface PropertyExposure {
  NAME: string;
  median_home_value: number;
  property_growth_rate: number;
  fema_risk_zone: string;
}

interface Stats {
  total_counties: number;
  avg_vulnerability: number;
  max_vulnerability: number;
  min_vulnerability: number;
  vulnerability_stats?: {
    mean: number;
    max: number;
    min: number;
  };
}

interface CorrelationValues {
  gdp_vulnerability: number;
  property_vulnerability: number;
  density_vulnerability: number;
}

interface Correlations {
  correlations: CorrelationValues;
}

export default function Dashboard({ selectedCounty }: DashboardProps) {
  const [topCounties, setTopCounties] = useState<County[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [criticalRuralZones, setCriticalRuralZones] = useState<CriticalRuralZone[]>([]);
  const [propertyExposure, setPropertyExposure] = useState<PropertyExposure[]>([]);
  const [correlations, setCorrelations] = useState<Correlations | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    topCounties: true,
    propertyExposure: false,
    correlations: false,
  });

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      const [topResponse, statsResponse, criticalRuralResponse, propertyResponse, correlationsResponse] = await Promise.all([
        axios.get(`${API_URL}/api/top-vulnerable?limit=10`),
        axios.get(`${API_URL}/api/stats`),
        axios.get(`${API_URL}/api/enhanced/critical-rural`),
        axios.get(`${API_URL}/api/enhanced/property-exposure?limit=5`),
        axios.get(`${API_URL}/api/enhanced/correlations`)
      ]);

      setTopCounties(topResponse.data.counties || []);
      setStats(statsResponse.data);
      // Enhanced stats are included in correlations response
      setCriticalRuralZones(criticalRuralResponse.data.critical_rural_zones || []);
      setPropertyExposure(propertyResponse.data.top_property_exposure || []);
      setCorrelations(correlationsResponse.data);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getCategoryColor = (category: string): string => {
    switch (category) {
      case 'Critical': return 'text-red-700 bg-red-100';
      case 'High': return 'text-red-600 bg-red-50';
      case 'Moderate': return 'text-orange-600 bg-orange-50';
      case 'Low': return 'text-yellow-600 bg-yellow-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getScatterData = () => {
    return topCounties.map(county => ({
      name: county.name,
      gdp: county.gdp,
      risk: county.hurricane_risk * 100,
      vulnerability: county.vulnerability_score * 100,
      category: county.risk_category
    }));
  };

  const getScatterColor = (category: string): string => {
    switch (category) {
      case 'Critical': return '#8B0000';
      case 'High': return '#DC143C';
      case 'Moderate': return '#FF8C00';
      case 'Low': return '#FFD700';
      default: return '#CCCCCC';
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-3/4"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  const SectionHeader = ({ title, isExpanded, onToggle, alert = false }: { title: string; isExpanded: boolean; onToggle: () => void; alert?: boolean }) => (
    <button
      onClick={onToggle}
      className="w-full flex items-center justify-between text-left group"
    >
      <h3 className={`font-bold text-base sm:text-lg text-gray-800 flex items-center ${alert ? 'mb-0' : ''}`}>
        {alert && (
          <span className="bg-red-600 text-white px-1.5 sm:px-2 py-0.5 sm:py-1 rounded mr-2 text-xs sm:text-sm">ALERT</span>
        )}
        {title}
      </h3>
      <svg
        className={`w-5 h-5 text-gray-500 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
      </svg>
    </button>
  );

  return (
    <div className="p-3 sm:p-6 space-y-4 sm:space-y-6">
      {/* Selected County Detail */}
      {selectedCounty && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 sm:p-4">
          <h3 className="font-bold text-base sm:text-lg mb-2 sm:mb-3 text-blue-900">
            {selectedCounty.properties.NAME} County
          </h3>
          <div className="space-y-1.5 sm:space-y-2 text-xs sm:text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Vulnerability Score:</span>
              <span className="font-bold text-blue-900">
                {((selectedCounty.properties.vulnerability_score || 0) * 100).toFixed(1)}%
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Category:</span>
              <span className={`px-2 py-1 rounded text-xs font-semibold ${getCategoryColor(selectedCounty.properties.risk_category || 'Unknown')}`}>
                {selectedCounty.properties.risk_category || 'Unknown'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Hurricane Risk:</span>
              <span className="font-semibold">
                {((selectedCounty.properties.hurricane_risk || 0) * 100).toFixed(1)}%
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Social Vulnerability:</span>
              <span className="font-semibold">
                {((selectedCounty.properties.social_vulnerability || 0) * 100).toFixed(1)}%
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Population:</span>
              <span className="font-semibold">
                {selectedCounty.properties.population?.toLocaleString() || 'N/A'}
              </span>
            </div>
            {selectedCounty.properties.gdp && (
              <div className="flex justify-between">
                <span className="text-gray-600">County GDP:</span>
                <span className="font-semibold">
                  ${(selectedCounty.properties.gdp / 1000).toFixed(1)}B
                </span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Summary Stats */}
      {stats && stats.vulnerability_stats && (
        <div className="grid grid-cols-2 gap-2 sm:gap-4">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-3 sm:p-4">
            <p className="text-xs sm:text-sm text-blue-600 font-semibold">Avg Vulnerability</p>
            <p className="text-xl sm:text-2xl font-bold text-blue-900">
              {(stats.vulnerability_stats.mean * 100).toFixed(1)}%
            </p>
          </div>
          <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-lg p-3 sm:p-4">
            <p className="text-xs sm:text-sm text-red-600 font-semibold">Max Vulnerability</p>
            <p className="text-xl sm:text-2xl font-bold text-red-900">
              {(stats.vulnerability_stats.max * 100).toFixed(1)}%
            </p>
          </div>
        </div>
      )}

      {/* Critical Rural Zones - Always visible first */}
      {criticalRuralZones.length > 0 && (
        <div>
          <h3 className="font-bold text-base sm:text-lg mb-2 sm:mb-3 text-gray-800 flex items-center">
            <span className="bg-red-600 text-white px-1.5 sm:px-2 py-0.5 sm:py-1 rounded mr-2 text-xs sm:text-sm">ALERT</span>
            Critical Rural Zones
          </h3>
          <div className="space-y-2 sm:space-y-3">
            {criticalRuralZones.map((zone) => (
              <div
                key={zone.name}
                className="bg-red-50 border border-red-200 rounded-lg p-3 sm:p-4"
              >
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-bold text-red-900 text-sm sm:text-base">{zone.name} County</h4>
                  <span className="text-xs sm:text-sm font-semibold text-red-700">
                    {(zone.enhanced_vulnerability * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-1.5 sm:gap-2 text-xs sm:text-sm">
                  <div>
                    <span className="text-gray-600">Status:</span>
                    <span className="ml-1 sm:ml-2 font-semibold capitalize">{zone.rural_status.replace('_', ' ')}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">FEMA:</span>
                    <span className="ml-1 sm:ml-2 font-semibold capitalize">{zone.fema_risk_zone}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Home:</span>
                    <span className="ml-1 sm:ml-2 font-semibold">${(zone.median_home_value / 1000).toFixed(0)}K</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Density:</span>
                    <span className="ml-1 sm:ml-2 font-semibold">{zone.population_density}/mi²</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Top 10 Vulnerable Counties - Collapsible */}
      <div>
        <SectionHeader
          title="Top 10 Most Vulnerable Counties"
          isExpanded={expandedSections.topCounties}
          onToggle={() => toggleSection('topCounties')}
        />
        {expandedSections.topCounties && (
          <div className="space-y-1.5 sm:space-y-2 mt-2 sm:mt-3">
          {topCounties.map((county, index) => (
            <div
              key={county.name}
              className="flex items-center justify-between p-2 sm:p-3 bg-gray-50 rounded-lg active:bg-gray-200 sm:hover:bg-gray-100 cursor-pointer transition-colors"
              onClick={() => {
                // Find and select this county
                // This would require passing the full feature, simplified for demo
                console.log('Selected:', county.name);
              }}
            >
              <div className="flex items-center space-x-2 sm:space-x-3">
                <div className="bg-blue-600 text-white rounded-full w-6 h-6 sm:w-8 sm:h-8 flex items-center justify-center font-bold text-xs sm:text-sm">
                  {index + 1}
                </div>
                <div>
                  <p className="font-semibold text-gray-800 text-xs sm:text-sm">{county.name}</p>
                  <p className="text-[10px] sm:text-xs text-gray-500">
                    Pop: {county.population?.toLocaleString()}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-bold text-gray-800 text-xs sm:text-base">
                  {(county.vulnerability_score * 100).toFixed(1)}%
                </p>
                <span className={`px-1.5 sm:px-2 py-0.5 sm:py-1 rounded text-[10px] sm:text-xs font-semibold ${getCategoryColor(county.risk_category)}`}>
                  {county.risk_category}
                </span>
              </div>
            </div>
          ))}
          </div>
        )}
      </div>

      {/* Scatter Plot - Collapsible */}
      <div>
        <SectionHeader
          title="GDP vs Hurricane Risk"
          isExpanded={expandedSections.scatter !== false}
          onToggle={() => toggleSection('scatter')}
        />
        {expandedSections.scatter !== false && (
        <div className="bg-gray-50 rounded-lg p-2 sm:p-4">
          <ResponsiveContainer width="100%" height={250}>
            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                type="number"
                dataKey="gdp"
                name="GDP"
                label={{ value: 'County GDP ($M)', position: 'bottom' }}
                tickFormatter={(value) => `$${(value / 1000).toFixed(0)}B`}
              />
              <YAxis
                type="number"
                dataKey="risk"
                name="Risk"
                label={{ value: 'Hurricane Risk (%)', angle: -90, position: 'left' }}
              />
              <Tooltip
                cursor={{ strokeDasharray: '3 3' }}
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                      <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-200">
                        <p className="font-bold">{data.name}</p>
                        <p className="text-sm">GDP: ${(data.gdp / 1000).toFixed(1)}B</p>
                        <p className="text-sm">Risk: {data.risk.toFixed(1)}%</p>
                        <p className="text-sm">Vulnerability: {data.vulnerability.toFixed(1)}%</p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Scatter data={getScatterData()} fill="#8884d8">
                {getScatterData().map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getScatterColor(entry.category)} />
                ))}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
          <p className="text-xs text-gray-500 mt-2 text-center">
            Bubble color represents vulnerability category
          </p>
        </div>
        )}
      </div>

      {/* Top Property Exposure - Collapsible */}
      {propertyExposure.length > 0 && (
        <div>
          <SectionHeader
            title="Highest Property Value Exposure"
            isExpanded={expandedSections.propertyExposure}
            onToggle={() => toggleSection('propertyExposure')}
          />
          {expandedSections.propertyExposure && (
            <div className="space-y-1.5 sm:space-y-2 mt-2 sm:mt-3">
            {propertyExposure.map((county, index) => (
              <div
                key={county.NAME}
                className="flex items-center justify-between p-2 sm:p-3 bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg"
              >
                <div className="flex items-center space-x-2 sm:space-x-3">
                  <div className="bg-purple-600 text-white rounded-full w-6 h-6 sm:w-8 sm:h-8 flex items-center justify-center font-bold text-xs sm:text-sm">
                    {index + 1}
                  </div>
                  <div>
                    <p className="font-semibold text-gray-800 text-xs sm:text-sm">{county.NAME}</p>
                    <p className="text-[10px] sm:text-xs text-gray-600">
                      Growth: {county.property_growth_rate}% annually
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-bold text-purple-900 text-xs sm:text-base">
                    ${(county.median_home_value / 1000).toFixed(0)}K
                  </p>
                  <p className="text-[10px] sm:text-xs text-gray-600 capitalize">
                    {county.fema_risk_zone} FEMA
                  </p>
                </div>
              </div>
            ))}
            </div>
          )}
        </div>
      )}

      {/* Correlation Analysis - Collapsible */}
      {correlations && (
        <div>
          <SectionHeader
            title="Correlation Analysis"
            isExpanded={expandedSections.correlations}
            onToggle={() => toggleSection('correlations')}
          />
          {expandedSections.correlations && (
            <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-lg p-3 sm:p-4 space-y-2 sm:space-y-3 mt-2 sm:mt-3">
            <div className="flex justify-between items-center">
              <div>
                <p className="font-semibold text-indigo-900 text-xs sm:text-base">GDP vs Vulnerability</p>
                <p className="text-[10px] sm:text-xs text-indigo-600">Higher GDP = Lower Vulnerability</p>
              </div>
              <div className="text-right">
                <p className="text-lg sm:text-2xl font-bold text-indigo-900">
                  {correlations.correlations.gdp_vulnerability.toFixed(3)}
                </p>
              </div>
            </div>
            <div className="h-px bg-indigo-200"></div>
            <div className="flex justify-between items-center">
              <div>
                <p className="font-semibold text-indigo-900 text-xs sm:text-base">Property Value vs Vulnerability</p>
                <p className="text-[10px] sm:text-xs text-indigo-600">Weak correlation</p>
              </div>
              <div className="text-right">
                <p className="text-lg sm:text-2xl font-bold text-indigo-900">
                  {correlations.correlations.property_vulnerability.toFixed(3)}
                </p>
              </div>
            </div>
            <div className="h-px bg-indigo-200"></div>
            <div className="flex justify-between items-center">
              <div>
                <p className="font-semibold text-indigo-900 text-xs sm:text-base">Density vs Vulnerability</p>
                <p className="text-[10px] sm:text-xs text-indigo-600">Higher Density = Lower Vulnerability</p>
              </div>
              <div className="text-right">
                <p className="text-lg sm:text-2xl font-bold text-indigo-900">
                  {correlations.correlations.density_vulnerability.toFixed(3)}
                </p>
              </div>
            </div>
            </div>
          )}
        </div>
      )}

      {/* Data Sources Footer */}
      <div className="text-[10px] sm:text-xs text-gray-500 border-t border-gray-200 pt-3 sm:pt-4">
        <p className="font-semibold mb-1">Data Sources:</p>
        <ul className="space-y-0.5 sm:space-y-1">
          <li>• NOAA Historical Hurricane Tracks</li>
          <li>• CDC Social Vulnerability Index</li>
          <li>• Bureau of Economic Analysis GDP Data</li>
          <li>• US Census Bureau</li>
          <li>• Statista Property Value Data</li>
          <li>• FEMA Risk Zone Classifications</li>
        </ul>
      </div>
    </div>
  );
}
