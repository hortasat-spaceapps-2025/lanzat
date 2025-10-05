# Lanzat Frontend

Interactive map interface for Florida Hurricane Vulnerability Platform

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

```bash
# Create .env.local file
cp .env.example .env.local

# Edit NEXT_PUBLIC_API_URL if backend is not on localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Features

### Interactive Map
- **Choropleth visualization** of all 67 Florida counties
- **Color-coded vulnerability scores** (Critical to Very Low)
- **Click counties** for detailed information
- **Hover effects** for better interactivity
- **OpenStreetMap tiles** (free, no API key required)

### Dashboard
- **Top 10 most vulnerable counties**
- **Summary statistics** (avg, max vulnerability)
- **Selected county details**
- **GDP vs Risk scatter plot**
- **Responsive sidebar**

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel deploy --prod
```

### Environment Variables (Vercel)

```
NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
```

## License

MIT License
