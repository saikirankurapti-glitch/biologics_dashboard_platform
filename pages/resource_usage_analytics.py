"""
Resource Usage & User Engagement Dashboard
Tracks module popularity, user actions, durations, drilldowns, heatmaps, and trends.
Uses the Stitch premium design system.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import logging
from services.resource_usage_service import ResourceUsageService
from utils.charts import ChartBuilder, format_large_number
import utils.ui_components as ui
from database.mongodb import MongoDBOperations

logger = logging.getLogger(__name__)


def render():
    """Render the Resource Usage Analytics Page"""
    theme = st.session_state.theme
    
    # Initialize service and database ops
    db_ops = MongoDBOperations()
    usage_service = st.session_state.get('resource_usage_service')
    if not usage_service:
        usage_service = ResourceUsageService()
        st.session_state.resource_usage_service = usage_service
        
    # Get user list for filters
    try:
        users_list = db_ops.find("users")
        user_options = ["All Users"] + sorted(list(set(u.get("email") for u in users_list if u.get("email"))))
    except Exception:
        user_options = ["All Users"]
        
    # ============ Global Filters ============
    st.write("**Filters**")
    col1, col2 = st.columns(2)
    
    with col1:
        days_range = st.selectbox(
            "Time Period",
            [7, 14, 30, 90, 180],
            format_func=lambda x: f"Last {x} days",
            index=2,  # Default to 30 days
            key="ru_days_range",
            label_visibility="collapsed"
        )
        
    with col2:
        user_filter = st.selectbox(
            "Filter by User",
            user_options,
            key="ru_user_filter",
            label_visibility="collapsed"
        )
        
    start_date = datetime.now() - timedelta(days=days_range)
    end_date = datetime.now()
    user_email = user_filter if user_filter != "All Users" else None
    
    st.write("---")
    
    # ============ KPI Dashboard Section ============
    st.markdown("### Platform Engagement KPIs")
    
    # Fetch KPI metrics
    kpis = usage_service.get_kpis(start_date=start_date, end_date=end_date, user_email=user_email)
    
    # Row 1 KPIs
    col_r1 = st.columns(4)
    with col_r1[0]:
        ui.render_kpi_card("Active Users", format_large_number(kpis["active_users"]), "group", border_color="#00687a", theme=theme)
    with col_r1[1]:
        ui.render_kpi_card("Total Sessions", format_large_number(kpis["sessions"]), "forum", border_color="#3B82F6", theme=theme)
    with col_r1[2]:
        ui.render_kpi_card("Avg Session Duration", f"{kpis['avg_duration']} m", "timer", border_color="#A855F7", theme=theme)
    with col_r1[3]:
        # Formatted total time spent
        total_hours = round(kpis["total_time"] / 60.0, 1)
        ui.render_kpi_card("Total Time On Platform", f"{total_hours} hrs", "schedule", border_color="#2ca02c", theme=theme)
        
    # Row 2 KPIs
    col_r2 = st.columns(4)
    with col_r2[0]:
        ui.render_kpi_card("Most Used Module", kpis["most_used"], "star", border_color="#00687a", theme=theme)
    with col_r2[1]:
        ui.render_kpi_card("Least Used Module", kpis["least_used"], "star_border", border_color="#3B82F6", theme=theme)
    with col_r2[2]:
        ui.render_kpi_card("Reports Generated", format_large_number(kpis["reports"]), "description", border_color="#A855F7", theme=theme)
    with col_r2[3]:
        ui.render_kpi_card("Experiments Run", format_large_number(kpis["experiments"]), "science", border_color="#2ca02c", theme=theme)
        
    st.write("---")
    
    # ============ Module Utilization ============
    st.markdown("### Module Utilization Analysis")
    module_data = usage_service.get_module_usage_metrics(start_date=start_date, end_date=end_date, user_email=user_email)
    
    if module_data:
        module_df = pd.DataFrame(module_data)
        col1, col2 = st.columns([1.2, 1.8])
        
        with col1:
            st.dataframe(
                module_df.rename(columns={
                    'module': 'Module Name',
                    'views': 'Visits',
                    'unique_users_count': 'Unique Users',
                    'time_spent': 'Time Spent (min)'
                }),
                use_container_width=True,
                hide_index=True
            )
            
        with col2:
            try:
                chart_builder = ChartBuilder()
                fig = chart_builder.create_bar_chart(
                    module_df,
                    'module',
                    'views',
                    "Total Visits by Module",
                    y_label="Visits",
                    theme=theme
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error rendering module usage chart: {e}")
    else:
        st.info("No module utilization data available for the selected range.")
        
    st.write("---")
    
    # ============ Usage Trends ============
    st.markdown("### Usage Volume & Engagement Trends")
    
    trend_freq = st.radio(
        "Trend Interval",
        ["Daily", "Weekly", "Monthly"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    frequency_map = {"Daily": "daily", "Weekly": "weekly", "Monthly": "monthly"}
    trend_data = usage_service.get_usage_trends(
        frequency=frequency_map[trend_freq],
        start_date=start_date,
        end_date=end_date,
        user_email=user_email
    )
    
    if trend_data:
        trend_df = pd.DataFrame(trend_data)
        t_col1, t_col2 = st.columns(2)
        
        with t_col1:
            try:
                chart_builder = ChartBuilder()
                fig_views = chart_builder.create_line_chart(
                    trend_df,
                    'period',
                    'views',
                    "Total Visits Over Time",
                    y_label="Visits",
                    theme=theme,
                    height=350
                )
                st.plotly_chart(fig_views, use_container_width=True)
            except Exception as e:
                st.error(f"Error rendering views trend: {e}")
                
        with t_col2:
            try:
                chart_builder = ChartBuilder()
                # Use deep indigo/secondary color for duration
                fig_dur = chart_builder.create_bar_chart(
                    trend_df,
                    'period',
                    'time_spent',
                    "Time Spent Over Time (minutes)",
                    y_label="Duration (min)",
                    theme=theme,
                    height=350
                )
                st.plotly_chart(fig_dur, use_container_width=True)
            except Exception as e:
                st.error(f"Error rendering time spent trend: {e}")
    else:
        st.info("No usage trend data available.")
        
    # ============ 3D Resource Usage Network ============
    st.markdown("### 3D Spatial Resource & Session Network")
    st.caption("Interactive 3D graph mapping active sessions, module transitions, and database/resource access flows.")
    
    import utils.three_js_renderer as three
    three.render_3d_resource_network(kpis, theme)
    
    st.write("---")
    
    # ============ Heatmap and User List ============
    st.markdown("### Platform Load & Activity Distribution")
    
    h_col1, h_col2 = st.columns([1.8, 1.2])
    
    with h_col1:
        st.markdown("#### Hourly Load Distribution Matrix (Day vs Hour)")
        heatmap_data = usage_service.get_heatmap_data(start_date=start_date, end_date=end_date, user_email=user_email)
        
        if not heatmap_data.empty:
            try:
                chart_builder = ChartBuilder()
                fig_heat = chart_builder.create_heatmap(
                    heatmap_data,
                    "Hourly Load Matrix",
                    theme=theme,
                    height=380
                )
                st.plotly_chart(fig_heat, use_container_width=True)
            except Exception as e:
                st.error(f"Error rendering heatmap: {e}")
        else:
            st.info("No heatmap data available.")
            
    with h_col2:
        st.markdown("#### Top Active Users")
        top_users = usage_service.get_user_activity_analysis(start_date=start_date, end_date=end_date, user_email=user_email)
        
        if top_users:
            top_users_df = pd.DataFrame(top_users)
            st.dataframe(
                top_users_df.rename(columns={
                    'user_email': 'User Email',
                    'sessions_count': 'Sessions',
                    'views': 'Visits',
                    'total_time': 'Time On App (min)'
                }),
                use_container_width=True,
                hide_index=True,
                height=380
            )
        else:
            st.info("No top active users data available.")
            
    st.write("---")
    
    # ============ Dynamic Drill-Down Section ============
    st.markdown("### Dynamic Analytics Drill-Downs")
    
    drill_tab1, drill_tab2 = st.tabs(["👤 User Drill-Down", "📦 Resource Drill-Down"])
    
    with drill_tab1:
        # Load all user emails for selection
        selected_user = st.selectbox(
            "Select User to Analyze",
            [u for u in user_options if u != "All Users"],
            key="drill_user_select"
        )
        
        if selected_user:
            user_drill = usage_service.get_user_drilldown(selected_user)
            
            ud_col1, ud_col2 = st.columns(2)
            with ud_col1:
                st.markdown(f"**Engagement Summary for {selected_user}**")
                st.write(f"• **Total Time Spent:** {user_drill['total_time']} minutes")
                
                last_act = user_drill['last_active']
                last_act_str = last_act.strftime('%Y-%m-%d %H:%M:%S') if last_act else "Never"
                st.write(f"• **Last Activity Time:** {last_act_str}")
                
                st.markdown("**Module Engagement Details**")
                if user_drill['modules']:
                    ud_modules_df = pd.DataFrame(user_drill['modules'])
                    st.dataframe(
                        ud_modules_df.rename(columns={
                            'module': 'Module Name',
                            'views': 'Visits',
                            'total_time': 'Time Spent (min)',
                            'last_access': 'Last Access'
                        }),
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No module activity recorded for this user.")
                    
            with ud_col2:
                st.markdown("**Top Accessed Resources**")
                if user_drill['resources']:
                    ud_res_df = pd.DataFrame(user_drill['resources'])
                    st.dataframe(
                        ud_res_df.rename(columns={
                            'resource': 'Resource Name',
                            'views': 'Access Count',
                            'last_access': 'Last Access'
                        }),
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No resource access recorded for this user.")
                    
    with drill_tab2:
        # Fetch resources
        try:
            res_coll = db_ops.connection.get_collection("resource_usage")
            resources_list = sorted(list(set(res_coll.distinct("resource_name"))))
        except Exception:
            resources_list = []
            
        if resources_list:
            selected_res = st.selectbox(
                "Select Resource to Analyze",
                resources_list,
                key="drill_resource_select"
            )
            
            if selected_res:
                res_drill = usage_service.get_resource_drilldown(selected_res)
                
                rd_col1, rd_col2 = st.columns([1, 2])
                with rd_col1:
                    st.markdown(f"**Resource Overview**")
                    st.write(f"• **Resource Identifier:** `{selected_res}`")
                    st.write(f"• **Total View Count:** {res_drill['total_views']}")
                    st.write(f"• **Average View Duration:** {res_drill['avg_duration']} minutes")
                    
                with rd_col2:
                    st.markdown("**User Access History**")
                    if res_drill['users']:
                        rd_users_df = pd.DataFrame(res_drill['users'])
                        st.dataframe(
                            rd_users_df.rename(columns={
                                'user': 'User Email',
                                'views': 'Visits',
                                'total_time': 'Total Time (min)',
                                'last_access': 'Last Access'
                            }),
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.info("No user accesses registered.")
        else:
            st.info("No resource data recorded in the database.")
            
    st.write("---")
    
    # ============ Export Logs & Reports ============
    st.markdown("### Export Logs & Analytics Reports")
    
    exp_col1, exp_col2 = st.columns(2)
    
    with exp_col1:
        if st.button("📥 Export Overview Metrics Summary"):
            export_summary = {
                'Metric': ['Total Active Users', 'Total Sessions', 'Avg Session Duration (min)', 'Total Platform Time (min)',
                           'Most Active Module', 'Least Active Module', 'Reports Generated', 'Experiments Run'],
                'Value': [kpis["active_users"], kpis["sessions"], kpis["avg_duration"], kpis["total_time"],
                          kpis["most_used"], kpis["least_used"], kpis["reports"], kpis["experiments"]]
            }
            export_summary_df = pd.DataFrame(export_summary)
            csv_summary = export_summary_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Summary CSV",
                data=csv_summary,
                file_name=f"resource_analytics_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
    with exp_col2:
        if st.button("📊 Export Filtered Raw Access Logs"):
            query = usage_service._build_query(start_date, end_date, user_email)
            try:
                raw_logs = list(db_ops.find("resource_usage", query))
                if raw_logs:
                    # Clean up _id for export
                    for log in raw_logs:
                        if '_id' in log:
                            log['_id'] = str(log['_id'])
                    raw_df = pd.DataFrame(raw_logs)
                    # Reorder columns logically
                    cols_order = ['user_email', 'module_name', 'resource_name', 'access_time', 'exit_time', 'duration_minutes', 'session_id', 'browser', 'ip_address']
                    cols_present = [c for c in cols_order if c in raw_df.columns]
                    raw_df = raw_df[cols_present]
                    
                    csv_logs = raw_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Raw Logs CSV",
                        data=csv_logs,
                        file_name=f"resource_raw_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No raw log documents found matching the filter.")
            except Exception as e:
                st.error(f"Failed to query raw logs: {e}")
