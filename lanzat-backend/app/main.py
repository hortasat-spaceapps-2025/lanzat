"""
Lanzat FastAPI Backend
Hurricane Economic Vulnerability Platform for Florida
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import geopandas as gpd
from pathlib import Path
import json
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Lanzat API",
    description="Hurricane Economic Vulnerability Platform for Florida",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
COUNTIES_FILE = DATA_DIR / "counties.geojson"
SUMMARY_FILE = DATA_DIR / "summary_stats.json"
ENHANCED_COUNTIES_FILE = DATA_DIR / "counties_enhanced.geojson"
ENHANCED_STATS_FILE = DATA_DIR / "enhanced_stats.json"
ACTIVE_STORMS_FILE = DATA_DIR / "active_hurricanes.json"
COUNTY_THREATS_FILE = DATA_DIR / "counties_current_threats.json"


# Helper functions
def load_counties_data():
    """Load pre-processed county vulnerability data"""
    if not COUNTIES_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Counties data not found. Please run data processing script first."
        )

    try:
        # Read GeoJSON directly to avoid Fiona path issues
        with open(COUNTIES_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading counties data: {str(e)}"
        )


def load_summary_stats():
    """Load summary statistics"""
    if not SUMMARY_FILE.exists():
        return None

    try:
        with open(SUMMARY_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load summary stats: {e}")
        return None


# API Routes
@app.get("/")
def root():
    """API root endpoint"""
    return {
        "message": "Lanzat API",
        "version": "0.1.0",
        "documentation": "/docs",
        "endpoints": {
            "counties": "/api/counties",
            "county_detail": "/api/counties/{county_name}",
            "top_vulnerable": "/api/top-vulnerable",
            "stats": "/api/stats",
            "realtime_storms": "/api/realtime/active-storms",
            "realtime_threats": "/api/realtime/county-threats"
        }
    }


@app.get("/api/counties")
def get_counties(include_geometry: bool = True):
    """
    Get all Florida counties with vulnerability scores

    Parameters:
    - include_geometry: Include GeoJSON geometry (default: True)

    Returns GeoJSON FeatureCollection
    """
    data = load_counties_data()

    if not include_geometry:
        # Remove geometry to reduce payload size
        for feature in data.get("features", []):
            feature.pop("geometry", None)

    return JSONResponse(content=data)


@app.get("/api/counties/{county_name}")
def get_county_detail(county_name: str):
    """
    Get detailed information for a specific county

    Parameters:
    - county_name: Name of the county (e.g., "Miami-Dade")
    """
    data = load_counties_data()

    # Find county (case-insensitive)
    county_name_lower = county_name.lower().replace(" county", "").strip()

    for feature in data.get("features", []):
        props = feature.get("properties", {})
        feature_name = props.get("NAME", "").lower()

        if feature_name == county_name_lower or feature_name == county_name_lower + " county":
            return JSONResponse(content={
                "name": props.get("NAME"),
                "vulnerability_score": props.get("vulnerability_score"),
                "hurricane_risk": props.get("hurricane_risk"),
                "gdp": props.get("gdp"),
                "social_vulnerability": props.get("social_vulnerability"),
                "population": props.get("population"),
                "risk_category": props.get("risk_category"),
                "geometry": feature.get("geometry")
            })

    raise HTTPException(
        status_code=404,
        detail=f"County '{county_name}' not found"
    )


@app.get("/api/top-vulnerable")
def get_top_vulnerable(limit: int = 10):
    """
    Get top N most vulnerable counties

    Parameters:
    - limit: Number of counties to return (default: 10, max: 67)
    """
    if limit < 1 or limit > 67:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 67"
        )

    data = load_counties_data()

    # Extract features with scores
    counties = []
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        counties.append({
            "name": props.get("NAME"),
            "vulnerability_score": props.get("vulnerability_score", 0),
            "hurricane_risk": props.get("hurricane_risk"),
            "gdp": props.get("gdp"),
            "social_vulnerability": props.get("social_vulnerability"),
            "population": props.get("population"),
            "risk_category": props.get("risk_category")
        })

    # Sort by vulnerability score (descending)
    counties_sorted = sorted(
        counties,
        key=lambda x: x.get("vulnerability_score", 0),
        reverse=True
    )

    return JSONResponse(content={
        "count": limit,
        "counties": counties_sorted[:limit]
    })


@app.get("/api/stats")
def get_stats():
    """Get summary statistics for all counties"""
    stats = load_summary_stats()

    if not stats:
        # Calculate basic stats from counties data
        data = load_counties_data()
        scores = [
            f.get("properties", {}).get("vulnerability_score", 0)
            for f in data.get("features", [])
        ]

        stats = {
            "total_counties": len(scores),
            "avg_vulnerability": sum(scores) / len(scores) if scores else 0,
            "max_vulnerability": max(scores) if scores else 0,
            "min_vulnerability": min(scores) if scores else 0
        }

    return JSONResponse(content=stats)


@app.get("/health")
def health_check():
    """Health check endpoint for deployment monitoring"""
    data_exists = COUNTIES_FILE.exists()
    enhanced_exists = ENHANCED_COUNTIES_FILE.exists()

    return {
        "status": "healthy" if data_exists else "degraded",
        "data_loaded": data_exists,
        "enhanced_data_loaded": enhanced_exists,
        "counties_file": str(COUNTIES_FILE),
        "summary_file": str(SUMMARY_FILE),
        "enhanced_counties_file": str(ENHANCED_COUNTIES_FILE) if enhanced_exists else None
    }


@app.get("/api/enhanced/counties")
def get_enhanced_counties(include_geometry: bool = True):
    """
    Get enhanced county data with Statista enrichment

    Includes: property values, rural status, FEMA correlation, etc.
    """
    if not ENHANCED_COUNTIES_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Enhanced data not found. Run enrichment script first."
        )

    try:
        with open(ENHANCED_COUNTIES_FILE, 'r') as f:
            data = json.load(f)

        if not include_geometry:
            for feature in data.get("features", []):
                feature.pop("geometry", None)

        return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading enhanced data: {str(e)}"
        )


@app.get("/api/enhanced/stats")
def get_enhanced_stats():
    """Get enhanced statistics with Statista data"""
    if not ENHANCED_STATS_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Enhanced stats not found. Run enrichment script first."
        )

    try:
        with open(ENHANCED_STATS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading enhanced stats: {str(e)}"
        )


@app.get("/api/enhanced/critical-rural")
def get_critical_rural_zones():
    """Get critical rural zones (high vulnerability + rural status)"""
    if not ENHANCED_COUNTIES_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Enhanced data not found."
        )

    try:
        with open(ENHANCED_COUNTIES_FILE, 'r') as f:
            data = json.load(f)

        critical_rural = []
        for feature in data.get("features", []):
            props = feature.get("properties", {})
            if props.get("critical_rural", False):
                critical_rural.append({
                    "name": props.get("NAME"),
                    "enhanced_vulnerability": props.get("enhanced_vulnerability"),
                    "rural_status": props.get("rural_status"),
                    "median_home_value": props.get("median_home_value"),
                    "gdp": props.get("gdp"),
                    "population_density": props.get("population_density"),
                    "fema_risk_zone": props.get("fema_risk_zone")
                })

        return JSONResponse(content={
            "count": len(critical_rural),
            "critical_rural_zones": critical_rural
        })
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading critical rural zones: {str(e)}"
        )


@app.get("/api/enhanced/property-exposure")
def get_property_exposure(limit: int = 10):
    """
    Get counties with highest property value exposure

    Parameters:
    - limit: Number of counties to return (default: 10)
    """
    if not ENHANCED_STATS_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Enhanced stats not found."
        )

    try:
        with open(ENHANCED_STATS_FILE, 'r') as f:
            stats = json.load(f)

        top_exposure = stats.get("top_10_property_exposure", [])[:limit]

        return JSONResponse(content={
            "count": len(top_exposure),
            "top_property_exposure": top_exposure
        })
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading property exposure: {str(e)}"
        )


@app.get("/api/enhanced/correlations")
def get_correlations():
    """Get correlation analysis (GDP, property values, density vs vulnerability)"""
    if not ENHANCED_STATS_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Enhanced stats not found."
        )

    try:
        with open(ENHANCED_STATS_FILE, 'r') as f:
            stats = json.load(f)

        return JSONResponse(content={
            "correlations": stats.get("correlations", {}),
            "interpretation": {
                "gdp_vulnerability": "Negative correlation means higher GDP = lower vulnerability",
                "property_vulnerability": "Correlation between property values and vulnerability",
                "density_vulnerability": "Correlation between population density and vulnerability"
            }
        })
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading correlations: {str(e)}"
        )


# Real-time Hurricane Tracking Endpoints
@app.get("/api/realtime/active-storms")
def get_active_storms():
    """
    Get current active hurricanes and tropical storms from NOAA NHC

    Returns real-time data on active storms including:
    - Storm name, classification, intensity
    - Current position (lat/lon)
    - Wind speed and pressure
    - Last update timestamp
    """
    if not ACTIVE_STORMS_FILE.exists():
        # If no real-time data available yet, return empty result
        return JSONResponse(content={
            "active_storms_count": 0,
            "active_storms": [],
            "last_update": None,
            "message": "No real-time data available. Run fetch_active_hurricanes.py to update."
        })

    try:
        with open(ACTIVE_STORMS_FILE, 'r') as f:
            data = json.load(f)

        return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading active storms data: {str(e)}"
        )


@app.get("/api/realtime/county-threats")
def get_county_threats(threat_level: Optional[str] = None):
    """
    Get county-level threat assessments based on active hurricanes

    Parameters:
    - threat_level: Filter by threat level (extreme/high/moderate/low/none)

    Returns:
    - County name
    - Current threat level
    - Distance to nearest storm
    - Nearest storm details
    - Enhanced vulnerability score
    """
    if not COUNTY_THREATS_FILE.exists():
        return JSONResponse(content={
            "counties": [],
            "message": "No threat assessment data available. Run fetch_active_hurricanes.py to update."
        })

    try:
        with open(COUNTY_THREATS_FILE, 'r') as f:
            threats = json.load(f)

        # Filter by threat level if specified
        if threat_level:
            threat_level_lower = threat_level.lower()
            if threat_level_lower not in ['extreme', 'high', 'moderate', 'low', 'none']:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid threat_level. Must be: extreme, high, moderate, low, or none"
                )

            threats = [t for t in threats if t['current_threat_level'] == threat_level_lower]

        return JSONResponse(content={
            "count": len(threats),
            "counties": threats
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading county threats: {str(e)}"
        )


@app.get("/api/realtime/critical-threats")
def get_critical_threats():
    """
    Get counties with BOTH high current threat AND high vulnerability

    These are the most critical counties requiring immediate attention
    during active hurricane events.

    Criteria:
    - Current threat level: extreme or high
    - Enhanced vulnerability: >= 0.6 (60%)
    """
    if not COUNTY_THREATS_FILE.exists():
        return JSONResponse(content={
            "critical_counties": [],
            "message": "No threat data available."
        })

    try:
        with open(COUNTY_THREATS_FILE, 'r') as f:
            threats = json.load(f)

        # Filter for critical threats
        critical = [
            t for t in threats
            if t['current_threat_level'] in ['extreme', 'high']
            and t.get('enhanced_vulnerability', 0) >= 0.6
        ]

        # Sort by vulnerability (descending)
        critical.sort(key=lambda x: x.get('enhanced_vulnerability', 0), reverse=True)

        return JSONResponse(content={
            "count": len(critical),
            "critical_counties": critical,
            "alert_level": "HIGH" if len(critical) > 0 else "NORMAL"
        })
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading critical threats: {str(e)}"
        )


@app.post("/api/realtime/refresh")
def refresh_realtime_data():
    """
    Trigger refresh of real-time hurricane data

    Executes the fetch_active_hurricanes.py script to update:
    - Active storms from NOAA NHC
    - County threat assessments

    Returns updated summary
    """
    import subprocess

    script_path = BASE_DIR / "scripts" / "fetch_active_hurricanes.py"

    if not script_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Real-time data fetch script not found"
        )

    try:
        # Run the script
        result = subprocess.run(
            ["python", str(script_path)],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Script execution failed: {result.stderr}"
            )

        # Load updated data
        if ACTIVE_STORMS_FILE.exists():
            with open(ACTIVE_STORMS_FILE, 'r') as f:
                data = json.load(f)

            return JSONResponse(content={
                "status": "success",
                "message": "Real-time data refreshed",
                "summary": {
                    "active_storms": data.get("active_storms_count", 0),
                    "counties_under_threat": data.get("counties_under_threat", 0),
                    "last_update": data.get("generated_at")
                }
            })
        else:
            return JSONResponse(content={
                "status": "success",
                "message": "Script executed but no data file generated"
            })

    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=504,
            detail="Real-time data refresh timed out"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error refreshing data: {str(e)}"
        )


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Resource not found", "detail": str(exc)}
    )


@app.exception_handler(500)
async def server_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
