"""
UI and Design System Components for Biologics Discovery Platform
Provides CSS styling overrides and reusable HTML components matching the Stitch design.
Uses clean_html helper to strip line indentation and prevent markdown code block formatting.
"""

import streamlit as st

def clean_html(html: str) -> str:
    """Removes all leading/trailing whitespace from each line to prevent markdown code block formatting"""
    return "".join(line.strip() for line in html.splitlines())


def apply_custom_css(theme: str):
    """Inject custom CSS stylesheet overrides for custom themes"""
    
    # Common styles (fonts, scrollbars, spacing, transitions)
    common_css = """
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Hanken+Grotesk:wght@600;700;800&family=JetBrains+Mono:wght@500&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');
    
    /* Hide Streamlit components */
    [data-testid="stHeader"] {
        display: none !important;
    }
    
    /* Global Typography */
    body, [data-testid="stAppViewContainer"], [data-testid="stWidgetLabel"] {
        font-family: 'Inter', sans-serif !important;
    }
    
    h1, h2, h3, h4, h5, h6, [data-testid="stHeader"] {
        font-family: 'Hanken Grotesk', sans-serif !important;
    }
    
    /* Glass Panel Styles */
    .glass-panel {
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        backdrop-filter: blur(12px);
        margin-bottom: 24px;
        transition: all 0.3s ease;
    }
    .glass-panel:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    /* Sequence Monospace Box */
    .sequence-bg {
        background: #0f172a;
        color: #38bdf8;
        font-family: 'JetBrains Mono', monospace;
        padding: 16px;
        border-radius: 8px;
        border: 1px solid #1e293b;
    }
    
    /* Custom Scrollbars */
    .custom-scrollbar::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    .custom-scrollbar::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 10px;
    }
    
    /* Navigation radio styling */
    div[data-testid="stRadio"] > label {
        display: none !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] {
        flex-direction: column !important;
        gap: 6px !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label {
        display: flex !important;
        align-items: center !important;
        padding: 10px 16px !important;
        border-radius: 8px !important;
        cursor: pointer !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        border: none !important;
        width: 100% !important;
    }
    
    /* Hide radio circle & default spacing */
    div[data-testid="stRadio"] div[role="radiogroup"] label input[type="radio"] {
        display: none !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label > div:first-child {
        display: none !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] {
        margin-left: 0 !important;
    }
    
    /* Sidebar specific custom brand logo spacing */
    .sidebar-brand {
        padding: 24px;
        margin-bottom: 24px;
    }
    
    /* Plotly charts customization */
    .js-plotly-plot .plotly .modebar {
        opacity: 0.3 !important;
    }
    .js-plotly-plot .plotly .modebar:hover {
        opacity: 0.9 !important;
    }
    """
    
    if theme == 'dark':
        theme_css = """
        /* Dark mode tokens */
        :root {
            --background: #0f172a;
            --surface: #1e293b;
            --on-surface: #f8fafc;
            --on-surface-variant: #94a3b8;
            --outline-variant: #334155;
            --secondary-container: #004e5c;
            --on-secondary-container: #acedff;
            --surface-container-low: #0f172a;
        }
        
        .stAppViewContainer {
            background-color: #0b0f19 !important;
            color: #f8fafc !important;
        }
        
        /* Sidebar container override */
        section[data-testid="stSidebar"] {
            background-color: #0d121f !important;
            border-right: 1px solid #1e293b !important;
            width: 260px !important;
        }
        
        /* Glass Panel */
        .glass-panel {
            background: rgba(17, 24, 39, 0.75);
            border: 1px solid rgba(51, 65, 85, 0.5);
            color: #f8fafc;
        }
        
        /* Radio nav active and hover */
        div[data-testid="stRadio"] div[role="radiogroup"] label {
            color: #94a3b8 !important;
        }
        div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
            background-color: rgba(51, 65, 85, 0.3) !important;
            color: #f8fafc !important;
        }
        div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
            background-color: #132a35 !important;
            color: #4cd7f6 !important;
            font-weight: 600 !important;
        }
        
        /* Prepend icons to radio labels */
        div[data-testid="stRadio"] div[role="radiogroup"] label:nth-of-type(1)::before {
            content: "dashboard";
            font-family: 'Material Symbols Outlined';
            font-size: 20px;
            margin-right: 12px;
        }
        div[data-testid="stRadio"] div[role="radiogroup"] label:nth-of-type(2)::before {
            content: "analytics";
            font-family: 'Material Symbols Outlined';
            font-size: 20px;
            margin-right: 12px;
        }
        div[data-testid="stRadio"] div[role="radiogroup"] label:nth-of-type(3)::before {
            content: "monitoring";
            font-family: 'Material Symbols Outlined';
            font-size: 20px;
            margin-right: 12px;
        }
        div[data-testid="stRadio"] div[role="radiogroup"] label:nth-of-type(4)::before {
            content: "biotech";
            font-family: 'Material Symbols Outlined';
            font-size: 20px;
            margin-right: 12px;
        }
        div[data-testid="stRadio"] div[role="radiogroup"] label:nth-of-type(5)::before {
            content: "science";
            font-family: 'Material Symbols Outlined';
            font-size: 20px;
            margin-right: 12px;
        }
        
        /* Native inputs styling */
        div[data-testid="stSelectbox"] select, div[data-testid="stSelectbox"] div[role="button"] {
            background-color: #1e293b !important;
            color: #f8fafc !important;
            border: 1px solid #334155 !important;
        }
        
        /* DataFrame styles */
        div[data-testid="stDataFrame"] {
            border: 1px solid #334155 !important;
            border-radius: 8px !important;
        }
        
        hr {
            border-color: #1e293b !important;
        }
        """
    else:
        theme_css = """
        /* Light mode tokens */
        :root {
            --background: #f8f9ff;
            --surface: #ffffff;
            --on-surface: #0b1c30;
            --on-surface-variant: #45464d;
            --outline-variant: #c6c6cd;
            --secondary-container: #57dffe;
            --on-secondary-container: #006172;
            --surface-container-low: #eff4ff;
        }
        
        .stAppViewContainer {
            background-color: #f8fafc !important;
            color: #0b1c30 !important;
        }
        
        /* Sidebar container override */
        section[data-testid="stSidebar"] {
            background-color: #eff4ff !important;
            border-right: 1px solid #c6c6cd !important;
            width: 260px !important;
        }
        
        /* Glass Panel */
        .glass-panel {
            background: rgba(255, 255, 255, 0.75);
            border: 1px solid rgba(226, 232, 240, 0.9);
            color: #0b1c30;
        }
        
        /* Radio nav active and hover */
        div[data-testid="stRadio"] div[role="radiogroup"] label {
            color: #45464d !important;
        }
        div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
            background-color: #dce9ff !important;
            color: #0b1c30 !important;
        }
        div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
            background-color: #57dffe !important;
            color: #006172 !important;
            font-weight: 600 !important;
        }
        
        /* Prepend icons to radio labels */
        div[data-testid="stRadio"] div[role="radiogroup"] label:nth-of-type(1)::before {
            content: "dashboard";
            font-family: 'Material Symbols Outlined';
            font-size: 20px;
            margin-right: 12px;
        }
        div[data-testid="stRadio"] div[role="radiogroup"] label:nth-of-type(2)::before {
            content: "analytics";
            font-family: 'Material Symbols Outlined';
            font-size: 20px;
            margin-right: 12px;
        }
        div[data-testid="stRadio"] div[role="radiogroup"] label:nth-of-type(3)::before {
            content: "monitoring";
            font-family: 'Material Symbols Outlined';
            font-size: 20px;
            margin-right: 12px;
        }
        div[data-testid="stRadio"] div[role="radiogroup"] label:nth-of-type(4)::before {
            content: "biotech";
            font-family: 'Material Symbols Outlined';
            font-size: 20px;
            margin-right: 12px;
        }
        div[data-testid="stRadio"] div[role="radiogroup"] label:nth-of-type(5)::before {
            content: "science";
            font-family: 'Material Symbols Outlined';
            font-size: 20px;
            margin-right: 12px;
        }
        
        /* Native inputs styling */
        div[data-testid="stSelectbox"] select, div[data-testid="stSelectbox"] div[role="button"] {
            background-color: #ffffff !important;
            color: #0b1c30 !important;
            border: 1px solid #c6c6cd !important;
        }
        
        /* DataFrame styles */
        div[data-testid="stDataFrame"] {
            border: 1px solid #c6c6cd !important;
            border-radius: 8px !important;
        }
        
        hr {
            border-color: #e2e8f0 !important;
        }
        """
        
    st.markdown(f"<style>{common_css}{theme_css}</style>", unsafe_allow_html=True)


