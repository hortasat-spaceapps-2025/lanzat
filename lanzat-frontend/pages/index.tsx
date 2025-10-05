import dynamic from 'next/dynamic';
import Head from 'next/head';
import { useState } from 'react';
import Dashboard from '@/components/Dashboard';
import Header from '@/components/Header';

// Leaflet requires window object, so disable SSR
const Map = dynamic(() => import('@/components/Map'), {
  ssr: false,
  loading: () => (
    <div className="h-full w-full flex items-center justify-center bg-gray-100">
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading map...</p>
      </div>
    </div>
  )
});

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

interface County {
  properties: CountyProperties;
  [key: string]: unknown;
}

export default function Home() {
  const [selectedCounty, setSelectedCounty] = useState<County | null>(null);
  const [showDashboard, setShowDashboard] = useState(true);
  const [mobileView, setMobileView] = useState<'map' | 'dashboard'>('map');

  return (
    <>
      <Head>
        <title>Lanzat - Florida Hurricane Vulnerability Platform</title>
        <meta name="description" content="Hurricane Economic Vulnerability Platform for Florida" />
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="h-screen flex flex-col overflow-hidden">
        <Header />

        {/* Desktop Layout */}
        <div className="flex-1 hidden lg:flex overflow-hidden">
          {/* Map */}
          <div className={`${showDashboard ? 'w-2/3' : 'w-full'} transition-all duration-300`}>
            <Map
              onCountySelect={setSelectedCounty}
              selectedCounty={selectedCounty}
            />
          </div>

          {/* Dashboard */}
          {showDashboard && (
            <div className="w-1/3 border-l border-gray-200 overflow-auto bg-white">
              <Dashboard
                selectedCounty={selectedCounty}
                onCountySelect={setSelectedCounty}
              />
            </div>
          )}

          {/* Toggle Dashboard Button - Desktop */}
          <button
            onClick={() => setShowDashboard(!showDashboard)}
            className="absolute right-4 top-20 bg-white shadow-lg rounded-lg p-3 hover:bg-gray-50 transition-colors z-[1000]"
            title={showDashboard ? 'Hide Dashboard' : 'Show Dashboard'}
          >
            <svg
              className="w-5 h-5 text-gray-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              {showDashboard ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Layout */}
        <div className="flex-1 flex flex-col lg:hidden overflow-hidden">
          {/* Map View */}
          <div className={`${mobileView === 'map' ? 'flex-1' : 'hidden'}`}>
            <Map
              onCountySelect={setSelectedCounty}
              selectedCounty={selectedCounty}
            />
          </div>

          {/* Dashboard View */}
          <div className={`${mobileView === 'dashboard' ? 'flex-1 overflow-auto bg-white' : 'hidden'}`}>
            <Dashboard
              selectedCounty={selectedCounty}
              onCountySelect={setSelectedCounty}
            />
          </div>

          {/* Mobile Navigation Tabs */}
          <div className="flex border-t border-gray-300 bg-white">
            <button
              onClick={() => setMobileView('map')}
              className={`flex-1 py-4 text-center font-semibold transition-colors ${
                mobileView === 'map'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-600 active:bg-gray-100'
              }`}
            >
              <svg className="w-6 h-6 mx-auto mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
              Map
            </button>
            <button
              onClick={() => setMobileView('dashboard')}
              className={`flex-1 py-4 text-center font-semibold transition-colors ${
                mobileView === 'dashboard'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-600 active:bg-gray-100'
              }`}
            >
              <svg className="w-6 h-6 mx-auto mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              Data
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
