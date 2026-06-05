# Biologics Discovery Platform Analytics Dashboard

A production-quality analytics dashboard for the Biologics Discovery Platform built with Python, Streamlit, MongoDB, Pandas, and Plotly.

## Overview

This dashboard provides comprehensive analytics and monitoring for drug discovery workflows, including:

- **Executive Command Center**: High-level KPIs and discovery pipeline metrics
- **User Analytics**: User engagement, activity trends, and departmental usage
- **Discovery Pipeline**: Target analysis, screening, docking, optimization, and ADMET metrics
- **Candidate Intelligence**: Candidate ranking, scoring, and ADMET analysis

## Features

### 🚀 Technical Highlights

- **Dynamic Schema Discovery**: Automatically detects MongoDB collections and schema
- **Read-Only Operations**: Secure, no data modification capabilities
- **Enterprise UI**: Dark/Light theme, responsive design, professional styling
- **Advanced Analytics**: Aggregation pipelines, trend analysis, and quality metrics
- **Export Capabilities**: CSV and chart download options
- **Error Handling**: Comprehensive logging and error management
- **Performance Optimization**: Caching and efficient database queries

### 📊 Dashboard Pages

#### Page 1: Executive Command Center
- **KPIs**: Total Users, Active Users, Targets, Screening Runs, Docking Jobs, Optimization Jobs, ADMET Predictions, Reports
- **Visualizations**: 
  - User Activity Trend (line chart)
  - Discovery Funnel (funnel chart)
  - Research Throughput (bar chart)
- **Filters**: Date range, User, Project, Status, Module

#### Page 2: User Analytics
- **KPIs**: Total Users, New Users, Daily Active Users, Monthly Active Users, Session Count
- **Visualizations**:
  - Daily Active Users Trend
  - Monthly Active Users Trend
  - Top Active Users (bar chart)
  - Department Usage (bar chart)
  - Activity Heatmap (day of week vs hour)
  - Login Trend

#### Page 3: Discovery Pipeline
- **Target Metrics**: Targets Loaded, Unique Proteins
- **Screening Metrics**: Runs, Molecules Screened, Hits Identified, Hit Rate
- **Docking Metrics**: Jobs, Success Rate, Average Binding Energy
- **Optimization Metrics**: Runs, Leads Generated
- **ADMET Metrics**: Runs, Success Rate
- **Visualizations**: Trends for each stage, Pipeline funnel

#### Page 4: Candidate Intelligence
- **KPIs**: Optimization Runs, Leads Generated, Best Candidate Score, ADMET Success %
- **Visualizations**:
  - Candidate Ranking Table
  - Top 5 Candidates
  - Optimization Score Distribution
  - ADMET Pass Rate by Property
  - Candidate Comparison Tool

## Project Structure

```
biologics_dashboard/
│
├── app.py                          # Main Streamlit application
├── config.py                       # Configuration and environment variables
├── requirements.txt                # Python dependencies
├── .env.example                    # Example environment variables
│
├── database/
│   └── mongodb.py                  # MongoDB connection and operations
│
├── services/
│   ├── discovery_service.py       # Database schema discovery
│   ├── users_service.py           # User analytics metrics
│   ├── pipeline_service.py        # Discovery pipeline metrics
│   └── candidate_service.py       # Candidate intelligence metrics
│
├── pages/
│   ├── executive_dashboard.py     # Executive dashboard page
│   ├── user_analytics.py          # User analytics page
│   ├── discovery_pipeline.py      # Pipeline metrics page
│   └── candidate_intelligence.py  # Candidate intelligence page
│
├── utils/
│   ├── schema_analyzer.py         # MongoDB schema analysis
│   ├── metrics.py                 # Metric calculations
│   └── charts.py                  # Plotly chart builders
│
└── assets/                         # Static assets (icons, logos)
```

## Installation

### Prerequisites

- Python 3.9+
- MongoDB Atlas account or local MongoDB instance
- pip or conda

### Setup Steps

1. **Clone repository**
   ```bash
   cd c:\Users\saiki\biologics_dashboards
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   copy .env.example .env
   ```

   Edit `.env` with your MongoDB credentials:
   ```
   MONGODB_URL=mongodb+srv://quantxai25_db_user:2Xj4kePUqLqoIZcm@cluster0.qyzjacn.mongodb.net/?appName=Cluster0
   DATABASE_NAME=biologics_platform
   DEFAULT_THEME=dark
   ```

5. **Run the dashboard**
   ```bash
   streamlit run app.py
   ```

   The dashboard will open in your browser at `http://localhost:8501`

## Configuration

### Environment Variables

```env
# MongoDB Configuration
MONGODB_URL=mongodb+srv://user:password@cluster.mongodb.net/?appName=Cluster0
DATABASE_NAME=biologics_platform

# API Keys
RESEND_API_KEY=your_api_key_here

# Dashboard Configuration
DASHBOARD_TITLE=Biologics Discovery Platform Analytics
DEFAULT_THEME=dark  # or 'light'
CACHE_TTL=3600     # Cache duration in seconds
LOG_LEVEL=INFO     # DEBUG, INFO, WARNING, ERROR
```