def render_brand_header():
    """Renders the top logo block in the custom sidebar"""
    st.markdown(clean_html("""
    <div style="padding: 12px 16px 24px 16px;">
        <h1 style="margin: 0; font-size: 22px; font-weight: 800; color: #312E81;">BioDiscovery AI</h1>
        <p style="margin: 2px 0 0 0; font-size: 12px; font-weight: 500; color: #64748b;">Discovery Lab 04</p>
    </div>
    """), unsafe_allow_html=True)


def render_top_bar(theme: str, page_title: str):
    """Renders the sticky top app bar with profile details from the database"""
    bg_color = "rgba(15, 23, 42, 0.85)" if theme == "dark" else "rgba(248, 250, 252, 0.85)"
    text_color = "#f8fafc" if theme == "dark" else "#0b1c30"
    border_color = "rgba(51, 65, 85, 0.5)" if theme == "dark" else "rgba(198, 198, 205, 0.5)"
    
    # Retrieve user from session state or default
    user_name = st.session_state.get("current_user_name", "saikiran")
    parts = user_name.split()
    if len(parts) >= 2:
        initials = (parts[0][0] + parts[1][0]).upper()
    elif len(parts) == 1:
        initials = parts[0][:2].upper()
    else:
        initials = "SK"
        
    st.markdown(clean_html(f"""
    <div style="
        position: sticky;
        top: 0;
        z-index: 999;
        background: {bg_color};
        backdrop-filter: blur(12px);
        border-bottom: 1px solid {border_color};
        display: flex;
        justify-content: space-between;
        align-items: center;
        height: 64px;
        padding: 0 24px;
        margin: -6rem -4rem 2rem -4rem;
    ">
        <div style="display: flex; align-items: center; gap: 16px;">
            <span style="font-family: 'Hanken Grotesk', sans-serif; font-size: 1.25rem; font-weight: 800; color: {text_color};">BioDiscovery Suite</span>
            <span style="color: #64748b; font-size: 14px;">|</span>
            <span style="font-size: 14px; font-weight: 600; color: #64748b;">{page_title}</span>
        </div>
        <div style="display: flex; align-items: center; gap: 16px;">
            <button style="background: transparent; border: none; color: {text_color}; cursor: pointer; display: flex; align-items: center;">
                <span class="material-symbols-outlined">notifications</span>
            </button>
            <div style="height: 24px; width: 1px; background: {border_color};"></div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="
                    width: 32px; 
                    height: 32px; 
                    border-radius: 50%; 
                    background: #00687a; 
                    color: #ffffff; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    font-size: 12px; 
                    font-weight: 700; 
                    border: 1px solid {border_color};
                ">
                    {initials}
                </div>
                <span style="font-size: 13px; font-weight: 600; color: {text_color};">{user_name}</span>
            </div>
        </div>
    </div>
    """), unsafe_allow_html=True)


