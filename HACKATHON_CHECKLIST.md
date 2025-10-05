# Lanzat Hackathon Checklist

**Project:** Florida Hurricane Economic Vulnerability Platform
**Time Available:** 24 hours
**Last Updated:** October 4, 2025

---

## 📋 Pre-Event Setup (Do This Now!)

### Environment Setup
- [ ] Python 3.8+ installed and working
- [ ] Node.js 18+ installed
- [ ] Git configured
- [ ] Code editor ready (VS Code recommended)
- [ ] Install Python dependencies: `pip install -r requirements.txt`

### Accounts & API Keys (Free, No Credit Card)
- [ ] BEA API Key: https://apps.bea.gov/api/signup/
- [ ] Optional: Google Earth Engine (if using satellite data)
- [ ] Optional: Mapbox token (for basemaps)

### Data Pre-Download (Save 30 minutes!)
- [ ] Run `python download_data.py` NOW
- [ ] Download CDC SVI manually: https://www.atsdr.cdc.gov/place-health/php/svi/svi-data-documentation-download.html
- [ ] Download FEMA NRI manually: https://hazards.fema.gov/nri/data-resources
- [ ] Verify all files in `data/` directory: `ls -lh data/`

### Documentation Review
- [ ] Read `QUICK_START.md` (5 min)
- [ ] Bookmark `RESOURCE_GUIDE.md` for reference
- [ ] Understand vulnerability score formula
- [ ] Review sample code snippets

---

## ⏱️ Hour-by-Hour Plan

### HOUR 0-4: Data Foundation ✅

#### Hour 0-1: Data Acquisition
- [ ] **0:00-0:15** - Project setup
  - [ ] Create GitHub repo
  - [ ] Initialize project structure
  - [ ] Install dependencies

- [ ] **0:15-0:45** - Automated downloads
  - [ ] Run `python download_data.py --process`
  - [ ] Verify county boundaries (2 MB)
  - [ ] Verify hurricane tracks (30 MB)
  - [ ] Verify GDP data (3 MB)

- [ ] **0:45-1:00** - Manual downloads
  - [ ] CDC SVI Florida CSV (5 min)
  - [ ] FEMA NRI Florida CSV (10 min)

#### Hour 1-2: Data Processing
- [ ] **1:00-1:15** - Data integration
  - [ ] Run `python integrate_data.py`
  - [ ] Verify output files created
  - [ ] Check for missing data

- [ ] **1:15-1:45** - Data validation
  - [ ] Load `vulnerability_map.geojson` in QGIS/Python
  - [ ] Verify 67 counties present
  - [ ] Check vulnerability scores calculated
  - [ ] Inspect sample county data

- [ ] **1:45-2:00** - Create test dataset
  - [ ] Export top 10 vulnerable counties
  - [ ] Create summary statistics
  - [ ] Document data quirks/issues

#### Hour 2-4: Backend Setup
- [ ] **2:00-2:30** - FastAPI skeleton
  - [ ] Create `backend/main.py`
  - [ ] Setup CORS
  - [ ] Load GeoJSON data
  - [ ] Test server: `uvicorn main:app --reload`

- [ ] **2:30-3:30** - Core API endpoints
  - [ ] `GET /api/counties` - All counties
  - [ ] `GET /api/county/{fips}` - Single county
  - [ ] `GET /api/stats` - Summary stats
  - [ ] `GET /api/top-vulnerable/{n}` - Top N list
  - [ ] Test all endpoints in browser/Postman

- [ ] **3:30-4:00** - API documentation
  - [ ] Add docstrings
  - [ ] Test `/docs` auto-generated docs
  - [ ] Document response formats
  - [ ] Add error handling

---

### HOUR 4-8: Core Functionality 🗺️

#### Hour 4-6: Frontend Foundation
- [ ] **4:00-4:30** - React setup
  - [ ] Create React app: `npm create vite@latest frontend`
  - [ ] Install Leaflet: `npm install leaflet react-leaflet`
  - [ ] Install Recharts: `npm install recharts`
  - [ ] Setup project structure

- [ ] **4:30-5:00** - Basic map
  - [ ] Create `Map/Lanzat.jsx`
  - [ ] Add Leaflet base tiles
  - [ ] Center on Florida (27.6648, -81.5158)
  - [ ] Test map renders

