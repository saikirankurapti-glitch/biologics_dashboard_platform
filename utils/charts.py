"""
Chart and visualization utilities
Reusable Plotly chart configurations
"""

import logging
from typing import List, Dict, Any
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

logger = logging.getLogger(__name__)

# Color schemes
COLORS_PROFESSIONAL = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    'warning': '#d62728',
    'info': '#9467bd',
    'light': '#e0e0e0',
    'dark': '#262626'
}

THEME_DARK = {
    'plot_bgcolor': '#1a1a1a',
    'paper_bgcolor': '#0f0f0f',
    'font_color': '#ffffff',
    'gridcolor': '#333333'
}

THEME_LIGHT = {
    'plot_bgcolor': '#ffffff',
    'paper_bgcolor': '#f5f5f5',
    'font_color': '#000000',
    'gridcolor': '#e0e0e0'
}


class ChartBuilder:
    """Build professional Plotly charts"""
    
    @staticmethod
    def create_line_chart(
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str,
        y_label: str = None,
        theme: str = 'dark',
        height: int = 400
    ) -> go.Figure:
        """Create line chart"""
        try:
            theme_config = THEME_DARK if theme == 'dark' else THEME_LIGHT
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[y_col],
                mode='lines+markers',
                name=y_label or y_col,
                line=dict(color=COLORS_PROFESSIONAL['primary'], width=2),
                marker=dict(size=6)
            ))
            
            fig.update_layout(
                title=title,
                xaxis_title=x_col,
                yaxis_title=y_label or y_col,
                hovermode='x unified',
                height=height,
                plot_bgcolor=theme_config['plot_bgcolor'],
                paper_bgcolor=theme_config['paper_bgcolor'],
                font=dict(color=theme_config['font_color']),
                xaxis=dict(gridcolor=theme_config['gridcolor']),
                yaxis=dict(gridcolor=theme_config['gridcolor']),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            
            return fig
        except Exception as e:
            logger.error(f"Error creating line chart: {str(e)}")
            return go.Figure()
    
    @staticmethod
    def create_bar_chart(
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str,
        y_label: str = None,
        theme: str = 'dark',
        height: int = 400,
        orientation: str = 'v'
    ) -> go.Figure:
        """Create bar chart"""
        try:
            theme_config = THEME_DARK if theme == 'dark' else THEME_LIGHT
            
            fig = go.Figure()
            if orientation == 'v':
                fig.add_trace(go.Bar(
                    x=df[x_col],
                    y=df[y_col],
                    marker=dict(color=COLORS_PROFESSIONAL['primary']),
                    name=y_label or y_col
                ))
            else:
                fig.add_trace(go.Bar(
                    y=df[x_col],
                    x=df[y_col],
                    marker=dict(color=COLORS_PROFESSIONAL['primary']),
                    name=y_label or y_col,
                    orientation='h'
                ))
            
            fig.update_layout(
                title=title,
                xaxis_title=x_col,
                yaxis_title=y_label or y_col,
                hovermode='closest',
                height=height,
                plot_bgcolor=theme_config['plot_bgcolor'],
                paper_bgcolor=theme_config['paper_bgcolor'],
                font=dict(color=theme_config['font_color']),
                xaxis=dict(gridcolor=theme_config['gridcolor']),
                yaxis=dict(gridcolor=theme_config['gridcolor']),
                margin=dict(l=50, r=50, t=80, b=50),
                showlegend=False
            )
            
            return fig
        except Exception as e:
            logger.error(f"Error creating bar chart: {str(e)}")
            return go.Figure()
    
    @staticmethod
    def create_pie_chart(
        df: pd.DataFrame,
        labels_col: str,
        values_col: str,
        title: str,
        theme: str = 'dark',
        height: int = 400
    ) -> go.Figure:
        """Create pie chart"""
        try:
            theme_config = THEME_DARK if theme == 'dark' else THEME_LIGHT
            
            fig = go.Figure()
            fig.add_trace(go.Pie(
                labels=df[labels_col],
                values=df[values_col],
                marker=dict(
                    colors=[
                        COLORS_PROFESSIONAL['primary'],
                        COLORS_PROFESSIONAL['secondary'],
                        COLORS_PROFESSIONAL['success'],
                        COLORS_PROFESSIONAL['warning'],
                        COLORS_PROFESSIONAL['info']
                    ]
                )
            ))
            
            fig.update_layout(
                title=title,
                height=height,
                paper_bgcolor=theme_config['paper_bgcolor'],
                font=dict(color=theme_config['font_color']),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            
            return fig
        except Exception as e:
            logger.error(f"Error creating pie chart: {str(e)}")
            return go.Figure()
    
    @staticmethod
    def create_funnel_chart(
        stages: List[Dict],
        title: str,
        theme: str = 'dark',
        height: int = 400
    ) -> go.Figure:
        """Create funnel chart from stages data"""
        try:
            theme_config = THEME_DARK if theme == 'dark' else THEME_LIGHT
            
            stage_names = [s['stage'] for s in stages]
            counts = [s['count'] for s in stages]
            
            fig = go.Figure()
            fig.add_trace(go.Funnel(
                x=counts,
                y=stage_names,
                marker=dict(
                    color=COLORS_PROFESSIONAL['primary'],
                    line=dict(color=COLORS_PROFESSIONAL['dark'], width=2)
                )
            ))
            
            fig.update_layout(
                title=title,
                height=height,
                plot_bgcolor=theme_config['plot_bgcolor'],
                paper_bgcolor=theme_config['paper_bgcolor'],
                font=dict(color=theme_config['font_color']),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            
            return fig
        except Exception as e:
            logger.error(f"Error creating funnel chart: {str(e)}")
            return go.Figure()
    
    @staticmethod
    def create_scatter_chart(
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str,
        color_col: str = None,
        theme: str = 'dark',
        height: int = 400
    ) -> go.Figure:
        """Create scatter plot"""
        try:
            theme_config = THEME_DARK if theme == 'dark' else THEME_LIGHT
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[y_col],
                mode='markers',
                marker=dict(
                    size=8,
                    color=df[color_col] if color_col else COLORS_PROFESSIONAL['primary'],
                    colorscale='Viridis' if color_col else None,
                    showscale=color_col is not None,
                    opacity=0.7
                ),
                text=df[color_col] if color_col else None,
                hoverinfo='x+y+text'
            ))
            
            fig.update_layout(
                title=title,
                xaxis_title=x_col,
                yaxis_title=y_col,
                hovermode='closest',
                height=height,
                plot_bgcolor=theme_config['plot_bgcolor'],
                paper_bgcolor=theme_config['paper_bgcolor'],
                font=dict(color=theme_config['font_color']),
                xaxis=dict(gridcolor=theme_config['gridcolor']),
                yaxis=dict(gridcolor=theme_config['gridcolor']),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            
            return fig
        except Exception as e:
            logger.error(f"Error creating scatter chart: {str(e)}")
            return go.Figure()
    
    @staticmethod
    def create_heatmap(
        df: pd.DataFrame,
        title: str,
        theme: str = 'dark',
        height: int = 500
    ) -> go.Figure:
        """Create heatmap"""
        try:
            theme_config = THEME_DARK if theme == 'dark' else THEME_LIGHT
            
            fig = go.Figure()
            fig.add_trace(go.Heatmap(
                z=df.values,
                x=df.columns,
                y=df.index,
                colorscale='Viridis'
            ))
            
            fig.update_layout(
                title=title,
                height=height,
                plot_bgcolor=theme_config['plot_bgcolor'],
                paper_bgcolor=theme_config['paper_bgcolor'],
                font=dict(color=theme_config['font_color']),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            
            return fig
        except Exception as e:
            logger.error(f"Error creating heatmap: {str(e)}")
            return go.Figure()
    
    @staticmethod
    def create_box_plot(
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str,
        theme: str = 'dark',
        height: int = 400
    ) -> go.Figure:
        """Create box plot"""
        try:
            theme_config = THEME_DARK if theme == 'dark' else THEME_LIGHT
            
            fig = go.Figure()
            fig.add_trace(go.Box(
                x=df[x_col],
                y=df[y_col],
                marker=dict(color=COLORS_PROFESSIONAL['primary'])
            ))
            
            fig.update_layout(
                title=title,
                xaxis_title=x_col,
                yaxis_title=y_col,
                height=height,
                plot_bgcolor=theme_config['plot_bgcolor'],
                paper_bgcolor=theme_config['paper_bgcolor'],
                font=dict(color=theme_config['font_color']),
                xaxis=dict(gridcolor=theme_config['gridcolor']),
                yaxis=dict(gridcolor=theme_config['gridcolor']),
                margin=dict(l=50, r=50, t=80, b=50)
            )
            
            return fig
        except Exception as e:
            logger.error(f"Error creating box plot: {str(e)}")
            return go.Figure()


def format_large_number(num: int) -> str:
    """Format large numbers with K, M, B suffixes"""
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    else:
        return str(num)