def render_kpi_card(title: str, value: str, icon: str, subtitle: str = None, delta: str = None, border_color: str = None, theme: str = "dark"):
    """Renders a custom glassmorphic KPI card with Stitch styling"""
    bg_color = "rgba(30, 41, 59, 0.45)" if theme == "dark" else "rgba(255, 255, 255, 0.7)"
    text_color = "#f8fafc" if theme == "dark" else "#0b1c30"
    variant_text = "#94a3b8" if theme == "dark" else "#45464d"
    border_style = f"border-top: 3px solid {border_color};" if border_color else ""
    border_outline = "rgba(51, 65, 85, 0.4)" if theme == "dark" else "rgba(226, 232, 240, 0.8)"
    
    delta_html = ""
    if delta:
        delta_color = "#2ca02c" if "+" in delta or "Rate" in title else "#d62728"
        delta_html = f'<div style="font-size: 12px; font-weight: 600; color: {delta_color}; margin-top: 4px;">{delta}</div>'
        
    subtitle_html = f'<div style="font-size: 11px; font-weight: 700; color: {variant_text}; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 2px;">{subtitle}</div>' if subtitle else ""
    
    st.markdown(clean_html(f"""
    <div class="glass-panel" style="background: {bg_color}; border: 1px solid {border_outline}; {border_style} padding: 18px; margin-bottom: 12px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                {subtitle_html}
                <div style="font-size: 14px; font-weight: 600; color: {text_color};">{title}</div>
            </div>
            <span class="material-symbols-outlined" style="color: {border_color or '#00687a'}; font-size: 20px;">{icon}</span>
        </div>
        <div style="font-size: 26px; font-weight: 800; font-family: 'Hanken Grotesk', sans-serif; color: {text_color}; margin-top: 8px;">{value}</div>
        {delta_html}
    </div>
    """), unsafe_allow_html=True)