- [ ] **5:00-6:00** - County layer
  - [ ] Fetch data from API
  - [ ] Add GeoJSON layer
  - [ ] Style counties by vulnerability score
  - [ ] Add color legend
  - [ ] Test interactivity

#### Hour 6-8: Interactive Features
- [ ] **6:00-6:30** - County popups
  - [ ] Create popup component
  - [ ] Display: Name, Score, GDP, Risk, SVI
  - [ ] Format numbers (currency, percentages)
  - [ ] Add "View Details" link

- [ ] **6:30-7:00** - Dashboard components
  - [ ] KPI cards (total counties, avg vulnerability, high risk count)
  - [ ] Connect to `/api/stats` endpoint
  - [ ] Basic styling

- [ ] **7:00-8:00** - Top 10 list
  - [ ] Create `TopCountiesList.jsx`
  - [ ] Fetch from `/api/top-vulnerable/10`
  - [ ] Display in table/card format
  - [ ] Add click to zoom on map

---

### HOUR 8-12: Data Visualization 📊

#### Hour 8-10: Charts & Graphs
- [ ] **8:00-9:00** - Scatter plot
  - [ ] GDP vs Vulnerability scatter
  - [ ] Recharts ScatterChart component
  - [ ] Color by risk category
  - [ ] Add tooltips with county names
  - [ ] Bubble size by population (if available)

- [ ] **9:00-10:00** - Additional visualizations
  - [ ] Bar chart: Top 10 vulnerable counties
  - [ ] Pie chart: Risk category distribution
  - [ ] Line chart: Hurricane frequency over time (optional)

#### Hour 10-12: Filtering & Search
- [ ] **10:00-10:30** - Risk level filter
  - [ ] Dropdown: All / Critical / High / Moderate / Low
  - [ ] Update map and dashboard on change
  - [ ] Highlight filtered counties

- [ ] **10:30-11:00** - GDP range filter
  - [ ] Slider: Min/Max GDP
  - [ ] Filter counties by economic size
  - [ ] Update visualizations

- [ ] **11:00-11:30** - County search
  - [ ] Search bar with autocomplete
  - [ ] Zoom to selected county
  - [ ] Show county details panel

- [ ] **11:30-12:00** - Filter combinations
  - [ ] Apply multiple filters
  - [ ] Show result count
  - [ ] Reset filters button

---

### HOUR 12-16: Polish & UX 💅

#### Hour 12-14: Design & Styling
- [ ] **12:00-12:30** - Layout
  - [ ] Responsive grid (map + sidebar)
  - [ ] Mobile breakpoints
  - [ ] Sticky header
  - [ ] Footer with credits

- [ ] **12:30-13:00** - Color scheme
  - [ ] Consistent color palette
  - [ ] Accessibility (WCAG AA)
  - [ ] Dark mode toggle (optional)
  - [ ] Brand colors

- [ ] **13:00-14:00** - Component styling
  - [ ] Cards with shadows
  - [ ] Hover effects
  - [ ] Loading states
  - [ ] Animations (subtle)

#### Hour 14-16: User Experience
- [ ] **14:00-14:30** - Loading states
  - [ ] Skeleton screens for data loading
  - [ ] Spinner for API calls
  - [ ] Progress indicators

- [ ] **14:30-15:00** - Error handling
  - [ ] API error messages
  - [ ] Network error handling
  - [ ] Data validation errors
  - [ ] Graceful degradation

- [ ] **15:00-15:30** - Performance
  - [ ] Lazy load components
  - [ ] Memoize expensive calculations
  - [ ] Optimize re-renders
  - [ ] Bundle size check

- [ ] **15:30-16:00** - Accessibility
  - [ ] Keyboard navigation
  - [ ] ARIA labels
  - [ ] Screen reader testing
  - [ ] Focus management

---

### HOUR 16-20: Advanced Features ⚡

#### Hour 16-17: Data Export
- [ ] **16:00-16:30** - Export functionality
  - [ ] Download filtered data as CSV
  - [ ] Export map as image
  - [ ] Generate PDF report (optional)

- [ ] **16:30-17:00** - Share functionality
  - [ ] Generate shareable URLs with filters
  - [ ] Social media preview cards
  - [ ] Embed code for map (optional)

