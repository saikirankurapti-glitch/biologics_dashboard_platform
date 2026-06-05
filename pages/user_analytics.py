"""
User Analytics Dashboard
User engagement, activity, and demographics
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import logging
from services.users_service import UsersService
from utils.charts import ChartBuilder, format_large_number

logger = logging.getLogger(__name__)


def render():
    """Render User Analytics Dashboard"""
    
    st.subheader("User Analytics")
    
    # Initialize service
    users_service = UsersService()
    
    # ============ Global Filters ============
    st.write("**Filters**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        days_range = st.selectbox(
            "Time Period",
            [7, 14, 30, 90, 180],
            format_func=lambda x: f"Last {x} days",
            label_visibility="collapsed"
        )
    
    with col2:
        activity_type = st.selectbox(
            "Activity Type",
            ["All Activities", "Login", "Data Access", "Analysis"],
            label_visibility="collapsed"
        )
    
    with col3:
        department = st.selectbox(
            "Department",
            ["All Departments"],
            label_visibility="collapsed"
        )
    
    st.write("---")
    
    # ============ KPI Cards ============
    st.subheader("User Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_users = users_service.get_total_users()
        st.metric(
            "👥 Total Users",
            format_large_number(total_users),
            delta=None
        )
    
    with col2:
        new_users = users_service.get_new_users(days=days_range)
        st.metric(
            "🆕 New Users",
            format_large_number(new_users),
            delta=None
        )
    
    with col3:
        daily_active = users_service.get_active_users(days=1)
        st.metric(
            "📊 Daily Active Users",
            format_large_number(daily_active),
            delta=None
        )
    
    with col4:
        try:
            monthly_active_data = users_service.get_monthly_active_users(months=1)
            monthly_active = monthly_active_data[0]['user_count'] if monthly_active_data else 0
        except:
            monthly_active = users_service.get_active_users(days=30)
        
        st.metric(
            "📈 Monthly Active Users",
            format_large_number(monthly_active),
            delta=None
        )
    
    with col5:
        session_count = users_service.get_session_count(days=days_range)
        st.metric(
            "💬 Session Count",
            format_large_number(session_count),
            delta=None
        )
    
    st.write("---")
    
    # ============ Daily Active Users Trend ============
    st.subheader("Daily Active Users Trend")
    
    dau_data = users_service.get_daily_active_users(days=days_range)
    
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
                theme=st.session_state.theme
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering DAU trend: {str(e)}")
            logger.error(f"DAU trend error: {str(e)}")
    else:
        st.info("No daily active users data available")
    
    st.write("---")
    
    # ============ Monthly Active Users Trend ============
    st.subheader("Monthly Active Users Trend")
    
    mau_data = users_service.get_monthly_active_users(months=6)
    
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
                theme=st.session_state.theme
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering MAU trend: {str(e)}")
            logger.error(f"MAU trend error: {str(e)}")
    else:
        st.info("No monthly active users data available")
    
    st.write("---")
    
    # ============ Top Active Users ============
    st.subheader("Top Active Users")
    
    top_users = users_service.get_top_active_users(limit=10)
    
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
                    theme=st.session_state.theme,
                    orientation='h'
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error rendering top users chart: {str(e)}")
    else:
        st.info("No top users data available")
    
    st.write("---")
    
    # ============ Department Usage ============
    st.subheader("Department Usage")
    
    dept_usage = users_service.get_user_department_usage(limit=10)
    
    if dept_usage:
        dept_df = pd.DataFrame(dept_usage)
        
        col1, col2 = st.columns([1, 1.5])
        
        with col1:
            st.dataframe(dept_df, use_container_width=True, hide_index=True)
        
        with col2:
            try:
                chart_builder = ChartBuilder()
                fig = chart_builder.create_bar_chart(
                    dept_df,
                    'department',
                    'activity_count',
                    "Department Activity",
                    y_label="Activity Count",
                    theme=st.session_state.theme
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error rendering department chart: {str(e)}")
    else:
        st.info("No department usage data available")
    
    st.write("---")
    
    # ============ Activity Heatmap ============
    st.subheader("Activity Heatmap (Day of Week vs Hour)")
    
    heatmap_data = users_service.get_activity_heatmap_data(days=days_range)
    
    if not heatmap_data.empty:
        try:
            chart_builder = ChartBuilder()
            fig = chart_builder.create_heatmap(
                heatmap_data,
                "User Activity Heatmap",
                theme=st.session_state.theme,
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering heatmap: {str(e)}")
    else:
        st.info("No heatmap data available")
    
    st.write("---")
    
    # ============ Login Trend ============
    st.subheader("Login Trend")
    
    login_trend = users_service.get_login_trend(days=days_range)
    
    if login_trend:
        login_df = pd.DataFrame(login_trend)
        
        try:
            chart_builder = ChartBuilder()
            fig = chart_builder.create_line_chart(
                login_df,
                'date',
                'logins',
                "Daily Logins",
                y_label="Login Count",
                theme=st.session_state.theme
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering login trend: {str(e)}")
    else:
        st.info("No login trend data available")
    
    st.write("---")
    
    # ============ Export Options ============
    st.subheader("Export Options")
    
    if st.button("📥 Export User Data"):
        # Create export data
        export_data = {
            'Metric': ['Total Users', 'New Users', 'Daily Active', 'Monthly Active', 'Session Count'],
            'Value': [total_users, new_users, daily_active, monthly_active, session_count]
        }
        export_df = pd.DataFrame(export_data)
        
        csv = export_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"user_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