def render_candidate_progress_bar(label: str, value: float, color: str):
    """Renders a simple HTML progress bar for efficacy, toxicity, etc."""
    percent = int(value * 100)
    return f"""
    <div style="margin-bottom: 10px;">
        <div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 600; text-transform: uppercase; color: #64748b; margin-bottom: 3px;">
            <span>{label}</span>
            <span style="font-family: 'JetBrains Mono', monospace;">{value:.2f}</span>
        </div>
        <div style="height: 6px; width: 100%; background: rgba(148, 163, 184, 0.2); border-radius: 4px; overflow: hidden;">
            <div style="height: 100%; width: {percent}%; background: {color}; border-radius: 4px;"></div>
        </div>
    </div>
    """


def render_lead_candidate_card(rank: int, name: str, match_percent: float, efficacy: float, toxicity: float, manufacturability: float, stability: float, border_color: str, theme: str = "dark"):
    """Renders a detailed Lead Candidate ranking card"""
    bg_color = "rgba(30, 41, 59, 0.45)" if theme == "dark" else "rgba(255, 255, 255, 0.7)"
    text_color = "#f8fafc" if theme == "dark" else "#0b1c30"
    variant_text = "#94a3b8" if theme == "dark" else "#45464d"
    border_outline = "rgba(51, 65, 85, 0.4)" if theme == "dark" else "rgba(226, 232, 240, 0.8)"
    
    progress_html = (
        render_candidate_progress_bar("Efficacy Score", efficacy, "#00687a") +
        render_candidate_progress_bar("Toxicity Risk", toxicity, "#FF4B4B") +
        render_candidate_progress_bar("Manufacturability", manufacturability, "#3B82F6") +
        render_candidate_progress_bar("Stability", stability, "#A855F7")
    )
    
    st.markdown(clean_html(f"""
    <div class="glass-panel" style="background: {bg_color}; border: 1px solid {border_outline}; border-top: 3px solid {border_color}; padding: 20px; margin-bottom: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
            <div>
                <span style="background: {border_color}20; color: {border_color}; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">Rank #{rank}</span>
                <h3 style="margin: 6px 0 0 0; font-size: 20px; font-weight: 800; color: {text_color};">{name}</h3>
            </div>
            <div style="text-align: right;">
                <div style="font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #00687a; font-size: 16px;">{match_percent}% Match</div>
                <div style="font-size: 9px; font-weight: 700; text-transform: uppercase; color: {variant_text}; letter-spacing: 1px;">Confidence</div>
            </div>
        </div>
        <div>
            {progress_html}
        </div>
    </div>
    """), unsafe_allow_html=True)


def render_insight_card(title: str, description: str, status_type: str = "info", theme: str = "dark"):
    """Renders a colorful status card with left accent border for insights"""
    
    colors = {
        "success": {"border": "#00687a", "bg_dark": "rgba(0, 104, 122, 0.1)", "bg_light": "rgba(0, 104, 122, 0.05)", "icon": "verified"},
        "warning": {"border": "#A855F7", "bg_dark": "rgba(168, 85, 247, 0.1)", "bg_light": "rgba(168, 85, 247, 0.05)", "icon": "auto_fix_high"},
        "critical": {"border": "#FF4B4B", "bg_dark": "rgba(255, 75, 75, 0.1)", "bg_light": "rgba(255, 75, 75, 0.05)", "icon": "warning"}
    }
    
    cfg = colors.get(status_type, colors["success"])
    bg = cfg["bg_dark"] if theme == "dark" else cfg["bg_light"]
    text_color = "#f8fafc" if theme == "dark" else "#0b1c30"
    variant_text = "#cbd5e1" if theme == "dark" else "#475569"
    
    st.markdown(clean_html(f"""
    <div style="
        display: flex;
        gap: 16px;
        padding: 16px;
        background: {bg};
        border-radius: 8px;
        border-left: 4px solid {cfg['border']};
        margin-bottom: 16px;
    ">
        <span class="material-symbols-outlined" style="color: {cfg['border']}; font-size: 22px; margin-top: 2px;">{cfg['icon']}</span>
        <div>
            <h4 style="margin: 0 0 4px 0; font-size: 14px; font-weight: 700; color: {text_color};">{title}</h4>
            <p style="margin: 0; font-size: 13px; color: {variant_text}; line-height: 1.5;">{description}</p>
        </div>
    </div>
    """), unsafe_allow_html=True)