#### Hour 17-18: Analytics & Insights
- [ ] **17:00-17:30** - Insights panel
  - [ ] Auto-generated insights
  - [ ] "Did you know?" facts
  - [ ] Correlations (GDP vs SVI, etc.)

- [ ] **17:30-18:00** - Comparison tool
  - [ ] Compare 2+ counties side-by-side
  - [ ] Highlight differences
  - [ ] Ranking across metrics

#### Hour 18-20: Testing & Debugging
- [ ] **18:00-18:30** - Unit tests
  - [ ] Test vulnerability score calculation
  - [ ] Test API endpoints
  - [ ] Test React components

- [ ] **18:30-19:00** - Integration tests
  - [ ] E2E test: Load map → Filter → View details
  - [ ] API + Frontend integration
  - [ ] Cross-browser testing

- [ ] **19:00-19:30** - Bug fixes
  - [ ] Fix critical bugs
  - [ ] Improve error handling
  - [ ] Performance optimizations

- [ ] **19:30-20:00** - Final polish
  - [ ] UI tweaks
  - [ ] Content review
  - [ ] Documentation updates

---

### HOUR 20-24: Deployment & Pitch 🚀

#### Hour 20-22: Deployment
- [ ] **20:00-20:30** - Backend deployment
  - [ ] Deploy to Railway/Render
  - [ ] Setup PostgreSQL (if used)
  - [ ] Configure environment variables
  - [ ] Test production API

- [ ] **20:30-21:00** - Frontend deployment
  - [ ] Deploy to Vercel/Netlify
  - [ ] Update API URLs
  - [ ] Test production app
  - [ ] Custom domain (optional)

- [ ] **21:00-21:30** - Integration testing
  - [ ] Test live deployment
  - [ ] Check all features work
  - [ ] Performance audit
  - [ ] Mobile testing

- [ ] **21:30-22:00** - Monitoring setup
  - [ ] Error tracking (Sentry, optional)
  - [ ] Analytics (Plausible, optional)
  - [ ] Health checks

#### Hour 22-24: Pitch Preparation
- [ ] **22:00-22:30** - Pitch deck
  - [ ] Problem statement
  - [ ] Solution overview
  - [ ] Demo walkthrough
  - [ ] Impact & use cases
  - [ ] Technical architecture

- [ ] **22:30-23:00** - Demo video
  - [ ] Record 2-3 minute demo
  - [ ] Highlight key features
  - [ ] Show real insights
  - [ ] Add voiceover/captions

- [ ] **23:00-23:30** - Practice pitch
  - [ ] 3-minute pitch script
  - [ ] 5-minute presentation
  - [ ] Q&A preparation
  - [ ] Backup demo (if live fails)

- [ ] **23:30-24:00** - Final touches
  - [ ] README with screenshots
  - [ ] GitHub repo cleanup
  - [ ] Submit project
  - [ ] Prepare for judging

---

## 🎯 Minimum Viable Product (MVP) Checklist

**Must-Have Features (for submission):**

- [x] **Data Integration**
  - [x] 5 datasets merged (boundaries, hurricanes, GDP, SVI, FEMA)
  - [x] Vulnerability scores calculated
  - [x] GeoJSON output with all metrics

- [ ] **Backend API**
  - [ ] GET all counties
  - [ ] GET single county
  - [ ] GET statistics
  - [ ] CORS enabled

- [ ] **Interactive Map**
  - [ ] Leaflet map centered on Florida
  - [ ] County choropleth by vulnerability
  - [ ] Color legend
  - [ ] County popups with data

- [ ] **Dashboard**
  - [ ] KPI cards (3-5 metrics)
  - [ ] Top 10 vulnerable counties list
  - [ ] At least 1 chart/graph

- [ ] **Deployment**
  - [ ] Backend live and accessible
  - [ ] Frontend deployed
  - [ ] Demo works reliably

**Nice-to-Have Features (if time permits):**

- [ ] Filters (risk level, GDP range)
- [ ] County search
- [ ] Scatter plot visualization
- [ ] Data export (CSV)
- [ ] Mobile responsive
- [ ] Dark mode

---

## 🏆 Judging Criteria Alignment

### Innovation (25%)
- [ ] Unique vulnerability scoring methodology
- [ ] Integration of 5+ diverse datasets
- [ ] Novel insights (GDP × Vulnerability correlation)

