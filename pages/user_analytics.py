"""
User Analytics Dashboard
Detailed user activity metrics and departmental breakdown
Refactored to match Stitch professional design system with dark/light themes.
Preserves all MongoDB integrations, filters, calculations, and exports.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import logging
from services.users_service import UsersService
from utils.charts import ChartBuilder, format_large_number
import utils.ui_components as ui
from database.mongodb import MongoDBOperations

logger = logging.getLogger(__name__)


def render():
    """Render User Analytics Dashboard"""
    
    theme = st.session_state.theme
    
    # Initialize service
    users_service = UsersService()
    db_ops = MongoDBOperations()
    
    # Fetch filter options from database
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
            index=2, # Default to 30 days
            label_visibility="collapsed"
        )
    
    with col2:
        user_filter = st.selectbox(
            "User Selection",
            user_options,
            label_visibility="collapsed"
        )
        
    # Map filters
    start_date = datetime.now() - timedelta(days=days_range)
    end_date = datetime.now()
    user_email = user_filter if user_filter != "All Users" else None
    
    st.write("---")
    
    # ============ KPI Cards ============
    st.markdown("### User Metrics Summary")
    metric_cols = st.columns(5)
    
    total_users = users_service.get_total_users(start_date=start_date, end_date=end_date, user_email=user_email)
    new_users = users_service.get_new_users(days=days_range, start_date=start_date, end_date=end_date, user_email=user_email)
    daily_active = users_service.get_active_users(days=1, start_date=datetime.now() - timedelta(days=1), end_date=end_date, user_email=user_email)
    
    try:
        monthly_active_data = users_service.get_monthly_active_users(months=1, start_date=datetime.now() - timedelta(days=30), end_date=end_date, user_email=user_email)
        monthly_active = monthly_active_data[0]['user_count'] if monthly_active_data else 0
    except Exception:
        monthly_active = users_service.get_active_users(days=30, start_date=datetime.now() - timedelta(days=30), end_date=end_date, user_email=user_email)
        
    session_count = users_service.get_session_count(days=days_range, start_date=start_date, end_date=end_date, user_email=user_email)
    
    with metric_cols[0]:
        ui.render_kpi_card("Total Users", format_large_number(total_users), "group", border_color="#00687a", theme=theme)
    with metric_cols[1]:
        ui.render_kpi_card("New Users", format_large_number(new_users), "person_add", border_color="#3B82F6", theme=theme)
    with metric_cols[2]:
        ui.render_kpi_card("Daily Active (DAU)", format_large_number(daily_active), "bolt", border_color="#A855F7", theme=theme)
    with metric_cols[3]:
        ui.render_kpi_card("Monthly Active (MAU)", format_large_number(monthly_active), "trending_up", border_color="#2ca02c", theme=theme)
    with metric_cols[4]:
        ui.render_kpi_card("Sessions Count", format_large_number(session_count), "forum", border_color="#312E81", theme=theme)
        
    st.write("---")
    
    # ============ Active Users Trend ============
    st.markdown("### Daily Active Users Trend")
    dau_data = users_service.get_daily_active_users(days=days_range, start_date=start_date, end_date=end_date, user_email=user_email)
    
    if dau_data:
        dau_df = pd.DataFrame(dau_data)
        try:
            chart_builder = ChartBuilder()
            fig = chart_builder.create_line_chart(
                dau_df,
                'date',
                'user_count',
                "Daily Active Users",
                y_label="Active Users",
                theme=theme
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering DAU trend: {str(e)}")
    else:
        st.info("No daily active users data available")
        
    st.write("---")
    
    # ============ Monthly Active Users Trend ============
    st.markdown("### Monthly Active Users Trend")
    mau_data = users_service.get_monthly_active_users(months=6, user_email=user_email)
    
    if mau_data:
        mau_df = pd.DataFrame(mau_data)
        try:
            chart_builder = ChartBuilder()
            fig = chart_builder.create_line_chart(
                mau_df,
                'month',
                'user_count',
                "Monthly Active Users",
                y_label="Active Users",
                theme=theme
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering MAU trend: {str(e)}")
    else:
        st.info("No monthly active users data available")
        
    st.write("---")
    
    # ============ Top Active Users ============
    st.markdown("### Top Active Users")
    top_users = users_service.get_top_active_users(limit=10, start_date=start_date, end_date=end_date, user_email=user_email)
    
    if top_users:
        top_users_df = pd.DataFrame(top_users)
        col1, col2 = st.columns([1, 1.5])
        
        with col1:
            st.dataframe(top_users_df, use_container_width=True, hide_index=True)
            
        with col2:
            try:
                chart_builder = ChartBuilder()
                fig = chart_builder.create_bar_chart(
                    top_users_df.head(10),
                    'user_id',
                    'activity_count',
                    "Top 10 Active Users",
                    y_label="Activity Count",
                    theme=theme,
                    orientation='h'
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error rendering top users chart: {str(e)}")
    else:
        st.info("No top active users data available")
        
    st.write("---")
    
    # ============ Department Usage (3D User Clustering) ============
    st.markdown("### 3D User Clustering Environment")
    st.caption("Visualizing platform user interaction clusters force-directed by department.")
    
    cluster_users = []
    for u in users_list:
        cluster_users.append({
            "email": u.get("email") or u.get("user_id") or "unknown@biologics.com",
            "department": u.get("department") or "Discovery",
            "role": u.get("role") or "Scientist",
            "activity_count": u.get("activity_count") or u.get("views") or int(u.get("login_count") or 1) * 5
        })
        
    if cluster_users:
        import utils.three_js_renderer as three
        three.render_3d_user_clustering(cluster_users, theme)
    else:
        st.info("No user clustering data available")
        
    st.write("---")
    
    # ============ Activity Heatmap ============
    st.markdown("### User Activity Heatmap (Day of Week vs Hour)")
    heatmap_data = users_service.get_activity_heatmap_data(days=days_range, start_date=start_date, end_date=end_date, user_email=user_email)
    
    if not heatmap_data.empty:
        try:
            chart_builder = ChartBuilder()
            fig = chart_builder.create_heatmap(
                heatmap_data,
                "User Activity Intensity Matrix",
                theme=theme,
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering heatmap: {str(e)}")
    else:
        st.info("No heatmap data available")
        
    st.write("---")
    
    # ============ Login Trend ============
    st.markdown("### Login Success Rate Trend")
    login_trend = users_service.get_login_trend(days=days_range, start_date=start_date, end_date=end_date, user_email=user_email)
    
    if login_trend:
        login_df = pd.DataFrame(login_trend)
        try:
            chart_builder = ChartBuilder()
            fig = chart_builder.create_line_chart(
                login_df,
                'date',
                'logins',
                "Daily System Logins",
                y_label="Login Count",
                theme=theme
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering login trend: {str(e)}")
    else:
        st.info("No login trend data available")
        
    st.write("---")
    
    # ============ Export Options ============
    st.markdown("### Export Options")
    if st.button("📥 Export User Directory Summary"):
        export_data = {
            'Metric': ['Total Users', 'New Users', 'Daily Active', 'Monthly Active', 'Session Count'],
            'Value': [total_users, new_users, daily_active, monthly_active, session_count]
        }
        export_df = pd.DataFrame(export_data)
        csv = export_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"user_analytics_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