def render_sequence_viewer(sequence: str, title: str, transcription_fidelity: float, codon_bias: float, theme: str = "dark"):
    """Renders a beautiful scrollable sequence viewer with MET/GL highlight"""
    # Replace MET and GL
    highlighted_seq = sequence
    highlighted_seq = highlighted_seq.replace(
        "MET", '<span style="background: rgba(168, 85, 247, 0.35); color: #c084fc; padding: 0 2px; border-radius: 2px;">MET</span>'
    )
    highlighted_seq = highlighted_seq.replace(
        "GL", '<span style="border-bottom: 2px solid #FF4B4B; color: #ff8080; font-weight: 700;">GL</span>'
    )
    
    st.markdown(clean_html(f"""
    <div class="glass-panel" style="background: {'rgba(30, 41, 59, 0.45)' if theme == 'dark' else 'rgba(255, 255, 255, 0.7)'}; border: 1px solid {'rgba(51, 65, 85, 0.4)' if theme == 'dark' else 'rgba(226, 232, 240, 0.8)'}; padding: 20px; display: flex; flex-direction: column; height: 100%;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <h3 style="margin: 0; font-size: 16px; font-weight: 700; color: {'#f8fafc' if theme == 'dark' else '#0b1c30'};">Sequence Analysis</h3>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 10px; background: rgba(148, 163, 184, 0.15); padding: 4px 8px; border-radius: 4px; color: {'#94a3b8' if theme == 'dark' else '#475569'};">{title}</span>
        </div>
        <div class="sequence-bg" style="position: relative; flex: 1; min-height: 140px; max-height: 220px; overflow-y: auto; overflow-x: hidden;">
            <div style="position: absolute; top: 8px; right: 8px; display: flex; align-items: center; gap: 6px;">
                <span style="width: 6px; height: 6px; border-radius: 50%; background: #2ca02c;"></span>
                <span style="font-size: 9px; text-transform: uppercase; font-weight: 700; color: #2ca02c; opacity: 0.8;">Real-time Stream</span>
            </div>
            <div style="font-size: 11px; line-height: 1.7; letter-spacing: 1px; word-break: break-all; margin-top: 10px; padding-right: 8px;">
                <span style="color: #64748b; font-size: 9px; display: block; margin-bottom: 6px; letter-spacing: 0.5px;"># BASE PAIR MAPPING 001-450</span>
                {highlighted_seq}
            </div>
        </div>
        <div style="display: flex; gap: 16px; margin-top: 16px;">
            <div style="flex: 1;">
                <div style="display: flex; justify-content: space-between; font-size: 10px; font-weight: 700; text-transform: uppercase; color: #64748b; margin-bottom: 4px;">
                    <span>Transcription Fidelity</span>
                    <span>{transcription_fidelity}%</span>
                </div>
                <div style="height: 4px; width: 100%; background: rgba(148, 163, 184, 0.2); border-radius: 2px;">
                    <div style="height: 100%; width: {transcription_fidelity}%; background: #00687a; border-radius: 2px;"></div>
                </div>
            </div>
            <div style="flex: 1;">
                <div style="display: flex; justify-content: space-between; font-size: 10px; font-weight: 700; text-transform: uppercase; color: #64748b; margin-bottom: 4px;">
                    <span>Codon Usage Bias</span>
                    <span>{codon_bias}%</span>
                </div>
                <div style="height: 4px; width: 100%; background: rgba(148, 163, 184, 0.2); border-radius: 2px;">
                    <div style="height: 100%; width: {codon_bias}%; background: #A855F7; border-radius: 2px;"></div>
                </div>
            </div>
        </div>
    </div>
    """), unsafe_allow_html=True)
