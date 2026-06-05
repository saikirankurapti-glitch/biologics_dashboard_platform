"""
Executive Command Center Dashboard
High-level KPIs and discovery funnel
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import logging
from services.users_service import UsersService
from services.pipeline_service import PipelineService
from utils.charts import ChartBuilder, format_large_number

logger = logging.getLogger(__name__)


def render():
    """Render Executive Dashboard"""
    
    st.subheader("Executive Command Center")
    
    # Initialize services
    users_service = UsersService()
    pipeline_service = PipelineService()
    
    # ============ Global Filters ============
    st.write("**Filters**")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        date_range = st.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=30), datetime.now()),
            label_visibility="collapsed"
        )
    
    with col2:
        user_filter = st.selectbox(
            "User",
            ["All Users"],
            label_visibility="collapsed"
        )
    
    with col3:
        project_filter = st.selectbox(
            "Project",
            ["All Projects"],
            label_visibility="collapsed"
        )
    
    with col4:
        status_filter = st.selectbox(
            "Status",
            ["All Status", "Active", "Completed", "In Progress"],
            label_visibility="collapsed"
        )
    
    st.write("---")
    
    # ============ KPI Cards ============
    st.subheader("Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_users = users_service.get_total_users()
        st.metric(
            "👥 Total Users",
            format_large_number(total_users),
            delta=None
        )
    
    with col2:
        active_users = users_service.get_active_users(days=7)
        st.metric(
            "⚡ Active Users (7d)",
            format_large_number(active_users),
            delta=None
        )
    
    with col3:
        targets = pipeline_service.get_targets_loaded()
        st.metric(
            "🎯 Targets Analyzed",
            format_large_number(targets),
            delta=None
        )
    
    with col4:
        screening_runs = pipeline_service.get_screening_runs()
        st.metric(
            "🔬 Screening Runs",
            format_large_number(screening_runs),
            delta=None
        )
    
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        docking_jobs = pipeline_service.get_docking_jobs()
        st.metric(
            "🧪 Docking Jobs",
            format_large_number(docking_jobs),
            delta=None
        )
    
    with col6:
        optimization_jobs = pipeline_service.get_optimization_runs()
        st.metric(
            "⚙️ Optimization Jobs",
            format_large_number(optimization_jobs),
            delta=None
        )
    
    with col7:
        admet_jobs = pipeline_service.get_admet_runs()
        st.metric(
            "🧬 ADMET Predictions",
            format_large_number(admet_jobs),
            delta=None
        )
    
    with col8:
        reports = st.session_state.discovery_service.get_collection_count('report_registry')
        st.metric(
            "📊 Reports Generated",
            format_large_number(reports),
            delta=None
        )
    
    st.write("---")
    
    # ============ Discovery Funnel ============
    st.subheader("Discovery Funnel")
    
    funnel_data = pipeline_service.get_discovery_funnel()
    
    if funnel_data:
        funnel_df = pd.DataFrame(funnel_data)
        
        col1, col2 = st.columns([1.5, 2.5])
        
        with col1:
            st.dataframe(funnel_df, use_container_width=True, hide_index=True)
        
        with col2:
            try:
                chart_builder = ChartBuilder()
                fig = chart_builder.create_funnel_chart(
                    funnel_data,
                    "Discovery Pipeline Funnel",
                    theme=st.session_state.theme
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error rendering funnel chart: {str(e)}")
                logger.error(f"Funnel chart error: {str(e)}")
    else:
        st.info("No funnel data available")
    
    st.write("---")
    
    # ============ Activity Trends ============
    st.subheader("User Activity Trend")
    
    daily_active = users_service.get_daily_active_users(days=30)
    
    if daily_active:
        dau_df = pd.DataFrame(daily_active)
        
        try:
            chart_builder = ChartBuilder()
            fig = chart_builder.create_line_chart(
                dau_df,
                'date',
                'user_count',
                "Daily Active Users Trend",
                y_label="Active Users",
                theme=st.session_state.theme
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering activity trend: {str(e)}")
            logger.error(f"Activity trend error: {str(e)}")
    else:
        st.info("No activity trend data available")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Screening Trend")
        screening_trend = pipeline_service.get_screening_trend(days=30)
        
        if screening_trend:
            trend_df = pd.DataFrame(screening_trend)
            try:
                chart_builder = ChartBuilder()
                fig = chart_builder.create_line_chart(
                    trend_df,
                    'date',
                    'count',
                    "Screening Runs Over Time",
                    y_label="Count",
                    theme=st.session_state.theme,
                    height=350
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error rendering screening trend: {str(e)}")
        else:
            st.info("No screening trend data available")
    
    with col2:
        st.subheader("Research Throughput")
        
        # Combine multiple metrics for throughput
        throughput_metrics = {
            'Targets': pipeline_service.get_targets_loaded(),
            'Screening': pipeline_service.get_screening_runs(),
            'Docking': pipeline_service.get_docking_jobs()
        }
        
        throughput_df = pd.DataFrame([throughput_metrics]).T.reset_index()
        throughput_df.columns = ['Module', 'Count']
        
        try:
            chart_builder = ChartBuilder()
            fig = chart_builder.create_bar_chart(
                throughput_df,
                'Module',
                'Count',
                "Research Throughput by Module",
                y_label="Count",
                theme=st.session_state.theme,
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering throughput chart: {str(e)}")
    
    st.write("---")
    
    # ============ Export Options ============
    st.subheader("Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export to CSV"):
            # Create export data
            export_data = {
                'Metric': ['Total Users', 'Active Users', 'Targets', 'Screening Runs',
                          'Docking Jobs', 'Optimization Jobs', 'ADMET Jobs', 'Reports'],
                'Value': [total_users, active_users, targets, screening_runs,
                         docking_jobs, optimization_jobs, admet_jobs, reports]
            }
            export_df = pd.DataFrame(export_data)
            
            csv = export_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"executive_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("🖼️ Export Charts"):
            st.info("Chart export feature available through Plotly's built-in download button on each chart")
