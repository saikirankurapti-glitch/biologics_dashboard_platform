"""
Biologics Discovery Platform Analytics Dashboard
Main Streamlit application
"""

import streamlit as st
import logging
from datetime import datetime, timedelta
import config
from services.discovery_service import DiscoveryService

# Configure logging
logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# ============ Page Configuration ============
st.set_page_config(
    page_title=config.DASHBOARD_TITLE,
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ Session State Initialization ============
if 'theme' not in st.session_state:
    st.session_state.theme = config.DEFAULT_THEME

if 'db_discovered' not in st.session_state:
    st.session_state.db_discovered = False

if 'discovery_service' not in st.session_state:
    st.session_state.discovery_service = None

if 'schemas' not in st.session_state:
    st.session_state.schemas = None

# ============ Theme Management ============
def apply_theme(theme: str):
    """Apply theme styling"""
    if theme == 'dark':
        st.markdown("""
        <style>
        :root {
            --primary-color: #1f77b4;
            --secondary-color: #ff7f0e;
            --background-color: #0f0f0f;
            --surface-color: #1a1a1a;
            --text-color: #ffffff;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #1f77b4 0%, #1a5fa0 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            margin: 10px 0;
        }
        
        .metric-value {
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .metric-label {
            font-size: 0.9em;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        :root {
            --primary-color: #1f77b4;
            --secondary-color: #ff7f0e;
            --background-color: #ffffff;
            --surface-color: #f5f5f5;
            --text-color: #000000;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #e8f4f8 0%, #d4e9f7 100%);
            padding: 20px;
            border-radius: 10px;
            color: #1f77b4;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin: 10px 0;
        }
        
        .metric-value {
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .metric-label {
            font-size: 0.9em;
            opacity: 0.8;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        </style>
        """, unsafe_allow_html=True)

apply_theme(st.session_state.theme)

# ============ Sidebar ============
with st.sidebar:
    st.title("🧬 Biologics Platform")
    st.write("---")
    
    # Theme toggle
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌙 Dark"):
            st.session_state.theme = 'dark'
            st.rerun()
    with col2:
        if st.button("☀️ Light"):
            st.session_state.theme = 'light'
            st.rerun()
    
    st.write("---")
    
    # Database status
    st.subheader("Database Status")
    
    if not st.session_state.db_discovered:
        st.info("🔄 Discovering database schema...")
        try:
            discovery_service = DiscoveryService()
            st.session_state.discovery_service = discovery_service
            schemas = discovery_service.discover_all_collections()
            st.session_state.schemas = schemas
            st.session_state.db_discovered = True
            st.success(f"✅ Found {len(schemas)} collections")
            discovery_service.print_discovery_report()
        except Exception as e:
            st.error(
                "❌ Database connection failed. "
                "Please verify your `.env` file and MongoDB access. "
                "If you are running locally, use `mongodb://localhost:27017` as your connection string."
            )
            st.error(f"Error details: {str(e)}")
            logger.error(f"Database discovery error: {str(e)}")
    else:
        if st.session_state.schemas:
            st.success(f"✅ Connected - {len(st.session_state.schemas)} collections")
            with st.expander("View Collections"):
                for coll_name in st.session_state.schemas.keys():
                    row_count = st.session_state.schemas[coll_name].get('document_count', 0)
                    st.write(f"• {coll_name}: {row_count:,} documents")
    
    st.write("---")
    
    # Navigation
    st.subheader("Navigation")
    page = st.radio(
        "Select Page",
        [
            "Executive Dashboard",
            "User Analytics",
            "Discovery Pipeline",
            "Candidate Intelligence"
        ],
        label_visibility="collapsed"
    )

# ============ Main Content ============
st.title(config.DASHBOARD_TITLE)

if not st.session_state.db_discovered or not st.session_state.schemas:
    st.warning("⚠️ Database is not yet discovered. Please check the sidebar.")
    st.stop()

# Import and render appropriate page
if page == "Executive Dashboard":
    from pages import executive_dashboard
    executive_dashboard.render()
elif page == "User Analytics":
    from pages import user_analytics
    user_analytics.render()
elif page == "Discovery Pipeline":
    from pages import discovery_pipeline
    discovery_pipeline.render()
elif page == "Candidate Intelligence":
    from pages import candidate_intelligence
    candidate_intelligence.render()

# Footer
st.write("---")
st.markdown(
    f"<div style='text-align: center; font-size: 0.8em; opacity: 0.6;'>"
    f"Biologics Discovery Platform © 2024 | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    f"</div>",
    unsafe_allow_html=True
)
