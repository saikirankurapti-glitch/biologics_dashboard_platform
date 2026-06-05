"""
Candidate Intelligence Dashboard
Candidate ranking, scoring, and ADMET analysis
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import logging
from services.candidate_service import CandidateService
from utils.charts import ChartBuilder, format_large_number

logger = logging.getLogger(__name__)


def render():
    """Render Candidate Intelligence Dashboard"""
    
    st.subheader("Candidate Intelligence")
    
    # Initialize service
    candidate_service = CandidateService()
    
    # ============ Global Filters ============
    st.write("**Filters**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ranking_limit = st.slider(
            "Show Top N Candidates",
            min_value=5,
            max_value=50,
            value=20,
            step=5,
            label_visibility="collapsed"
        )
    
    with col2:
        score_filter = st.slider(
            "Min Score Filter",
            min_value=0,
            max_value=100,
            value=0,
            step=5,
            label_visibility="collapsed"
        )
    
    with col3:
        status_filter = st.selectbox(
            "Status",
            ["All Status", "Active", "Completed", "In Review"],
            label_visibility="collapsed"
        )
    
    st.write("---")
    
    # ============ KPI Cards ============
    st.subheader("Candidate Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        optimization_runs = candidate_service.get_optimization_runs()
        st.metric(
            "⚙️ Optimization Runs",
            format_large_number(optimization_runs),
            delta=None
        )
    
    with col2:
        leads_generated = candidate_service.get_leads_generated()
        st.metric(
            "🚀 Leads Generated",
            format_large_number(leads_generated),
            delta=None
        )
    
    with col3:
        best_score = candidate_service.get_best_candidate_score()
        st.metric(
            "🏆 Best Candidate Score",
            f"{best_score:.2f}",
            delta=None
        )
    
    with col4:
        admet_success = candidate_service.get_admet_success_percentage()
        st.metric(
            "✅ ADMET Success Rate",
            f"{admet_success}%",
            delta=None
        )
    
    st.write("---")
    
    # ============ Candidate Ranking Table ============
    st.subheader("Candidate Ranking")
    
    candidates = candidate_service.get_candidate_ranking(limit=ranking_limit)
    
    if candidates:
        candidates_df = pd.DataFrame(candidates)
        
        # Rename for display
        display_cols = ['candidate_id', 'target_id', 'optimization_score', 'binding_energy', 'status']
        if 'candidate_id' in candidates_df.columns:
            candidates_df_display = candidates_df[display_cols].copy()
            candidates_df_display.columns = ['Candidate ID', 'Target ID', 'Opt Score', 'Binding Energy', 'Status']
            
            st.dataframe(
                candidates_df_display,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.dataframe(candidates_df, use_container_width=True, hide_index=True)
    else:
        st.info("No candidate ranking data available")
    
    st.write("---")
    
    # ============ Top Candidates ============
    st.subheader("Top 5 Candidates")
    
    top_candidates = candidate_service.get_top_candidates(limit=5)
    
    if top_candidates:
        top_df = pd.DataFrame(top_candidates)
        
        col1, col2 = st.columns([1, 1.5])
        
        with col1:
            top_display_cols = ['candidate_id', 'optimization_score']
            if 'candidate_id' in top_df.columns:
                top_df_display = top_df[top_display_cols].copy()
                top_df_display.columns = ['Candidate', 'Score']
                st.dataframe(top_df_display, use_container_width=True, hide_index=True)
        
        with col2:
            try:
                if 'candidate_id' in top_df.columns and 'optimization_score' in top_df.columns:
                    chart_builder = ChartBuilder()
                    fig = chart_builder.create_bar_chart(
                        top_df[['candidate_id', 'optimization_score']].rename(
                            columns={'candidate_id': 'Candidate', 'optimization_score': 'Score'}
                        ),
                        'Candidate',
                        'Score',
                        "Top 5 Candidates by Score",
                        y_label="Score",
                        theme=st.session_state.theme,
                        orientation='h'
                    )
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error rendering top candidates chart: {str(e)}")
    else:
        st.info("No top candidates data available")
    
    st.write("---")
    
    # ============ Optimization Score Distribution ============
    st.subheader("Optimization Score Distribution")
    
    score_dist = candidate_service.get_optimization_score_distribution()
    
    if score_dist:
        score_dist_df = pd.DataFrame(score_dist)
        
        try:
            chart_builder = ChartBuilder()
            fig = chart_builder.create_bar_chart(
                score_dist_df,
                'score_range',
                'count',
                "Score Distribution",
                y_label="Count",
                theme=st.session_state.theme
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering score distribution: {str(e)}")
    else:
        st.info("No score distribution data available")
    
    st.write("---")
    
    # ============ ADMET Pass Rate ============
    st.subheader("ADMET Pass Rate by Property")
    
    admet_rates = candidate_service.get_admet_pass_rate()
    
    if admet_rates:
        admet_df = pd.DataFrame(admet_rates)
        
        col1, col2 = st.columns([1, 1.5])
        
        with col1:
            if 'property' in admet_df.columns and 'pass_rate' in admet_df.columns:
                display_df = admet_df[['property', 'pass_rate', 'passed', 'failed']].copy()
                display_df.columns = ['Property', 'Pass Rate (%)', 'Passed', 'Failed']
                st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        with col2:
            try:
                if 'property' in admet_df.columns and 'pass_rate' in admet_df.columns:
                    chart_builder = ChartBuilder()
                    fig = chart_builder.create_bar_chart(
                        admet_df[['property', 'pass_rate']].rename(
                            columns={'property': 'Property', 'pass_rate': 'Pass Rate'}
                        ),
                        'Property',
                        'Pass Rate',
                        "ADMET Pass Rates",
                        y_label="Pass Rate (%)",
                        theme=st.session_state.theme
                    )
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error rendering ADMET pass rates: {str(e)}")
    else:
        st.info("No ADMET pass rate data available")
    
    st.write("---")
    
    # ============ Candidate Comparison ============
    st.subheader("Candidate Comparison")
    
    if st.checkbox("Enable Candidate Comparison"):
        col1, col2 = st.columns(2)
        
        with col1:
            candidate_1 = st.text_input("Candidate 1 ID")
        
        with col2:
            candidate_2 = st.text_input("Candidate 2 ID")
        
        if candidate_1 and candidate_2:
            comparison_data = candidate_service.get_candidate_comparison([candidate_1, candidate_2])
            
            if comparison_data:
                comp_df = pd.DataFrame(comparison_data)
                st.dataframe(comp_df, use_container_width=True, hide_index=True)
            else:
                st.info("No comparison data available for selected candidates")
    
    st.write("---")
    
    # ============ Candidate Quality Metrics ============
    st.subheader("Candidate Quality Summary")
    
    if candidates:
        candidate_ids = [c.get('candidate_id') for c in candidates[:10] if 'candidate_id' in c]
        
        if candidate_ids:
            quality_metrics = candidate_service.calculate_candidate_quality_metrics(candidate_ids)
            
            if quality_metrics:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Count",
                        quality_metrics.get('candidate_count', 0)
                    )
                
                with col2:
                    st.metric(
                        "Avg Score",
                        f"{quality_metrics.get('average_score', 0):.2f}"
                    )
                
                with col3:
                    st.metric(
                        "Max Score",
                        f"{quality_metrics.get('max_score', 0):.2f}"
                    )
                
                with col4:
                    st.metric(
                        "Min Score",
                        f"{quality_metrics.get('min_score', 0):.2f}"
                    )
    
    st.write("---")
    
    # ============ Export Options ============
    st.subheader("Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export Candidates"):
            if candidates:
                export_df = pd.DataFrame(candidates)
                csv = export_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"candidates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    
    with col2:
        if st.button("📥 Export ADMET Data"):
            if admet_rates:
                admet_export_df = pd.DataFrame(admet_rates)
                csv = admet_export_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"admet_rates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