### Impact (25%)
- [ ] Real-world use cases documented
- [ ] Emergency management applicability
- [ ] Scalability to other states/hazards

### Technical Execution (25%)
- [ ] Clean, well-structured code
- [ ] Proper data processing pipeline
- [ ] Responsive, accessible UI
- [ ] Deployed and working demo

### Presentation (25%)
- [ ] Clear problem statement
- [ ] Compelling demo
- [ ] Strong narrative
- [ ] Professional delivery

---

## 🚨 Critical Path (Must Complete)

**These tasks MUST be done for a functional demo:**

1. ✅ Data integration script working
2. ✅ Vulnerability scores calculated correctly
3. [ ] API serving county data
4. [ ] Map displaying counties with colors
5. [ ] County popups showing data
6. [ ] Deployment (backend + frontend)
7. [ ] 3-minute pitch prepared

**If short on time, SKIP:**
- Advanced charts (stick to simple visualizations)
- Filters (focus on core map)
- Satellite imagery (MVP doesn't need it)
- Complex database setup (use GeoJSON directly)

---

## 📝 Final Submission Checklist

- [ ] **GitHub Repository**
  - [ ] Code committed and pushed
  - [ ] README with setup instructions
  - [ ] Screenshots/demo GIF
  - [ ] License file

- [ ] **Live Demo**
  - [ ] Backend URL works
  - [ ] Frontend URL works
  - [ ] All features functional
  - [ ] No critical bugs

- [ ] **Documentation**
  - [ ] API documentation
  - [ ] Data sources cited
  - [ ] Architecture diagram
  - [ ] User guide (optional)

- [ ] **Presentation**
  - [ ] Pitch deck (PDF)
  - [ ] Demo video (MP4)
  - [ ] Pitch script practiced
  - [ ] Q&A answers prepared

- [ ] **Submission**
  - [ ] Hackathon platform submission
  - [ ] All required fields filled
  - [ ] Submitted before deadline
  - [ ] Confirmation received

---

## 🎬 Demo Script (3 minutes)

**Minute 1: Problem & Solution**
> "Florida faces increasing hurricane risk. But which communities are MOST vulnerable? We built Lanzat to answer this by combining hurricane risk data, economic data, and social vulnerability metrics into a single score."

**Minute 2: Demo**
> [Show map] "Here's Florida. Counties in red are most vulnerable. [Click Miami-Dade] This popup shows the vulnerability score, GDP, and risk factors. [Show dashboard] Our dashboard highlights the top 10 most vulnerable counties and shows GDP vs vulnerability correlation."

**Minute 3: Impact & Tech**
> "Emergency managers can use this to prioritize resources. [Show filter] We can filter by risk level. [Show export] And export data for planning. We integrated 5 datasets—NOAA hurricanes, BEA economics, CDC social vulnerability, FEMA risk, and Census boundaries—using Python, FastAPI, and React."

**Closing:**
> "Lanzat helps save lives by identifying which communities need help most. Thank you!"

---

## 🔧 Emergency Fixes

**If things go wrong:**

### API Down
- [ ] Use static GeoJSON file in frontend
- [ ] Pre-load all data client-side
- [ ] Skip real-time features

### Deployment Fails
- [ ] Run locally, record demo video
- [ ] Use ngrok to expose local server
- [ ] Share Loom video instead of live demo

### Data Issues
- [ ] Use sample/mock data
- [ ] Reduce to top 20 counties only
- [ ] Simplify vulnerability formula

### Map Not Rendering
- [ ] Fall back to static image
- [ ] Use table view instead
- [ ] Show charts only

---

## 📞 Quick Help Resources

**Stuck on something? Check these first:**

- **Python errors:** `RESOURCE_GUIDE.md` Section 7.1
- **Map not showing:** `QUICK_START.md` Troubleshooting
- **API issues:** FastAPI docs auto-generated at `/docs`
- **Data download fails:** Manual download links in `RESOURCE_GUIDE.md`

**Last Resort:**
- Google the exact error message
- Stack Overflow
- ChatGPT for code fixes
- Team members / mentors

---

**Good luck! You've got this! 🚀🌊💪**

---

**Remember:**
- Save early, save often
- Commit code frequently
- Test each feature before moving on
- Don't over-engineer
- Done > Perfect
- Ship the MVP!
