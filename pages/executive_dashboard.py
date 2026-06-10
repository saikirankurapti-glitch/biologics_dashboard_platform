"""
Executive Command Center Dashboard
High-level KPIs and discovery funnel
Refactored to match Stitch professional design system with dark/light themes.
Preserves all MongoDB integrations, filters, calculations, and exports.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import logging
from services.users_service import UsersService
from services.pipeline_service import PipelineService
from utils.charts import ChartBuilder, format_large_number
import utils.ui_components as ui
from database.mongodb import MongoDBOperations

logger = logging.getLogger(__name__)


def render():
    """Render Executive Dashboard"""
    
    theme = st.session_state.theme
    
    # Initialize services
    users_service = UsersService()
    pipeline_service = PipelineService()
    db_ops = MongoDBOperations()
    
    # Fetch filter options from database
    try:
        users_list = db_ops.find("users")
        user_options = ["All Users"] + sorted(list(set(u.get("email") for u in users_list if u.get("email"))))
    except Exception:
        user_options = ["All Users"]
        
    try:
        targets_list = db_ops.find("targets")
        target_ids = set()
        for t in targets_list:
            tid = t.get('target_id') or t.get('name') or str(t.get('_id'))
            target_ids.add(tid)
            
        opt_targets = db_ops.find("optimizations")
        for o in opt_targets:
            tid = o.get('target_id')
            if tid:
                target_ids.add(tid)
                
        project_options = ["All Projects"] + sorted(list(target_ids))
    except Exception:
        project_options = ["All Projects"]
        
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
            user_options,
            label_visibility="collapsed"
        )
    
    with col3:
        project_filter = st.selectbox(
            "Project",
            project_options,
            label_visibility="collapsed"
        )
    
    with col4:
        status_filter = st.selectbox(
            "Status",
            ["All Status", "Active", "Completed", "In Progress"],
            label_visibility="collapsed"
        )
        
    # Map filters
    start_date = None
    end_date = None
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date = datetime.combine(date_range[0], datetime.min.time())
        end_date = datetime.combine(date_range[1], datetime.max.time())
        
    user_email = user_filter if user_filter != "All Users" else None
    target_id = project_filter if project_filter != "All Projects" else None
    status = status_filter if status_filter != "All Status" else None
    
    st.write("---")
    
    # ============ KPI Cards ============
    st.markdown("### Key Performance Indicators")
    
    total_users = users_service.get_total_users(start_date=start_date, end_date=end_date, user_email=user_email)
    active_users = users_service.get_active_users(days=7, start_date=start_date, end_date=end_date, user_email=user_email)
    targets = pipeline_service.get_targets_loaded(start_date=start_date, end_date=end_date, user_email=user_email, target_id=target_id, status=status)
    screening_runs = pipeline_service.get_screening_runs(start_date=start_date, end_date=end_date, user_email=user_email, target_id=target_id, status=status)
    docking_jobs = pipeline_service.get_docking_jobs(start_date=start_date, end_date=end_date, user_email=user_email, target_id=target_id, status=status)
    optimization_jobs = pipeline_service.get_optimization_runs(start_date=start_date, end_date=end_date, user_email=user_email, target_id=target_id, status=status)
    admet_jobs = pipeline_service.get_admet_runs(start_date=start_date, end_date=end_date, user_email=user_email, target_id=target_id, status=status)
    
    try:
        report_query = {}
        if start_date and end_date:
            report_query['created_at'] = {'$gte': start_date, '$lte': end_date}
        if user_email:
            report_query['created_by'] = user_email
        reports = db_ops.count_documents('report_registry', report_query)
    except Exception:
        reports = 0

    kpis = [
        {"title": "Total Users", "value": format_large_number(total_users), "icon": "group", "color": "#00687a"},
        {"title": "Active Users (7d)", "value": format_large_number(active_users), "icon": "bolt", "color": "#3B82F6"},
        {"title": "Targets Analyzed", "value": format_large_number(targets), "icon": "track_changes", "color": "#A855F7"},
        {"title": "Screening Runs", "value": format_large_number(screening_runs), "icon": "science", "color": "#2ca02c"},
        {"title": "Docking Jobs", "value": format_large_number(docking_jobs), "icon": "biotech", "color": "#00687a"},
        {"title": "Optimization Jobs", "value": format_large_number(optimization_jobs), "icon": "settings", "color": "#3B82F6"},
        {"title": "ADMET Predictions", "value": format_large_number(admet_jobs), "icon": "bubble_chart", "color": "#A855F7"},
        {"title": "Reports Generated", "value": format_large_number(reports), "icon": "description", "color": "#2ca02c"}
    ]

    import utils.three_js_renderer as three
    three.render_3d_kpis(kpis, theme)
    
    st.write("---")
    
    # ============ Discovery Funnel ============
    st.markdown("### Discovery Funnel (3D)")
    
    # Gather all 9 stages dynamically
    funnel_query = {}
    if start_date and end_date:
        funnel_query['created_at'] = {'$gte': start_date, '$lte': end_date}
    if user_email:
        funnel_query['created_by'] = user_email
    if target_id and target_id != "All Targets" and target_id != "All Projects":
        funnel_query['target_id'] = target_id

    stages_data = [
        {"stage": "Target Discovery", "count": targets, "description": "Disease-related target identification and annotation."},
        {"stage": "AI Screening", "count": screening_runs, "description": "Virtual screening of compound libraries."},
        {"stage": "Docking", "count": docking_jobs, "description": "Molecular docking and affinity analysis."},
        {"stage": "Lead Optimization", "count": optimization_jobs, "description": "Scaffold optimization and affinity refinement."},
        {"stage": "ADMET", "count": admet_jobs, "description": "Absorption, distribution, metabolism, excretion, and toxicity profiling."},
        {"stage": "Preformulation", "count": db_ops.count_documents('preformulation_reports', funnel_query), "description": "Physical and chemical characterization of active substances."},
        {"stage": "Formulation", "count": db_ops.count_documents('formulation_designs', funnel_query), "description": "Dosage form design and parameter definition."},
        {"stage": "Experiments", "count": db_ops.count_documents('experiments', funnel_query), "description": "Wet-lab experimental validation."},
        {"stage": "Reports", "count": reports, "description": "Final regulatory compliance dossiers and summary reports."}
    ]

    for idx, stage in enumerate(stages_data):
        if idx == 0:
            stage['conversion_rate'] = 100
        else:
            prev_count = stages_data[idx - 1]['count']
            stage['conversion_rate'] = round((stage['count'] / prev_count * 100), 1) if prev_count > 0 else 0.0

    col1, col2 = st.columns([1.2, 2.8])
    with col1:
        stages_df = pd.DataFrame(stages_data)[['stage', 'count', 'conversion_rate']]
        stages_df.columns = ['Stage', 'Count', 'Conversion %']
        st.dataframe(stages_df, use_container_width=True, hide_index=True)
    with col2:
        three.render_3d_funnel(stages_data, theme)
    
    st.write("---")
    
    # ============ Activity Trends ============
    st.markdown("### User Activity Trend")
    
    daily_active = users_service.get_daily_active_users(days=30, start_date=start_date, end_date=end_date, user_email=user_email)
    
    if daily_active:
        dau_df = pd.DataFrame(daily_active)
        try:
            chart_builder = ChartBuilder()
            fig = chart_builder.create_line_chart(
                dau_df,
                'date',
                'user_count',
                "Daily Active Users (DAU) Trend",
                y_label="Active Users",
                theme=theme
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering activity trend: {str(e)}")
            logger.error(f"Activity trend error: {str(e)}")
    else:
        st.info("No activity trend data available")
        
    st.write("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Screening Trend")
        screening_trend = pipeline_service.get_screening_trend(days=30, start_date=start_date, end_date=end_date, user_email=user_email, target_id=target_id, status=status)
        
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
                    theme=theme,
                    height=350
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error rendering screening trend: {str(e)}")
        else:
            st.info("No screening trend data available")
    
    with col2:
        st.markdown("### Research Throughput")
        throughput_metrics = {
            'Targets': targets,
            'Screening': screening_runs,
            'Docking': docking_jobs
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
                theme=theme,
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering throughput chart: {str(e)}")
    
    st.write("---")
    
    # ============ Export Options ============
    st.markdown("### Export Options")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export to CSV"):
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
