"""
Biologics Discovery Platform Analytics Dashboard
Main Streamlit application
"""

import streamlit as st
import logging
from datetime import datetime, timedelta
import config
from services.discovery_service import DiscoveryService
import utils.ui_components as ui

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

if 'current_user_email' not in st.session_state:
    st.session_state.current_user_email = "saikirankurapti@gmail.com"

if 'resource_usage_service' not in st.session_state:
    try:
        from services.resource_usage_service import ResourceUsageService
        st.session_state.resource_usage_service = ResourceUsageService()
    except Exception as e:
        logger.error(f"Failed to initialize ResourceUsageService: {e}")
        st.session_state.resource_usage_service = None

# ============ Theme Management ============
ui.apply_custom_css(st.session_state.theme)

# ============ Sidebar ============
with st.sidebar:
    ui.render_brand_header()
    
    # Navigation Section
    page = st.radio(
        "Select Page",
        [
            "Executive Dashboard",
            "User Analytics",
            "Resource Usage Analytics",
            "Discovery Pipeline",
            "Candidate Intelligence"
        ],
        label_visibility="collapsed"
    )
    
    # Track resource usage page navigation
    if st.session_state.get('resource_usage_service'):
        st.session_state.resource_usage_service.track_page_navigation(page)
    
    st.write("---")
    
    # Action Button
    if st.button("Run Analysis", use_container_width=True, type="primary"):
        st.toast("🧬 Computational drug pipeline analysis started...")
        
    # Theme toggles
    theme_col1, theme_col2 = st.columns(2)
    with theme_col1:
        if st.button("🌙 Dark", use_container_width=True, type="secondary" if st.session_state.theme == "light" else "primary"):
            st.session_state.theme = 'dark'
            st.rerun()
    with theme_col2:
        if st.button("☀️ Light", use_container_width=True, type="secondary" if st.session_state.theme == "dark" else "primary"):
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
            
            # Fetch a real user's full_name
            try:
                from database.mongodb import MongoDBOperations
                db_ops = MongoDBOperations()
                user_doc = db_ops.find_one("users", {"email": "saikirankurapti@gmail.com"})
                if not user_doc:
                    user_doc = db_ops.find_one("users", {})
                if user_doc:
                    st.session_state.current_user_name = user_doc.get("full_name") or "saikiran"
                else:
                    st.session_state.current_user_name = "saikiran"
            except Exception as e:
                st.session_state.current_user_name = "saikiran"
                
            st.success(f"✅ Found {len(schemas)} collections")
            discovery_service.print_discovery_report()
        except Exception as e:
            st.error(
                "❌ Database connection failed. "
                "Please verify your `.env` file and MongoDB access."
            )
            st.error(f"Error details: {str(e)}")
            logger.error(f"Database discovery error: {str(e)}")
    else:
        if st.session_state.schemas:
            st.success(f"✅ Connected ({len(st.session_state.schemas)} collections)")
            with st.expander("View Collections"):
                for coll_name in st.session_state.schemas.keys():
                    row_count = st.session_state.schemas[coll_name].get('document_count', 0)
                    st.write(f"• {coll_name}: {row_count:,} docs")

# ============ Main Content ============
if not st.session_state.db_discovered or not st.session_state.schemas:
    st.warning("⚠️ Database is not yet discovered. Please check the sidebar.")
    st.stop()

# Sticky Top App Bar
ui.render_top_bar(st.session_state.theme, page)

# Import and render appropriate page
if page == "Executive Dashboard":
    from pages import executive_dashboard
    executive_dashboard.render()
elif page == "User Analytics":
    from pages import user_analytics
    user_analytics.render()
elif page == "Resource Usage Analytics":
    from pages import resource_usage_analytics
    resource_usage_analytics.render()
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
    f"Biologics Discovery Platform © 2026 | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    f"</div>",
    unsafe_allow_html=True
)