### Theme Configuration

The dashboard supports two themes:

- **Dark Theme** (default): Professional, suitable for extended use
- **Light Theme**: High contrast, suitable for presentations

Toggle themes using the buttons in the sidebar.

## Database Discovery

The dashboard automatically discovers the MongoDB schema on startup:

1. **Connects** to MongoDB using credentials from environment variables
2. **Lists** all collections in the database
3. **Analyzes** each collection:
   - Document count
   - Field names and data types
   - Null percentages
   - Unique value counts
   - Detects date fields, status fields, and ID fields
4. **Generates** comprehensive data dictionary
5. **Detects** potential relationships between collections

### Collections Expected

- `users` - User profiles and metadata
- `user_activities` - User action logs
- `access_logs` - System access records
- `targets` - Drug targets and proteins
- `screenings` - Virtual screening runs
- `docking_jobs` - Molecular docking simulations
- `optimizations` - Lead optimization runs
- `admet_jobs` - ADMET predictions
- `preformulation_reports` - Formulation data
- `formulation_designs` - Design parameters
- `experiments` - Experimental records
- `report_registry` - Generated reports catalog

**Note**: The dashboard dynamically discovers collections. If a collection exists but is empty or has unexpected schema, metrics will gracefully handle the absence of data.

## Usage Guide

### Navigating the Dashboard

1. **Select Theme**: Use the theme buttons in the sidebar to toggle between dark and light modes
2. **View Collections**: Expand "Database Status" in sidebar to see discovered collections
3. **Select Page**: Use the radio buttons to navigate between dashboard pages
4. **Apply Filters**: Use global filters to narrow down data by date, user, project, or status
5. **Export Data**: Download metric summaries as CSV or charts as PNG

### KPI Cards

Each KPI card displays:
- **Metric Name**: Clear, descriptive label with icon
- **Value**: Current metric value with formatting (K for thousands, M for millions)
- **Delta**: Change indicator (optional, when historical data available)

### Charts and Visualizations

All charts include:
- **Interactive Elements**: Hover for detailed values
- **Download Button**: Export as PNG using Plotly's toolbar
- **Responsive Design**: Adapts to sidebar collapse/expand

### Filters

Global filters are available on each page:
- **Date Range**: Select custom date intervals
- **User Filter**: Focus on specific user or all users
- **Project Filter**: Filter by research project
- **Status Filter**: Show only specific statuses (Active, Completed, etc.)
- **Module Filter**: Filter by discovery pipeline stage

## API Reference

### Discovery Service

```python
from services.discovery_service import DiscoveryService

discovery = DiscoveryService()

# Discover all collections
schemas = discovery.discover_all_collections()

# Get schema for specific collection
schema = discovery.get_collection_schema('users')

# Get available collections
collections = discovery.get_available_collections()

# Get data dictionary
data_dict = discovery.get_data_dictionary()
```

### Users Service

```python
from services.users_service import UsersService

users = UsersService()

# Get metrics
total_users = users.get_total_users()
active_users = users.get_active_users(days=7)
new_users = users.get_new_users(days=30)

# Get trends
dau = users.get_daily_active_users(days=30)
mau = users.get_monthly_active_users(months=6)

# Get analytics
top_users = users.get_top_active_users(limit=10)
dept_usage = users.get_user_department_usage()
heatmap = users.get_activity_heatmap_data(days=30)
```

### Pipeline Service

```python
from services.pipeline_service import PipelineService

pipeline = PipelineService()

# Target metrics
targets = pipeline.get_targets_loaded()
proteins = pipeline.get_unique_proteins()

# Screening metrics
runs = pipeline.get_screening_runs()
molecules = pipeline.get_molecules_screened()
hits = pipeline.get_hits_identified()
hit_rate = pipeline.get_hit_rate()

# Docking metrics
jobs = pipeline.get_docking_jobs()
success_rate = pipeline.get_docking_success_rate()
binding_energy = pipeline.get_average_binding_energy()

# Pipeline funnel
funnel = pipeline.get_discovery_funnel()
```

### Candidate Service

```python
from services.candidate_service import CandidateService

candidate = CandidateService()

# Get metrics
candidates = candidate.get_candidate_ranking(limit=20)
top = candidate.get_top_candidates(limit=5)
best_score = candidate.get_best_candidate_score()

# Get distributions
score_dist = candidate.get_optimization_score_distribution()
admet_rates = candidate.get_admet_pass_rate()

# Compare candidates
comparison = candidate.get_candidate_comparison(['cand1', 'cand2'])
```

## Metrics Explained

### User Metrics

- **Total Users**: Sum of all user documents
- **Active Users**: Distinct users with activity in last N days
- **New Users**: Users created in last N days
- **Daily Active Users (DAU)**: Daily count of unique active users
- **Monthly Active Users (MAU)**: Monthly count of unique active users
- **Session Count**: Total user activity records

### Pipeline Metrics

