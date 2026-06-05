# Quick Start Guide

## 5-Minute Setup

### Step 1: Install Dependencies
```bash
cd c:\Users\saiki\biologics_dashboards
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
# Copy example configuration
copy .env.example .env

# The .env already has MongoDB credentials
# (Pre-configured for your setup)
```

### Step 3: Run Dashboard
```bash
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`

## First Launch

When you first run the dashboard:

1. **Database Discovery** (takes 30-60 seconds):
   - Connects to MongoDB
   - Discovers all collections
   - Analyzes schema of each collection
   - Generates data dictionary

2. **Status Indicators**:
   - 🔄 "Discovering database schema..." - In progress
   - ✅ "Connected - X collections" - Complete
   - ❌ "Database connection failed" - Error (check .env)

3. **Sidebar Status**:
   - Expands to show all discovered collections
   - Displays document count for each
   - Shows last updated timestamp

## Navigation

- **Sidebar**: Select theme (Dark/Light) and dashboard page
- **Pages**: 
  - Executive Dashboard - High-level KPIs
  - User Analytics - User engagement metrics
  - Discovery Pipeline - Drug discovery workflow metrics
  - Candidate Intelligence - Top candidates and scoring

## Features to Try

### Executive Dashboard
1. View KPI cards (8 major metrics)
2. Expand date range filter to 90 days
3. Look at Discovery Funnel visualization
4. Download executive summary as CSV

### User Analytics
1. Change time period to "Last 180 days"
2. View Daily Active Users trend
3. Check Activity Heatmap (shows when users are most active)
4. Export user data as CSV

### Discovery Pipeline
1. See complete pipeline metrics (Target → ADMET)
2. Observe Hit Rate and Success Rate metrics
3. View trends for each stage
4. Download pipeline metrics

### Candidate Intelligence
1. View top candidates ranked by score
2. Check ADMET pass rates by property
3. Compare specific candidates
4. Export candidate data

## Troubleshooting

### Dashboard won't start
```bash
# Check Python version (need 3.9+)
python --version

# Try reinstalling dependencies
pip install --upgrade -r requirements.txt

# Check if port 8501 is in use
# Kill the process or use --server.port flag
streamlit run app.py --server.port 8502
```

### No data appears
1. Check MongoDB connection in sidebar
2. Verify collections exist in your database
3. Check that collections have documents
4. Review sidebar "Database Status" section

### Slow performance
1. Reduce date range in filters
2. Close other applications
3. Increase CACHE_TTL in .env
4. Consider scaling MongoDB

## Configuration Tips

### Customize Theme
```env
DEFAULT_THEME=light  # or 'dark'
```

### Adjust Cache Duration
```env
CACHE_TTL=7200  # 2 hours (default is 3600 = 1 hour)
```

### Change Log Level
```env
LOG_LEVEL=DEBUG  # For detailed logs
LOG_LEVEL=WARNING  # For minimal logs
```

### Custom Dashboard Title
```env
DASHBOARD_TITLE="My Custom Dashboard Title"
```

## Common Metrics Explained

- **Active Users (7d)**: Unique users with activity in last 7 days
- **Hit Rate**: Percentage of molecules that showed hits (Hits / Molecules × 100)
- **Success Rate**: Percentage of jobs that completed successfully
- **DAU**: Daily Active Users (unique users per day)
- **MAU**: Monthly Active Users (unique users per month)

## Next Steps

1. ✅ Run `streamlit run app.py`
2. ✅ View Executive Dashboard
3. ✅ Explore other pages
4. ✅ Adjust filters and export data
5. ✅ Customize theme and settings

## Advanced Usage

### Custom Filters
The dashboard supports dynamic filters based on available data:
- Date Range: Adjust start and end dates
- User: Filter by specific user (if data available)
- Project: Filter by project (if data available)
- Status: Filter by status field (Active, Completed, etc.)

### Export Data
Each page offers CSV export of key metrics:
1. Click "📥 Export..." button
2. Click "📥 Download CSV" in popup
3. File saves to Downloads folder

### View Discovered Schema
In sidebar, expand "Database Status" → "View Collections"
Shows all collections with document counts

## System Requirements

- Python 3.9 or higher
- 4GB RAM minimum
- Network access to MongoDB
- Modern web browser

## Performance Tips

- **First load**: Takes 30-60 seconds for schema discovery
- **Subsequent loads**: Much faster due to caching
- **Filters**: Apply date range filters to speed up analytics
- **Export**: Large exports may take a few seconds

## Support

- Check logs in terminal running Streamlit
- Review README.md for detailed documentation
- Check .env configuration
- Verify MongoDB connection

---

**That's it!** You're ready to explore your data. 🎉
