"""
Discovery Pipeline Dashboard
Target, Screening, Docking, Optimization, and ADMET metrics
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import logging
from services.pipeline_service import PipelineService
from utils.charts import ChartBuilder, format_large_number

logger = logging.getLogger(__name__)


def render():
    """Render Discovery Pipeline Dashboard"""
    
    st.subheader("Discovery Pipeline")
    
    # Initialize service
    pipeline_service = PipelineService()
    
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
        pipeline_stage = st.selectbox(
            "Pipeline Stage",
            ["All Stages", "Targets", "Screening", "Docking", "Optimization", "ADMET"],
            label_visibility="collapsed"
        )
    
    with col3:
        status_filter = st.selectbox(
            "Status",
            ["All Status", "Completed", "In Progress", "Failed"],
            label_visibility="collapsed"
        )
    
    st.write("---")
    
    # ============ Target Metrics ============
    st.subheader("Target Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        targets_loaded = pipeline_service.get_targets_loaded()
        st.metric(
            "🎯 Targets Loaded",
            format_large_number(targets_loaded),
            delta=None
        )
    
    with col2:
        unique_proteins = pipeline_service.get_unique_proteins()
        st.metric(
            "🧬 Unique Proteins",
            format_large_number(unique_proteins),
            delta=None
        )
    
    target_trend = pipeline_service.get_target_analysis_trend(days=days_range)
    
    if target_trend:
        target_df = pd.DataFrame(target_trend)
        
        try:
            chart_builder = ChartBuilder()
            fig = chart_builder.create_line_chart(
                target_df,
                'date',
                'count',
                "Target Analysis Trend",
                y_label="Count",
                theme=st.session_state.theme
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering target trend: {str(e)}")
    else:
        st.info("No target trend data available")
    
    st.write("---")
    
    # ============ Screening Metrics ============
    st.subheader("Virtual Screening")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        screening_runs = pipeline_service.get_screening_runs()
        st.metric(
            "🔬 Screening Runs",
            format_large_number(screening_runs),
            delta=None
        )
    
    with col2:
        molecules_screened = pipeline_service.get_molecules_screened()
        st.metric(
            "🧪 Molecules Screened",
            format_large_number(molecules_screened),
            delta=None
        )
    
    with col3:
        hits_identified = pipeline_service.get_hits_identified()
        st.metric(
            "🎯 Hits Identified",
            format_large_number(hits_identified),
            delta=None
        )
    
    col1, col2 = st.columns(2)
    
    with col1:
        hit_rate = pipeline_service.get_hit_rate()
        st.metric(
            "📊 Hit Rate",
            f"{hit_rate}%",
            delta=None
        )
    
    with col2:
        # Screening efficiency (hits per run)
        if screening_runs > 0:
            efficiency = round(hits_identified / screening_runs, 2)
            st.metric(
                "⚡ Hits per Run",
                efficiency,
                delta=None
            )
    
    screening_trend = pipeline_service.get_screening_trend(days=days_range)
    
    if screening_trend:
        screening_df = pd.DataFrame(screening_trend)
        
        try:
            chart_builder = ChartBuilder()
            fig = chart_builder.create_line_chart(
                screening_df,
                'date',
                'count',
                "Screening Trend",
                y_label="Count",
                theme=st.session_state.theme
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering screening trend: {str(e)}")
    else:
        st.info("No screening trend data available")
    
    st.write("---")
    
    # ============ Docking Metrics ============
    st.subheader("Molecular Docking")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        docking_jobs = pipeline_service.get_docking_jobs()
        st.metric(
            "🧪 Docking Jobs",
            format_large_number(docking_jobs),
            delta=None
        )
    
    with col2:
        docking_success = pipeline_service.get_docking_success_rate()
        st.metric(
            "✅ Success Rate",
            f"{docking_success}%",
            delta=None
        )
    
    with col3:
        avg_binding = pipeline_service.get_average_binding_energy()
        st.metric(
            "⚡ Avg Binding Energy",
            f"{avg_binding:.3f}",
            delta=None
        )
    
    docking_trend = pipeline_service.get_docking_trend(days=days_range)
    
    if docking_trend:
        docking_df = pd.DataFrame(docking_trend)
        
        try:
            chart_builder = ChartBuilder()
            fig = chart_builder.create_line_chart(
                docking_df,
                'date',
                'count',
                "Docking Trend",
                y_label="Count",
                theme=st.session_state.theme
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering docking trend: {str(e)}")
    else:
        st.info("No docking trend data available")
    
    st.write("---")
    
    # ============ Optimization Metrics ============
    st.subheader("Lead Optimization")
    
    col1, col2 = st.columns(2)
    
    with col1:
        optimization_runs = pipeline_service.get_optimization_runs()
        st.metric(
            "⚙️ Optimization Runs",
            format_large_number(optimization_runs),
            delta=None
        )
    
    with col2:
        leads_generated = pipeline_service.get_leads_generated()
        st.metric(
            "🚀 Leads Generated",
            format_large_number(leads_generated),
            delta=None
        )
    
    optimization_trend = pipeline_service.get_optimization_trend(days=days_range)
    
    if optimization_trend:
        opt_df = pd.DataFrame(optimization_trend)
        
        try:
            chart_builder = ChartBuilder()
            fig = chart_builder.create_line_chart(
                opt_df,
                'date',
                'count',
                "Optimization Trend",
                y_label="Count",
                theme=st.session_state.theme
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering optimization trend: {str(e)}")
    else:
        st.info("No optimization trend data available")
    
    st.write("---")
    
    # ============ ADMET Metrics ============
    st.subheader("ADMET Prediction")
    
    col1, col2 = st.columns(2)
    
    with col1:
        admet_runs = pipeline_service.get_admet_runs()
        st.metric(
            "🧬 ADMET Predictions",
            format_large_number(admet_runs),
            delta=None
        )
    
    with col2:
        admet_success = pipeline_service.get_admet_success_rate()
        st.metric(
            "✅ Success Rate",
            f"{admet_success}%",
            delta=None
        )
    
    admet_trend = pipeline_service.get_admet_trend(days=days_range)
    
    if admet_trend:
        admet_df = pd.DataFrame(admet_trend)
        
        try:
            chart_builder = ChartBuilder()
            fig = chart_builder.create_line_chart(
                admet_df,
                'date',
                'count',
                "ADMET Trend",
                y_label="Count",
                theme=st.session_state.theme
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering ADMET trend: {str(e)}")
    else:
        st.info("No ADMET trend data available")
    
    st.write("---")
    
    # ============ Pipeline Funnel ============
    st.subheader("Discovery Pipeline Funnel")
    
    funnel_data = pipeline_service.get_discovery_funnel()
    
    if funnel_data:
        funnel_df = pd.DataFrame(funnel_data)
        
        col1, col2 = st.columns([1, 1.5])
        
        with col1:
            st.dataframe(funnel_df, use_container_width=True, hide_index=True)
        
        with col2:
            try:
                chart_builder = ChartBuilder()
                fig = chart_builder.create_funnel_chart(
                    funnel_data,
                    "Discovery Pipeline",
                    theme=st.session_state.theme
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error rendering funnel: {str(e)}")
    else:
        st.info("No pipeline funnel data available")
    
    st.write("---")
    
    # ============ Export Options ============
    st.subheader("Export Options")
    
    if st.button("📥 Export Pipeline Data"):
        export_data = {
            'Stage': ['Target', 'Screening', 'Docking', 'Optimization', 'ADMET'],
            'Count': [targets_loaded, screening_runs, docking_jobs, optimization_runs, admet_runs],
            'Success Rate': ['-', f"{pipeline_service.get_hit_rate()}%", f"{docking_success}%", '-', f"{admet_success}%"]
        }
        export_df = pd.DataFrame(export_data)
        
        csv = export_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"pipeline_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