- **Hit Rate**: (Hits / Molecules Screened) × 100
- **Success Rate**: (Successful Jobs / Total Jobs) × 100
- **Conversion Rate**: (Stage Count / Previous Stage Count) × 100
- **Average Binding Energy**: Mean binding energy across docking results

### Candidate Metrics

- **Candidate Score**: Optimization score (0-100)
- **ADMET Success Rate**: Percentage of ADMET predictions that pass
- **Quality Metrics**: Average, max, and min scores for candidate set

## Database Queries

All queries use MongoDB aggregation pipelines for performance:

```python
# Example: Get daily active users
pipeline = [
    {'$match': {'timestamp': {'$gte': cutoff_date}}},
    {'$group': {'_id': '$date', 'active_users': {'$addToSet': '$user_id'}}},
    {'$project': {'date': '$_id', 'user_count': {'$size': '$active_users'}}},
    {'$sort': {'date': 1}}
]
```

### Read-Only Operations

The dashboard uses only read-only MongoDB operations:

- `find()` - Retrieve documents
- `find_one()` - Retrieve single document
- `aggregate()` - Process with aggregation pipeline
- `count_documents()` - Count matching documents

**Explicitly forbidden write operations:**
- insert_one, insert_many
- update_one, update_many
- delete_one, delete_many
- replace_one, drop

## Performance Optimization

### Caching

The dashboard implements caching for:

- **Schema discovery**: Cached at application startup
- **Collections list**: Cached for session duration
- **Metric calculations**: Default TTL of 1 hour (configurable)

To adjust cache duration:

```env
CACHE_TTL=7200  # 2 hours
```

### Query Optimization

- Uses MongoDB aggregation pipelines instead of client-side processing
- Limits data retrieval with `$limit` stages
- Groups data efficiently with `$group` stage
- Indexes utilized through connection parameters

### Database Connection

- Single connection instance (singleton pattern)
- Connection pooling configured in PyMongo
- Server selection timeout: 5 seconds
- Connect timeout: 10 seconds

## Error Handling

The dashboard includes comprehensive error handling:

1. **Connection Errors**: Graceful fallback with error messages
2. **Missing Collections**: Metrics return 0 or empty data
3. **Schema Mismatches**: Flexible field detection
4. **Null Values**: Handled in aggregations and calculations
5. **Logging**: All errors logged with context

View logs in the terminal running Streamlit.

## Troubleshooting

### Connection Issues

**Error**: `Failed to connect to MongoDB`

**Solution**:
1. Verify `MONGODB_URL` in `.env`
2. Check MongoDB Atlas IP whitelist
3. Ensure credentials are correct
4. Test connection with MongoDB Compass

### No Data Displayed

**Error**: "No data available" for specific metric

**Possible Causes**:
- Collection is empty
- Field names don't match expectations
- Date range has no data

**Solution**:
- Check collection schemas in sidebar
- Verify field names match your database
- Expand date range filters

### Slow Dashboard Performance

**Solution**:
1. Increase `CACHE_TTL` for less frequent updates
2. Reduce date range in trends
3. Limit number of top records displayed
4. Check MongoDB query logs

## Production Deployment

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
```

Build and run:

```bash
docker build -t biologics-dashboard .
docker run -e MONGODB_URL=<url> -p 8501:8501 biologics-dashboard
```

### Cloud Deployment (Streamlit Cloud)

1. Push to GitHub repository
2. Connect to Streamlit Cloud
3. Configure environment variables in Settings
4. Deploy

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name dashboard.example.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Security Considerations

1. **Credentials**: Never commit `.env` file with credentials
2. **Database Access**: Use read-only MongoDB users for production
3. **Network**: Ensure MongoDB is not publicly accessible
4. **HTTPS**: Deploy behind HTTPS in production
5. **Authentication**: Consider adding Streamlit authentication layer

## Contributing

### Adding New Metrics

1. Add metric calculation to appropriate service
2. Create KPI card in dashboard page
3. Add visualization using ChartBuilder
4. Document in README

### Adding New Charts

1. Extend `ChartBuilder` class in `utils/charts.py`
2. Use Plotly for consistency
3. Support both dark and light themes
4. Test responsiveness

## Monitoring and Maintenance

### Regular Tasks

- Check MongoDB connection logs
- Monitor dashboard performance
- Review metric calculations for accuracy
- Update dependencies monthly

### Logging

Check logs for:
```
[Collection Name] - Analysis complete
[Metric] - Calculation successful
Error messages with timestamps
```

## Support and Resources

- **Streamlit Docs**: https://docs.streamlit.io/
- **Plotly Docs**: https://plotly.com/python/
- **PyMongo Docs**: https://pymongo.readthedocs.io/
- **MongoDB Docs**: https://docs.mongodb.com/

## License

Proprietary - Biologics Discovery Platform

## Version History

### v1.0.0 (2024)

- Initial release
- 4 dashboard pages
- 50+ KPIs and metrics
- Schema discovery
- Multi-theme support
- Export functionality
- Comprehensive documentation

## Authors

Biologics Platform Analytics Team

---

**Last Updated**: June 2024

For questions or issues, please contact the platform team.
