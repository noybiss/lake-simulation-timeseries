"""
visualizer.py — Plotly chart builders for the Scenario Simulator.

Design System: "Environmental Simulation System" — DARK MODE.
Colors: Primary (#98cded), Secondary (#76d4e7), Accent orange (#f97316).
Font: Inter for UI, Space Grotesk for data labels.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Design tokens (matched to Stitch design system — DARK MODE)
# ---------------------------------------------------------------------------
_SURFACE = "#0f171a"
_CARD_BG = "#1b2427"
_BORDER = "#31393d"
_GRID = "#262e32"
_TEXT_PRIMARY = "#e0e3e5"
_TEXT_SECONDARY = "#c0c7cd"
_TEXT_MUTED = "#8a9297"

_HIST_COLOR = "#98cded"      # Light Blue — historical actual
_PRED_COLOR = "#f97316"      # Orange — scenario predicted
_SECONDARY = "#76d4e7"       # Secondary Blue/Green — positive SHAP bars
_ERROR = "#ffb4ab"           # light red — negative SHAP bars


def _base_layout(**kwargs) -> dict:
    return dict(
        paper_bgcolor=_CARD_BG,
        plot_bgcolor=_CARD_BG,
        font=dict(
            color=_TEXT_SECONDARY,
            family="Inter, system-ui, sans-serif",
            size=14,
        ),
        margin=dict(l=55, r=20, t=40, b=45),
        xaxis=dict(
            gridcolor=_GRID,
            showline=True,
            linecolor=_BORDER,
            zeroline=False,
            tickfont=dict(family="Space Grotesk, monospace", size=11, color=_TEXT_MUTED),
        ),
        yaxis=dict(
            gridcolor=_GRID,
            showline=True,
            linecolor=_BORDER,
            zeroline=False,
            tickfont=dict(family="Space Grotesk, monospace", size=11, color=_TEXT_MUTED),
        ),
        legend=dict(
            bgcolor="rgba(255,255,255,0)",
            bordercolor=_BORDER,
            borderwidth=1,
            font=dict(family="Space Grotesk, monospace", size=12, color=_TEXT_SECONDARY),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        hoverlabel=dict(
            bgcolor=_CARD_BG,
            font_family="Space Grotesk, monospace",
            font_size=13,
            bordercolor=_BORDER,
        ),
        **kwargs,
    )


# ---------------------------------------------------------------------------
# Chart 1 — Time-series comparison
# ---------------------------------------------------------------------------

def plot_comparison(
    hist_df: pd.DataFrame,
    scenario_df: pd.DataFrame,
    target_col: str,
) -> go.Figure:
    """Interactive line chart: historical actual vs. scenario predicted."""
    fig = go.Figure()

    # Historical — solid line
    fig.add_trace(go.Scatter(
        x=hist_df.index,
        y=hist_df[target_col],
        mode="lines",
        name="Historical Data",
        line=dict(color=_HIST_COLOR, width=2.5),
        hovertemplate="%{x|%Y-%m-%d}<br><b>%{y:.4f}</b><extra>Historical</extra>",
    ))

    # Scenario predicted — dashed line
    fig.add_trace(go.Scatter(
        x=scenario_df.index,
        y=scenario_df[target_col],
        mode="lines",
        name="Scenario Projection",
        line=dict(color=_PRED_COLOR, width=2.5, dash="dash"),
        hovertemplate="%{x|%Y-%m-%d}<br><b>%{y:.4f}</b><extra>Predicted</extra>",
    ))

    layout = _base_layout(
        hovermode="x unified",
        height=380,
    )
    fig.update_layout(**layout)
    return fig


# ---------------------------------------------------------------------------
# Chart 2 — SHAP feature importance
# ---------------------------------------------------------------------------

def plot_shap_bar(
    mean_abs_shap: np.ndarray,
    feature_names: list[str],
) -> go.Figure:
    """Horizontal bar chart of mean absolute SHAP values per feature."""
    # Sort ascending for horizontal bars (top = most important)
    order = np.argsort(mean_abs_shap)
    sorted_names = [feature_names[i] for i in order]
    sorted_vals = mean_abs_shap[order]

    # Only show top 10 features
    if len(sorted_names) > 10:
        sorted_names = sorted_names[-10:]
        sorted_vals = sorted_vals[-10:]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=sorted_vals,
        y=sorted_names,
        orientation="h",
        marker=dict(
            color=_SECONDARY,
            opacity=0.8,
            line=dict(width=0),
        ),
        hovertemplate="<b>%{y}</b><br>Mean |SHAP|: %{x:.5f}<extra></extra>",
        name="Feature Impact",
    ))

    layout = _base_layout(
        height=320,
        bargap=0.35,
        showlegend=False,
    )
    fig.update_layout(**layout)
    fig.update_yaxes(
        tickfont=dict(family="Space Grotesk, monospace", size=10, color=_TEXT_SECONDARY),
    )
    fig.update_xaxes(
        title_text="Mean |SHAP Value|",
        title_font=dict(size=10, color=_TEXT_MUTED),
    )
    return fig
