"""
Discovery Pipeline Dashboard
Detailed view of drug discovery pipeline stages and throughput
Refactored to match Stitch professional design system with dark/light themes.
Preserves all MongoDB integrations, filters, calculations, and exports.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import logging
from services.pipeline_service import PipelineService
from utils.charts import ChartBuilder, format_large_number
import utils.ui_components as ui

logger = logging.getLogger(__name__)


def render():
    """Render Discovery Pipeline Dashboard"""
    
    theme = st.session_state.theme
    
    # Initialize service
    pipeline_service = PipelineService()
    
    # Fetch filter options from database
    try:
        targets_list = pipeline_service.db_ops.find("targets")
        target_options = ["All Targets"]
        target_map = {}
        for t in targets_list:
            tid = t.get('target_id') or t.get('sequence') or str(t.get('_id'))
            name = t.get('name') or t.get('target_name') or tid
            display_name = f"{tid} - {name}"
            if len(display_name) > 80:
                display_name = display_name[:77] + "..."
            target_options.append(display_name)
            target_map[display_name] = tid
            
        opt_targets = pipeline_service.db_ops.find("optimizations")
        for o in opt_targets:
            tid = o.get('target_id')
            if tid and tid not in target_map.values():
                display_name = f"{tid} - Optimization Target"
                target_options.append(display_name)
                target_map[display_name] = tid
    except Exception:
        target_options = ["All Targets"]
        target_map = {}
        
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
        target_filter = st.selectbox(
            "Target Select",
            target_options,
            label_visibility="collapsed"
        )
        
    # Map filters
    start_date = datetime.now() - timedelta(days=days_range)
    end_date = datetime.now()
    selected_target = target_map.get(target_filter)
    
    st.write("---")
    
    # ============ Stage 1: Target Identification ============
    st.markdown("### 🎯 Stage 1: Target Identification")
    st.caption("Identify disease-relevant target proteins and structural models.")
    
    targets_loaded = pipeline_service.get_targets_loaded(start_date=start_date, end_date=end_date, target_id=selected_target)
    unique_proteins = pipeline_service.get_unique_proteins(start_date=start_date, end_date=end_date, target_id=selected_target)
    
    t_cols = st.columns(2)
    with t_cols[0]:
        ui.render_kpi_card("Targets Loaded", format_large_number(targets_loaded), "track_changes", border_color="#00687a", theme=theme)
    with t_cols[1]:
        ui.render_kpi_card("Unique Proteins", format_large_number(unique_proteins), "biotech", border_color="#3B82F6", theme=theme)
        
    target_trend = pipeline_service.get_target_analysis_trend(days=days_range, start_date=start_date, end_date=end_date, target_id=selected_target)
    if target_trend:
        t_df = pd.DataFrame(target_trend)
        try:
            chart_builder = ChartBuilder()
            fig = chart_builder.create_line_chart(
                t_df,
                'date',
                'count',
                "Target Integration Rate over Time",
                y_label="Count",
                theme=theme,
                height=250
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering target trend: {str(e)}")
    else:
        st.info("No target trend data available")
        
    st.write("---")
    
    # ============ Stage 2: Virtual Screening ============
    st.markdown("### 🔬 Stage 2: Virtual Screening")
    st.caption("High-throughput molecular screening (HTVS) on protein pockets.")
    
    screening_runs = pipeline_service.get_screening_runs(start_date=start_date, end_date=end_date, target_id=selected_target)
    molecules_screened = pipeline_service.get_molecules_screened(start_date=start_date, end_date=end_date, target_id=selected_target)
    hits_identified = pipeline_service.get_hits_identified(start_date=start_date, end_date=end_date, target_id=selected_target)
    hit_rate = pipeline_service.get_hit_rate(start_date=start_date, end_date=end_date, target_id=selected_target)
    efficiency = round(hits_identified / screening_runs, 2) if screening_runs > 0 else 0.0
    
    s_cols = st.columns(5)
    with s_cols[0]:
        ui.render_kpi_card("Screening Runs", format_large_number(screening_runs), "science", border_color="#00687a", theme=theme)
    with s_cols[1]:
        ui.render_kpi_card("Molecules Screened", format_large_number(molecules_screened), "bubble_chart", border_color="#3B82F6", theme=theme)
    with s_cols[2]:
        ui.render_kpi_card("Hits Identified", format_large_number(hits_identified), "emoji_events", border_color="#A855F7", theme=theme)
    with s_cols[3]:
        ui.render_kpi_card("Hit Rate", f"{hit_rate}%", "query_stats", border_color="#2ca02c", theme=theme)
    with s_cols[4]:
        ui.render_kpi_card("Hits per Run", f"{efficiency}", "speed", border_color="#312E81", theme=theme)
        
    screening_trend = pipeline_service.get_screening_trend(days=days_range, start_date=start_date, end_date=end_date, target_id=selected_target)
    if screening_trend:
        s_df = pd.DataFrame(screening_trend)
        try:
            chart_builder = ChartBuilder()
            fig = chart_builder.create_line_chart(
                s_df,
                'date',
                'count',
                "HTVS Activity Trend",
                y_label="Count",
                theme=theme,
                height=250
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering screening trend: {str(e)}")
    else:
        st.info("No screening trend data available")
        
    st.write("---")
    
    # ============ Stage 3: Molecular Docking ============
    st.markdown("### ⚡ Stage 3: Molecular Docking")
    st.caption("Thermodynamic docking simulations and binding energy calculation.")
    
    docking_jobs = pipeline_service.get_docking_jobs(start_date=start_date, end_date=end_date, target_id=selected_target)
    docking_success = pipeline_service.get_docking_success_rate(start_date=start_date, end_date=end_date, target_id=selected_target)
    avg_binding = pipeline_service.get_average_binding_energy(start_date=start_date, end_date=end_date, target_id=selected_target)
    
    d_cols = st.columns(3)
    with d_cols[0]:
        ui.render_kpi_card("Docking Jobs", format_large_number(docking_jobs), "settings", border_color="#00687a", theme=theme)
    with d_cols[1]:
        ui.render_kpi_card("Docking Success Rate", f"{docking_success}%", "check_circle", border_color="#2ca02c", theme=theme)
    with d_cols[2]:
        ui.render_kpi_card("Avg Binding Energy", f"{avg_binding:.3f} kcal/mol", "bolt", border_color="#A855F7", theme=theme)
        
    docking_trend = pipeline_service.get_docking_trend(days=days_range, start_date=start_date, end_date=end_date, target_id=selected_target)
    if docking_trend:
        d_df = pd.DataFrame(docking_trend)
        try:
            chart_builder = ChartBuilder()
            fig = chart_builder.create_line_chart(
                d_df,
                'date',
                'count',
                "Docking Run Frequency",
                y_label="Count",
                theme=theme,
                height=250
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering docking trend: {str(e)}")
    else:
        st.info("No docking trend data available")
        
    st.write("---")
    
    # ============ Stage 4: Lead Optimization ============
    st.markdown("### ⚙️ Stage 4: Lead Optimization")
    st.caption("Refining candidate scaffold structures for optimal target binding affinity.")
    
    optimization_runs = pipeline_service.get_optimization_runs(start_date=start_date, end_date=end_date, target_id=selected_target)
    leads_generated = pipeline_service.get_leads_generated(start_date=start_date, end_date=end_date, target_id=selected_target)
    
    o_cols = st.columns(2)
    with o_cols[0]:
        ui.render_kpi_card("Optimization Runs", format_large_number(optimization_runs), "tune", border_color="#00687a", theme=theme)
    with o_cols[1]:
        ui.render_kpi_card("Leads Generated", format_large_number(leads_generated), "rocket_launch", border_color="#3B82F6", theme=theme)
        
    optimization_trend = pipeline_service.get_optimization_trend(days=days_range, start_date=start_date, end_date=end_date, target_id=selected_target)
    if optimization_trend:
        opt_df = pd.DataFrame(optimization_trend)
        try:
            chart_builder = ChartBuilder()
            fig = chart_builder.create_line_chart(
                opt_df,
                'date',
                'count',
                "Lead Optimization Cycles",
                y_label="Count",
                theme=theme,
                height=250
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering optimization trend: {str(e)}")
    else:
        st.info("No optimization trend data available")
        
    st.write("---")
    
    # ============ Stage 5: ADMET Prediction ============
    st.markdown("### 🧬 Stage 5: ADMET Prediction")
    st.caption("In-silico ADMET (Absorption, Distribution, Metabolism, Excretion, Toxicity) profiling.")
    
    admet_runs = pipeline_service.get_admet_runs(start_date=start_date, end_date=end_date, target_id=selected_target)
    admet_success = pipeline_service.get_admet_success_rate(start_date=start_date, end_date=end_date, target_id=selected_target)
    
    a_cols = st.columns(2)
    with a_cols[0]:
        ui.render_kpi_card("ADMET Predictions", format_large_number(admet_runs), "donut_large", border_color="#00687a", theme=theme)
    with a_cols[1]:
        ui.render_kpi_card("ADMET Success Rate", f"{admet_success}%", "check_circle", border_color="#2ca02c", theme=theme)
        
    admet_trend = pipeline_service.get_admet_trend(days=days_range, start_date=start_date, end_date=end_date, target_id=selected_target)
    if admet_trend:
        admet_df = pd.DataFrame(admet_trend)
        try:
            chart_builder = ChartBuilder()
            fig = chart_builder.create_line_chart(
                admet_df,
                'date',
                'count',
                "ADMET Computation Rate",
                y_label="Count",
                theme=theme,
                height=250
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering ADMET trend: {str(e)}")
    else:
        st.info("No ADMET trend data available")
        
    st.write("---")
    
    # ============ Discovery Pipeline Funnel ============
    st.markdown("### Discovery Pipeline Funnel (3D)")
    
    funnel_query = {}
    if start_date and end_date:
        funnel_query['created_at'] = {'$gte': start_date, '$lte': end_date}
    if selected_target:
        funnel_query['target_id'] = selected_target

    reports_query = dict(funnel_query)
    reports = pipeline_service.db_ops.count_documents('report_registry', reports_query)

    stages_data = [
        {"stage": "Target Discovery", "count": targets_loaded, "description": "Disease-related target identification and annotation."},
        {"stage": "AI Screening", "count": screening_runs, "description": "Virtual screening of compound libraries."},
        {"stage": "Docking", "count": docking_jobs, "description": "Molecular docking and affinity analysis."},
        {"stage": "Lead Optimization", "count": optimization_runs, "description": "Scaffold optimization and affinity refinement."},
        {"stage": "ADMET", "count": admet_runs, "description": "Absorption, distribution, metabolism, excretion, and toxicity profiling."},
        {"stage": "Preformulation", "count": pipeline_service.db_ops.count_documents('preformulation_reports', funnel_query), "description": "Physical and chemical characterization of active substances."},
        {"stage": "Formulation", "count": pipeline_service.db_ops.count_documents('formulation_designs', funnel_query), "description": "Dosage form design and parameter definition."},
        {"stage": "Experiments", "count": pipeline_service.db_ops.count_documents('experiments', funnel_query), "description": "Wet-lab experimental validation."},
        {"stage": "Reports", "count": reports, "description": "Final regulatory compliance dossiers and summary reports."}
    ]

    for idx, stage in enumerate(stages_data):
        if idx == 0:
            stage['conversion_rate'] = 100
        else:
            prev_count = stages_data[idx - 1]['count']
            stage['conversion_rate'] = round((stage['count'] / prev_count * 100), 1) if prev_count > 0 else 0.0

    import utils.three_js_renderer as three
    
    col1, col2 = st.columns([1.2, 2.8])
    with col1:
        stages_df = pd.DataFrame(stages_data)[['stage', 'count', 'conversion_rate']]
        stages_df.columns = ['Stage', 'Count', 'Conversion %']
        st.dataframe(stages_df, use_container_width=True, hide_index=True)
    with col2:
        three.render_3d_funnel(stages_data, theme)
        
    st.write("---")
    
    # ============ 3D Knowledge Graph ============
    st.markdown("### 3D Discovery Knowledge Graph")
    st.caption("Visualizing high-fidelity relationships mapping targets, virtual screening runs, leads, and ADMET profiles.")
    three.render_3d_knowledge_graph(theme)
    
    st.write("---")
    
    # ============ Export Options ============
    st.markdown("### Export Options")
    if st.button("📥 Export Comprehensive Pipeline Summary"):
        export_data = {
            'Stage': ['Target', 'Screening', 'Docking', 'Optimization', 'ADMET'],
            'Count': [targets_loaded, screening_runs, docking_jobs, optimization_runs, admet_runs],
            'Success Rate': ['-', f"{hit_rate}%", f"{docking_success}%", '-', f"{admet_success}%"]
        }
        export_df = pd.DataFrame(export_data)
        csv = export_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"pipeline_metrics_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
