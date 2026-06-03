"""
app.py — Lake Environment Scenario Predictor
EcoPredict AI · Simulation Engine

All scenarios run automatically on file upload.
Design system: Stitch "Environmental Simulation System" light theme.
"""
from __future__ import annotations

import io
import time
import traceback
import random
import logging

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.model_selection import TimeSeriesSplit

from modules.data_loader import (
    clean_data_issues,
    clean_specific_columns,
    detect_data_issues,
    detect_target_column,
    load_excel,
    normalize_time_index,
    separate_sheets,
    validate_column_match,
)
from modules.explainer import compute_shap_values
from modules.feature_engineering import engineer_features
from modules.model import train, predict
from modules.visualizer import plot_comparison, plot_shap_bar
from modules.logger import save_simulation_log

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="OmniSim AI · Universal Time-Series Simulation",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Design System — "Environmental Simulation System" (Stitch)
# Colors: Corporate / Scientific Minimalism · Light theme
# Fonts: Inter + Space Grotesk
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

    :root {
        color-scheme: dark;
        --primary: #98cded;
        --on-primary: #00354a;
        --primary-container: #004d68;
        --on-primary-container: #c3e8ff;
        --secondary: #76d4e7;
        --on-secondary: #00363d;
        --secondary-container: #004f58;
        --on-secondary-container: #a3eeff;
        --tertiary: #41d8f4;
        --on-tertiary: #00363e;
        --tertiary-container: #004e59;
        --on-tertiary-container: #a7eeff;
        --error: #ffb4ab;
        --on-error: #690005;
        --error-container: #93000a;
        --on-error-container: #ffdad6;
        --surface: #0f171a;
        --surface-dim: #0f171a;
        --surface-bright: #353f43;
        --surface-container-lowest: #0a1215;
        --surface-container-low: #172023;
        --surface-container: #1b2427;
        --surface-container-high: #262e32;
        --surface-container-highest: #31393d;
        --on-surface: #e0e3e5;
        --on-surface-variant: #c0c7cd;
        --outline: #8a9297;
        --outline-variant: #41484d;
        --background: #0f171a;
        --on-background: #e0e3e5;
        --card-bg: #1b2427;
        --border: #31393d;
        --gutter: 24px;
        --card-padding: 20px;
        --stack-gap: 12px;
        
        /* Rounded corners */
        --rounded-sm: 0.125rem;
        --rounded: 0.25rem;
        --rounded-md: 0.375rem;
        --rounded-lg: 0.5rem;
        --rounded-xl: 0.75rem;
    }

    /* ── Reset Streamlit defaults ──────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
        color: var(--on-surface) !important;
    }
    .stApp {
        background: var(--background) !important;
    }
    /* Hide streamlit chrome but keep sidebar toggle */
    #MainMenu, footer,
    .stDeployButton { display: none !important; }
    header[data-testid="stHeader"] {
        background: transparent !important;
        border: none !important;
    }

    /* ── Typography ────────────────────────────────────────── */
    h1, h2, h3 {
        color: var(--on-surface) !important;
    }
    .stMarkdown p, .stMarkdown li, .stMarkdown span {
        color: var(--on-surface-variant) !important;
    }
    h1 {
        font-family: 'Inter', sans-serif !important;
        font-size: 30px !important;
        font-weight: 600 !important;
        line-height: 38px !important;
        letter-spacing: -0.02em !important;
    }
    h2 {
        font-family: 'Inter', sans-serif !important;
        font-size: 24px !important;
        font-weight: 600 !important;
        line-height: 32px !important;
        letter-spacing: -0.01em !important;
    }
    h3 {
        font-family: 'Inter', sans-serif !important;
        font-size: 20px !important;
        font-weight: 600 !important;
        line-height: 28px !important;
    }
    .body-lg {
        font-family: 'Inter', sans-serif !important;
        font-size: 16px !important;
        font-weight: 400 !important;
        line-height: 24px !important;
        color: var(--on-surface-variant) !important;
    }
    .body-sm {
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
        font-weight: 400 !important;
        line-height: 20px !important;
        color: var(--on-surface-variant) !important;
    }
    .label-caps {
        font-family: 'Inter', sans-serif !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        line-height: 16px !important;
        letter-spacing: 0.05em !important;
        text-transform: uppercase !important;
        color: var(--on-surface) !important;
    }
    .mono-data {
        font-family: 'Space Grotesk', monospace !important;
        font-size: 13px !important;
        font-weight: 400 !important;
        line-height: 18px !important;
        color: var(--on-surface) !important;
    }

    /* ── Widget Labels ─────────────────────────────────────── */
    label, [data-testid="stWidgetLabel"] p, [data-testid="stCheckbox"] label {
        color: var(--on-surface) !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }

    /* ── File Uploader ───────────────────────────────────── */
    [data-testid="stFileUploader"] {
        background: transparent !important;
    }
    [data-testid="stFileUploadDropzone"] {
        background: var(--surface-container) !important;
        border: 1px dashed var(--outline) !important;
        border-radius: var(--rounded) !important;
    }
    /* Force high-contrast text on everything inside the uploader */
    [data-testid="stFileUploader"] label,
    [data-testid="stFileUploadDropzone"] div,
    [data-testid="stFileUploadDropzone"] p,
    [data-testid="stFileUploadDropzone"] span,
    [data-testid="stFileUploadDropzone"] small,
    [data-testid="stFileUploadDropzone"] button {
        color: var(--on-surface) !important;
    }
    /* Icon color */
    [data-testid="stFileUploadDropzone"] svg {
        fill: var(--on-surface) !important;
    }

    /* ── Sidebar ──────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: var(--surface-container-low) !important; 
        border-right: 1px solid var(--border) !important;
        width: 320px !important;
    }

    /* ── Cards ────────────────────────────────────────────── */
    .eco-card {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: var(--rounded-lg);
        padding: var(--card-padding);
        position: relative;
        overflow: hidden;
        margin-bottom: var(--stack-gap);
    }
    .eco-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: var(--primary);
    }

    /* ── Secondary Button (Download) ────────────────────── */
    .stDownloadButton > button {
        background: transparent !important;
        color: var(--secondary) !important;
        border: 1px solid var(--secondary) !important;
        border-radius: var(--rounded);
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 0.5rem 1rem;
        text-transform: none !important;
        box-shadow: none !important;
    }
    .stDownloadButton > button:hover {
        background: rgba(118, 212, 231, 0.1) !important;
        transform: none !important;
    }

    /* ── Primary Action Button (Run) ─────────────────────── */
    .stButton > button[kind="primary"] {
        background: var(--primary) !important;
        color: var(--on-primary) !important;
        border: none !important;
        border-radius: var(--rounded);
        font-weight: 700 !important;
    }

    /* ── Metric boxes ────────────────────────────────────── */
    [data-testid="stMetric"] {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: var(--rounded);
        padding: 1rem;
    }
    [data-testid="stMetricValue"] {
        font-family: 'Space Grotesk', monospace !important;
        font-size: 24px !important;
        font-weight: 400 !important;
        color: var(--on-surface) !important;
    }
    [data-testid="stMetricLabel"] {
        font-family: 'Inter', sans-serif !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        letter-spacing: 0.05em !important;
        text-transform: uppercase !important;
        color: var(--on-surface-variant) !important;
    }

    /* ── Tabs ─────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 1px solid var(--border);
        background: transparent !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Inter', sans-serif !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: var(--on-surface-variant);
        background: transparent !important;
    }
    .stTabs [aria-selected="true"] {
        color: var(--primary) !important;
        border-bottom: 2px solid var(--primary) !important;
    }

    /* ── Target badge ────────────────────────────────────── */
    .target-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.2rem 0.65rem;
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        border-radius: 4px;
    }
    .target-badge.primary {
        background: #064e3b;
        color: #d1fae5;
        border: 1px solid #065f46;
    }
    .target-badge.secondary {
        background: #1e293b;
        color: #e2e8f0;
        border: 1px solid #334155;
    }

    /* ── Status indicator / Chips ────────────────────────── */
    .status-dot {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-dot.live { background: #10b981; }
    .status-dot.error { background: #ef4444; }

    .status-chip {
        display: inline-flex;
        align-items: center;
        padding: 2px 10px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .status-chip.success {
        background: #064e3b;
        color: #d1fae5;
        border: 1px solid #065f46;
    }
    .status-chip.running {
        background: #0c4a6e;
        color: #e0f2fe;
        border: 1px solid #075985;
    }
    .status-chip.error {
        background: #7f1d1d;
        color: #fef2f2;
        border: 1px solid #991b1b;
    }

    /* ── Label caps ──────────────────────────────────────── */
    .label-caps {
        font-size: 0.75rem;
        font-weight: 800;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: var(--on-surface);
    }

    /* ── Mono data ───────────────────────────────────────── */
    .mono-data {
        font-family: 'Space Grotesk', monospace;
        font-size: 0.85rem;
        font-weight: 500;
        color: var(--on-surface);
    }

    /* ── Explanation text ────────────────────────────────── */
    .explain {
        font-size: 0.88rem;
        line-height: 1.6;
        color: var(--on-surface-variant);
        margin-bottom: 1.2rem;
    }

    /* ── Footer bar ──────────────────────────────────────── */
    .footer-bar {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
        margin-top: 3rem;
        padding: 1.5rem;
        background: var(--surface-container-low);
        border: 1px solid var(--border);
        border-radius: 8px;
    }
    .footer-bar .label-caps { margin-bottom: 0.4rem; color: var(--on-surface-variant); }
    .footer-bar .value {
        font-size: 0.95rem;
        font-weight: 700;
        color: var(--primary);
    }

    /* ── Expander sections ───────────────────────────────── */
    .streamlit-expanderHeader {
        background: var(--card-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--rounded) !important;
        padding: 1rem 1.2rem !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        color: var(--on-surface) !important;
    }
    .streamlit-expanderContent {
        background: var(--surface-container-low) !important;
        border: 1px solid var(--border) !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
        padding: 1.2rem !important;
        margin-top: -1px !important;
    }
    .streamlit-expanderContent h3 {
        color: var(--primary) !important;
        font-size: 1.1rem !important;
        font-weight: 800 !important;
        margin: 1.2rem 0 0.6rem 0 !important;
    }
    .streamlit-expanderContent p,
    .streamlit-expanderContent li {
        color: var(--on-surface-variant) !important;
        font-size: 0.9rem !important;
        line-height: 1.7 !important;
    }
    .streamlit-expanderContent strong {
        color: var(--on-surface) !important;
        font-weight: 700 !important;
    }
    .streamlit-expanderContent code {
        background: #1e293b !important;
        color: var(--primary) !important;
        padding: 0.2rem 0.4rem !important;
        border-radius: 4px !important;
        font-family: 'Space Grotesk', monospace !important;
        font-size: 0.85rem !important;
        border: 1px solid #334155;
    }

    /* ── Markdown content ───────────────────────────────── */
    .stMarkdown {
        color: var(--on-surface) !important;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: var(--primary) !important;
        font-weight: 800 !important;
        margin-top: 1.5rem !important;
    }
    .stMarkdown p, .stMarkdown li {
        color: var(--on-surface-variant) !important;
        line-height: 1.7 !important;
        font-size: 0.95rem !important;
    }
    .stMarkdown strong {
        color: var(--on-surface) !important;
        font-weight: 700 !important;
    }
    .stMarkdown code {
        background: #1e293b !important;
        color: var(--primary) !important;
        padding: 0.2rem 0.4rem !important;
        border-radius: 4px !important;
        font-family: 'Space Grotesk', monospace !important;
        border: 1px solid #334155;
    }

    /* ── Info/Warning/Success boxes ───────────────────────── */
    .stInfo, .stWarning, .stSuccess, .stError {
        background: var(--surface-container-low) !important;
        border: 1px solid var(--border) !important;
        border-left: 5px solid var(--outline) !important;
        border-radius: 8px !important;
        padding: 1.2rem !important;
    }
    .stInfo { border-left-color: #3b82f6 !important; }
    .stWarning { border-left-color: #f59e0b !important; }
    .stSuccess { border-left-color: #10b981 !important; }
    .stError { border-left-color: #ef4444 !important; }

    .stInfo p, .stWarning p, .stSuccess p, .stError p {
        color: var(--on-surface) !important;
        font-size: 0.92rem !important;
        font-weight: 500 !important;
    }

    /* ── Buttons ────────────────────────────────────────── */
    .stButton > button {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        border-radius: 6px !important;
        padding: 0.5rem 1.2rem !important;
    }
    .stButton > button[kind="primary"] {
        background: var(--primary) !important;
        color: var(--on-primary) !important;
        border: none !important;
    }

    /* ── Headers in alert boxes ───────────────────────────── */
    .stAlert h3 {
        color: var(--primary) !important;
        font-size: 1.1rem !important;
        font-weight: 800 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar — branding + file upload
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div style="padding:1.5rem 1rem 1rem;">
            <h1 style="font-size:20px; font-weight:600; color:var(--primary); margin:0; letter-spacing:-0.01em; line-height:1.2;">
                Environmental<br>Simulation System
            </h1>
            <p class="label-caps" style="margin-top:0.5rem; color:var(--outline); font-size:10px;">
                OmniSim AI · Scenario Engine
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Upload Dataset",
        type=["xls", "xlsx"],
        help="Excel file: Sheet 1 = Historical, Sheet 2+ = Scenarios (one column empty).",
    )

    st.markdown("---")
    st.markdown(
        """
        <div style="padding:0 0.5rem;">
            <p class="label-caps" style="margin-bottom:0.6rem;">How it works</p>
            <ol class="body-sm" style="color:var(--on-surface-variant); line-height:1.6; padding-left:1.1rem; margin:0;">
                <li><b>Upload</b> an Excel file (.xls / .xlsx)</li>
                <li>Sheet 1 is your <b>Historical</b> data</li>
                <li>Sheets 2+ are <b>Scenarios</b></li>
                <li>Each scenario has <b>one empty column</b> — that's the target</li>
                <li>Model trains on history, predicts missing scenario values</li>
                <li>SHAP analysis shows <b>key drivers</b></li>
            </ol>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="position:fixed;bottom:0;left:0;width:320px;padding:1rem;
                     border-top:1px solid var(--border);background:var(--surface-container-low);">
            <p class="label-caps" style="font-size:10px; color:var(--outline); margin:0; line-height:1.4;">
                OmniSim AI · XGBoost + SHAP<br>
                <span style="color:var(--primary); font-weight:800;">Made and Designed by OA</span>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Helper: run full pipeline for one scenario (cached)
# ---------------------------------------------------------------------------
def _run_scenario(
    historical_raw: pd.DataFrame,
    scenario_raw: pd.DataFrame,
    scenario_name: str,
) -> dict | str:
    """
    Run the full ML pipeline for a single scenario.
    
    This function orchestrates the entire simulation process for a given scenario:
    1. Validates the structural integrity of the input data.
    2. Identifies the target variable (the missing column in the scenario).
    3. Normalizes time indices for consistent time-series alignment.
    4. Engineers lag and rolling features for the historical data.
    5. Trains an XGBoost model on the historical feature set.
    6. Generates predictions to fill the missing values in the scenario.
    7. Computes model performance metrics (R², RMSE) and SHAP values for explainability.
    
    Returns:
        A dictionary containing the simulation results, or a string describing an error.
    """
    # 1. Structural validation: Ensure scenario columns match historical columns (except for the target)
    try:
        validate_column_match(historical_raw, scenario_raw)
    except ValueError as e:
        return str(e)

    # 2. Target identification: Find the single completely empty column in the scenario
    try:
        target_col = detect_target_column(scenario_raw)
    except ValueError as e:
        return str(e)

    # 3. Time normalization: Set Datetime index to ensure strict chronological ordering
    try:
        hist_df = normalize_time_index(historical_raw)
        scen_df = normalize_time_index(scenario_raw)
    except ValueError as e:
        return str(e)

    # 4. Feature engineering: Extract temporal features, lags, and rolling averages
    X_hist, y_hist = engineer_features(hist_df, target_col=target_col)
    X_scen, _ = engineer_features(scen_df, target_col=target_col)
    
    # Align scenario features with historical features (fill missing with NaN to prevent bias, XGBoost handles NaNs natively)
    X_scen = X_scen.reindex(columns=X_hist.columns, fill_value=np.nan)

    # 5. Model Optimization & Training
    
    # ── Beautiful Live Optimization UI ──
    st.markdown(
        f"""
        <div style="padding:1rem; background:var(--surface-container-low); border-left:4px solid var(--primary); border-radius:var(--rounded); margin-bottom:1rem;">
            <h4 style="margin:0; color:var(--primary); font-size:16px;">🚀 Hyperparameter Optimization: {scenario_name}</h4>
            <p class="body-sm" style="margin:0.2rem 0 0; color:var(--on-surface-variant);">Searching for the optimal model configuration using Time-Series Cross-Validation...</p>
        </div>
        """, unsafe_allow_html=True
    )
    
    col_chart, col_stats = st.columns([2, 1], gap="large")
    with col_chart:
        chart_placeholder = st.empty()
    with col_stats:
        stats_placeholder = st.empty()
        
    opt_progress = st.progress(0)
    
    best_cv_r2 = -float("inf")
    best_cv_rmse = float("inf")
    best_params = {}
    history_r2 = []
    
    n_iterations = 15
    t0 = time.time()
    
    # Fix random seed for reproducibility
    random.seed(42)
    
    try:
        # TimeSeriesSplit ensures we never train on future data to predict the past
        tscv = TimeSeriesSplit(n_splits=4)
        
        for i in range(n_iterations):
            # Generate random hyperparameters
            lr = random.uniform(0.01, 0.2)
            max_depth = random.randint(3, 8)
            n_estimators = random.randint(100, 500)
            
            params = {
                "learning_rate": lr,
                "max_depth": max_depth,
                "n_estimators": n_estimators,
            }
            
            fold_r2s = []
            fold_rmses = []
            
            # Cross-validate the current parameter set
            for train_idx, val_idx in tscv.split(X_hist):
                X_t, X_v = X_hist.iloc[train_idx], X_hist.iloc[val_idx]
                y_t, y_v = y_hist.iloc[train_idx], y_hist.iloc[val_idx]
                
                fold_model = train(X_t, y_t, params=params)
                y_v_pred = predict(fold_model, X_v)
                
                fold_r2s.append(r2_score(y_v, y_v_pred))
                fold_rmses.append(np.sqrt(mean_squared_error(y_v, y_v_pred)))
            
            current_cv_r2 = np.mean(fold_r2s)
            current_cv_rmse = np.mean(fold_rmses)
            
            # Track best cross-validated model parameters
            if current_cv_r2 > best_cv_r2:
                best_cv_r2 = current_cv_r2
                best_cv_rmse = current_cv_rmse
                best_params = params
                
            # Plot the progression
            history_r2.append({"Iteration": i + 1, "Current CV R²": current_cv_r2, "Best CV R²": best_cv_r2})
            chart_df = pd.DataFrame(history_r2).set_index("Iteration")
            
            # Update live chart
            chart_placeholder.line_chart(chart_df, color=["#41d8f4", "#10b981"], height=220)
            
            # Update live stats card
            stats_placeholder.markdown(
                f"""
                <div style="background:var(--surface-container-highest); padding:1.2rem; border-radius:var(--rounded-lg); border:1px solid var(--border); height:220px; display:flex; flex-direction:column; justify-content:center;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                        <span class="label-caps" style="color:var(--on-surface-variant);">Iteration</span>
                        <span class="mono-data" style="color:var(--primary); font-weight:700;">{i+1} / {n_iterations}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                        <span class="label-caps" style="color:var(--on-surface-variant);">CV R²</span>
                        <span class="mono-data" style="color:var(--tertiary); font-weight:700;">{current_cv_r2:.4f}</span>
                    </div>
                    <hr style="width:100%; border:none; border-top:1px dashed var(--outline-variant); margin:0 0 1rem 0;">
                    <p class="label-caps" style="color:#10b981; margin:0 0 0.2rem 0; display:flex; align-items:center; gap:0.3rem;">
                        <span class="material-symbols-outlined" style="font-size:14px;">trophy</span> Best CV R²
                    </p>
                    <p class="mono-data" style="font-size:28px; color:#10b981; font-weight:800; margin:0 0 0.5rem 0;">{best_cv_r2:.4f}</p>
                    <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:0.5rem; text-align:center;">
                        <div style="background:var(--surface-container-lowest); padding:0.3rem; border-radius:4px;">
                            <div style="font-size:9px; color:var(--outline); text-transform:uppercase; font-weight:700;">LR</div>
                            <div class="mono-data" style="font-size:11px;">{best_params['learning_rate']:.3f}</div>
                        </div>
                        <div style="background:var(--surface-container-lowest); padding:0.3rem; border-radius:4px;">
                            <div style="font-size:9px; color:var(--outline); text-transform:uppercase; font-weight:700;">Depth</div>
                            <div class="mono-data" style="font-size:11px;">{best_params['max_depth']}</div>
                        </div>
                        <div style="background:var(--surface-container-lowest); padding:0.3rem; border-radius:4px;">
                            <div style="font-size:9px; color:var(--outline); text-transform:uppercase; font-weight:700;">Trees</div>
                            <div class="mono-data" style="font-size:11px;">{best_params['n_estimators']}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True
            )
            
            opt_progress.progress((i + 1) / n_iterations)
            time.sleep(0.15)
            
        opt_progress.empty()
        
        # Finally, train the best model on the FULL historical dataset
        model = train(X_hist, y_hist, params=best_params)
        r2 = best_cv_r2
        rmse = best_cv_rmse
        
    except Exception as e:
        return f"Model optimization failed: {e}"
        
    train_time = time.time() - t0

    # Show a live status indicator for the finalization phase
    finalize_msg = st.empty()
    finalize_msg.markdown(
        f"""
        <div style="padding:0.75rem 1rem;background:var(--surface-container-low);border-left:4px solid var(--tertiary);border-radius:var(--rounded);margin-bottom:1rem;">
            <p class="body-sm" style="margin:0;color:var(--tertiary);font-weight:600;display:flex;align-items:center;gap:0.5rem;">
                <span class="material-symbols-outlined" style="animation: spin 2s linear infinite;">sync</span>
                Finalizing model predictions and calculating SHAP explanations...
            </p>
        </div>
        <style>@keyframes spin {{ 100% {{ transform:rotate(360deg); }} }}</style>
        """,
        unsafe_allow_html=True,
    )

    # 6. Prediction: Predict the missing target variable in the scenario
    preds = predict(model, X_scen)
    scen_filled = scen_df.copy()
    scen_filled[target_col] = preds

    # 8. Explainability: Calculate SHAP values to identify key drivers
    try:
        mean_shap, feat_names = compute_shap_values(model, X_scen)
    except Exception as e:
        logging.error(f"SHAP computation failed for {scenario_name}: {e}")
        mean_shap, feat_names = None, None

    # Clear the finalizing message once done
    finalize_msg.empty()

    return dict(
        target_col=target_col,
        hist_df=hist_df,
        scen_filled=scen_filled,
        r2=r2,
        rmse=rmse,
        train_time=train_time,
        n_features=len(X_hist.columns),
        mean_shap=mean_shap,
        feat_names=feat_names,
        model=model,
    )


# ---------------------------------------------------------------------------
# Main content area
# ---------------------------------------------------------------------------
if uploaded is None:
    # Empty state
    st.markdown(
        """
        <div style="display:flex;align-items:center;justify-content:center;height:70vh;flex-direction:column;">
            <span class="material-symbols-outlined" style="font-size:64px;color:var(--outline-variant);margin-bottom:1rem;">science</span>
            <h2 style="margin:0;">No dataset loaded</h2>
            <p class="body-lg" style="color:var(--on-surface-variant);margin:0.5rem 0 0;max-width:480px;text-align:center;">
                Upload an Excel file using the sidebar to begin.
                The simulator will automatically process <b>all scenarios</b> and display the results.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# ---------------------------------------------------------------------------
# Process uploaded file
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div style="padding:1rem 1.5rem;background:var(--surface-container-low);border-left:4px solid var(--primary-container);border-radius:var(--rounded);margin-bottom:1.5rem;">
        <h3 style="margin:0 0 0.25rem 0;color:var(--primary-container);font-size:16px;">📋 File Analysis Started</h3>
        <p class="body-sm" style="margin:0;color:var(--on-surface-variant);">Reading your Excel file and preparing the simulation environment...</p>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    sheets = load_excel(uploaded)
    st.markdown(
        f"""
        <div style="padding:0.75rem 1rem;background:#064e3b;border-left:4px solid #10b981;border-radius:var(--rounded);margin-bottom:1rem;">
            <p class="body-sm" style="margin:0;color:#d1fae5;font-weight:600;">
                ✅ Successfully loaded <strong>{len(sheets)} sheet(s)</strong> from your Excel file
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    historical_raw, scenarios = separate_sheets(sheets)
    st.markdown(
        f"""
        <div style="padding:0.75rem 1rem;background:#064e3b;border-left:4px solid #10b981;border-radius:var(--rounded);margin-bottom:1rem;">
            <p class="body-sm" style="margin:0;color:#d1fae5;font-weight:600;">
                ✅ Identified <strong>1 Historical sheet</strong> and <strong>{len(scenarios)} Scenario sheet(s)</strong>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
except ValueError as e:
    st.markdown(
        f"""
        <div style="padding:1rem 1.5rem;background:var(--error-container);border-left:4px solid var(--error);border-radius:var(--rounded);margin-bottom:1.5rem;">
            <h3 style="margin:0 0 0.25rem 0;color:var(--error);font-size:16px;">❌ File Structure Error</h3>
            <p class="body-sm" style="margin:0;color:var(--on-error-container);">{e}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()
except Exception as e:
    st.markdown(
        f"""
        <div style="padding:1rem 1.5rem;background:var(--error-container);border-left:4px solid var(--error);border-radius:var(--rounded);margin-bottom:1.5rem;">
            <h3 style="margin:0 0 0.25rem 0;color:var(--error);font-size:16px;">❌ File Reading Error</h3>
            <p class="body-sm" style="margin:0;color:var(--on-error-container);">Failed to read the Excel file: {e}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

if not scenarios:
    st.markdown(
        """
        <div style="padding:1rem 1.5rem;background:var(--surface-container-highest);border-left:4px solid var(--outline);border-radius:var(--rounded);margin-bottom:1.5rem;">
            <h3 style="margin:0 0 0.25rem 0;color:var(--primary);font-size:16px;">⚠️ No Scenarios Found</h3>
            <p class="body-sm" style="margin:0;color:var(--on-surface-variant);">Your Excel file must have at least 2 sheets: Sheet 1 (Historical) + Sheet 2+ (Scenarios)</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# ---------------------------------------------------------------------------
# Data Quality Check
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div style="padding:1rem 1.5rem;background:var(--surface-container-low);border-left:4px solid var(--primary-container);border-radius:var(--rounded);margin-bottom:1.5rem;">
        <h3 style="margin:0 0 0.25rem 0;color:var(--primary-container);font-size:16px;">🔍 Data Quality Analysis</h3>
        <p class="body-sm" style="margin:0;color:var(--on-surface-variant);">Scanning your data for potential issues...</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Allow users to customize missing data placeholders
st.markdown("### ⚙️ Missing Data Settings")
st.markdown("*Configure which values should be treated as missing data:*")

st.info("💡 **Note**: -1 is no longer treated as missing data by default, as it can be a valid value (e.g., -1°C temperature). Only use it as a missing value placeholder if you're certain -1 never occurs in your real data.")

col1, col2 = st.columns(2)

with col1:
    default_missing = st.checkbox(
        "Use default missing values (-999, -9999, 999, 9999)",
        value=True,
        help="Common placeholders used to indicate missing data in scientific datasets"
    )

with col2:
    custom_missing = st.text_input(
        "Additional missing values (comma-separated)",
        placeholder="e.g., -1, 0, 99999",
        help="Add any other values that should be treated as missing data"
    )

# Outlier detection settings
st.markdown("### 📊 Outlier Detection Settings")
st.markdown("*Adjust how aggressively the system detects statistical outliers:*")

col3, col4 = st.columns(2)

with col3:
    iqr_threshold = st.slider(
        "IQR Threshold",
        min_value=1.5,
        max_value=5.0,
        value=3.0,
        step=0.5,
        help="Higher values = fewer outliers detected. 3.0 is standard, 1.5 is very strict, 5.0 is very lenient."
    )

with col4:
    show_outlier_details = st.checkbox(
        "Show detailed outlier information",
        value=True,
        help="Display sample values and ranges for detected outliers"
    )

# Build the missing placeholders list
missing_placeholders = []
if default_missing:
    missing_placeholders = [-999.0, -9999.0, 999.0, 9999.0]

if custom_missing:
    try:
        custom_values = [float(x.strip()) for x in custom_missing.split(',') if x.strip()]
        missing_placeholders.extend(custom_values)
    except ValueError:
        st.warning("⚠️ Invalid format in custom missing values. Please use comma-separated numbers.")

all_sheets = {"Historical": historical_raw, **scenarios}
issues_report = detect_data_issues(all_sheets, missing_placeholders=missing_placeholders if missing_placeholders else None, iqr_threshold=iqr_threshold)

total_issues = sum(sheet['total_issues'] for sheet in issues_report.values())

if total_issues > 0:
    st.markdown(
        f"""
        <div style="padding:1rem 1.5rem;background:var(--surface-container-highest);border-left:4px solid var(--tertiary);border-radius:var(--rounded);margin-bottom:1.5rem;">
            <h3 style="margin:0 0 0.25rem 0;color:var(--tertiary);font-size:16px;">⚠️ Data Issues Detected</h3>
            <p class="body-sm" style="margin:0;color:var(--on-surface-variant);">Found <strong>{total_issues} problematic data points</strong> across your sheets.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Track which columns to clean
    columns_to_clean = {
        'missing_placeholders': [],
        'outliers': []
    }

    # Display detailed issues with per-column controls
    for sheet_name, sheet_issues in issues_report.items():
        if sheet_issues['total_issues'] == 0:
            continue

        with st.expander(f"📊 {sheet_name} — {sheet_issues['total_issues']} issues found", expanded=False):
            # Missing placeholders
            if sheet_issues['missing_placeholders']:
                st.markdown("### 🚫 Missing Data Placeholders")
                st.markdown("*Values that represent missing data:*")
                for col, placeholders in sheet_issues['missing_placeholders'].items():
                    with st.container():
                        col_row1, col_row2 = st.columns([3, 1])
                        with col_row1:
                            st.markdown(f"**{col}**")
                            for p in placeholders:
                                st.markdown(f"- `{p['value']}` appears **{p['count']}** times ({p['percentage']:.1f}%)")
                        with col_row2:
                            clean_this = st.checkbox(
                                f"Clean {col}",
                                key=f"clean_missing_{sheet_name}_{col}",
                                value=True,
                                help="Replace these values with NaN"
                            )
                            if clean_this and col not in columns_to_clean['missing_placeholders']:
                                columns_to_clean['missing_placeholders'].append((sheet_name, col))

            # Outliers
            if sheet_issues['outliers']:
                st.markdown("### 📈 Statistical Outliers")
                st.markdown(f"*Values outside the normal range (IQR threshold: {iqr_threshold}):*")
                for col, outlier_info in sheet_issues['outliers'].items():
                    with st.container():
                        col_row1, col_row2 = st.columns([3, 1])
                        with col_row1:
                            st.markdown(f"**{col}**: **{outlier_info['count']}** outliers ({outlier_info['percentage']:.1f}%)")
                            st.markdown(f"  - Normal range: `{outlier_info['lower_bound']:.2f}` to `{outlier_info['upper_bound']:.2f}`")
                            if show_outlier_details and outlier_info['outlier_values']:
                                st.markdown(f"  - Sample outliers: `{', '.join(f'{v:.2f}' for v in outlier_info['outlier_values'][:5])}`")
                        with col_row2:
                            clean_this = st.checkbox(
                                f"Clean {col}",
                                key=f"clean_outlier_{sheet_name}_{col}",
                                value=False,  # Default to False for outliers since they might be valid
                                help="Replace these values with NaN"
                            )
                            if clean_this and col not in columns_to_clean['outliers']:
                                columns_to_clean['outliers'].append((sheet_name, col))

            # Extreme values
            if sheet_issues['extreme_values']:
                st.markdown("### 🔥 Extreme Value Ranges")
                st.markdown("*Columns with unusually large value ranges:*")
                for col, ext_info in sheet_issues['extreme_values'].items():
                    st.markdown(f"- **{col}**: Range `{ext_info['min']:.2f}` to `{ext_info['max']:.2f}`")
                    st.markdown(f"  - Mean: `{ext_info['mean']:.2f}`, Std: `{ext_info['std']:.2f}`")

            # Recommendations
            if sheet_issues['recommendations']:
                st.markdown("### 💡 Recommendations")
                for rec in sheet_issues['recommendations']:
                    st.markdown(f"- {rec}")

    # Summary of what will be cleaned
    st.markdown("---")
    st.markdown("### 📋 Summary of Selected Actions")

    total_to_clean = len(columns_to_clean['missing_placeholders']) + len(columns_to_clean['outliers'])

    if total_to_clean > 0:
        st.markdown(f"**You've selected {total_to_clean} column(s) to clean:**")

        if columns_to_clean['missing_placeholders']:
            st.markdown("**Missing Data Placeholders:**")
            for sheet_name, col in columns_to_clean['missing_placeholders']:
                st.markdown(f"- {sheet_name}: {col}")

        if columns_to_clean['outliers']:
            st.markdown("**Statistical Outliers:**")
            for sheet_name, col in columns_to_clean['outliers']:
                st.markdown(f"- {sheet_name}: {col}")
    else:
        st.info("No columns selected for cleaning. All data will be processed as-is.")

    # Action buttons
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        clean_data = st.button(
            f"✅ Clean Selected ({total_to_clean})",
            type="primary",
            use_container_width=True,
            disabled=total_to_clean == 0,
            help="Replace selected problematic values with NaN"
        )

    with col2:
        proceed_as_is = st.button(
            "⏭️ Proceed as-is",
            use_container_width=True,
            help="Continue with original data"
        )

    if clean_data:
        st.markdown(
            f"""
            <div style="padding:0.75rem 1rem;background:#064e3b;border-left:4px solid #10b981;border-radius:var(--rounded);margin-bottom:1.5rem;">
                <p class="body-sm" style="margin:0;color:#d1fae5;font-weight:600;">
                    ✅ Data Cleaning Applied. Proceeding with simulation...
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Clean specific columns based on user selection
        cleaned_sheets = clean_specific_columns(
            all_sheets,
            issues_report,
            columns_to_clean,
            missing_placeholders=missing_placeholders if missing_placeholders else None
        )

        # Update the main data structures
        historical_raw = cleaned_sheets["Historical"]
        scenarios = {name: cleaned_sheets[name] for name in scenarios.keys()}

        st.success(f"Successfully cleaned {total_to_clean} column(s)! Proceeding with simulation...")

    elif not proceed_as_is:
        st.warning("⚠️ Action required: Please choose either 'Clean Selected' or 'Proceed as-is' above to continue the simulation.")
        st.stop()

else:
    st.markdown(
        """
        <div style="padding:1rem 1.5rem;background:#064e3b;border-left:4px solid #10b981;border-radius:4px;margin-bottom:1.5rem;">
            <h3 style="margin:0 0 0.5rem 0;color:#10b981;font-size:1rem;font-weight:700;">✅ No Data Issues Found</h3>
            <p style="margin:0;font-size:0.85rem;color:#d1fae5;font-weight:500;">Your data looks good! No problematic values detected.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Automatically run ALL scenarios
# ---------------------------------------------------------------------------
results: dict[str, dict] = {}
errors: dict[str, str] = {}

progress_bar = st.progress(0, text="Running simulations…")
scenario_items = list(scenarios.items())

for idx, (scen_name, scen_df) in enumerate(scenario_items):
    progress_bar.progress(
        (idx + 1) / len(scenario_items),
        text=f"Processing {scen_name}…"
    )
    result = _run_scenario(historical_raw.copy(), scen_df.copy(), scen_name)
    if isinstance(result, str):
        errors[scen_name] = result
    else:
        results[scen_name] = result
        # Log successful simulation results for future AI analysis
        save_simulation_log(scen_name, result)

progress_bar.empty()

# Show errors if any
for scen_name, err_msg in errors.items():
    st.error(f"**{scen_name}** — {err_msg}")

if not results:
    st.error("All scenarios failed. Please check your Excel file.")
    st.stop()

# ---------------------------------------------------------------------------
# Render results — one tab per scenario (auto-generated)
# ---------------------------------------------------------------------------
tab_names = list(results.keys())
tabs = st.tabs(tab_names)

for tab, scen_name in zip(tabs, tab_names):
    res = results[scen_name]

    with tab:
        # ── Header ─────────────────────────────────────────────────
        col_title, col_download = st.columns([4, 1])
        with col_title:
            st.markdown(
                f"""
                <div style="margin-bottom:0.3rem;">
                    <span class="status-dot live"></span>
                    <span class="label-caps" style="color:var(--primary);">Prediction Complete</span>
                </div>
                <h2 style="margin:0;">
                    {scen_name}
                </h2>
                """,
                unsafe_allow_html=True,
            )
        with col_download:
            # Use German formatting: semicolon separator and comma for decimals
            csv_bytes = res["scen_filled"].to_csv(sep=';', decimal=',').encode("utf-8")
            safe_name = scen_name.replace("Scenario: ", "").replace(" ", "_")
            st.download_button(
                label="⬇ Download CSV",
                data=csv_bytes,
                file_name=f"{safe_name}_predicted.csv",
                mime="text/csv",
                key=f"dl_{scen_name}",
            )

        # ── Metrics strip ──────────────────────────────────────────
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Accuracy (R²)", f"{res['r2']:.4f}", help="R-squared score. Measures how well the model predicts the target. 1.0 is perfect, 0.0 means it's just guessing the average.")
        m2.metric("Avg Error (RMSE)", f"{res['rmse']:.5f}", help="Root Mean Squared Error. The average absolute difference between the predicted and actual values. Lower is better.")
        m3.metric("Target Variable", res["target_col"], help="The specific column from your scenario sheet that the AI is attempting to predict.")
        m4.metric("Factors", str(res["n_features"]), help="The total number of historical data columns (including engineered features like lags) the model used to make its prediction.")

        st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

        # ── Main chart: time-series comparison ─────────────────────
        st.markdown(
            f'''
            <div class="eco-card">
                <h3 title="This chart compares the historical data (light blue) against the AI's projections for the target variable in the scenario (orange dashed line).">
                    Target Variable Prediction 
                    <span class="material-symbols-outlined" style="font-size:16px; vertical-align:middle; color:var(--outline); cursor:help;">info</span>
                </h3>
            ''',
            unsafe_allow_html=True,
        )
        fig_ts = plot_comparison(res["hist_df"], res["scen_filled"], res["target_col"])
        st.plotly_chart(fig_ts, use_container_width=True, config={"displayModeBar": True})
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        # ── Bottom section: SHAP + Data Summary side by side ───────
        col_shap, col_summary = st.columns([2, 1], gap="medium")

        with col_shap:
            st.markdown(
                f'''
                <div class="eco-card">
                    <h3 title="SHAP (SHapley Additive exPlanations) values show which historical factors most heavily influenced the AI's predictions.">
                        AI Decision Factors (SHAP)
                        <span class="material-symbols-outlined" style="font-size:16px; vertical-align:middle; color:var(--outline); cursor:help;">info</span>
                    </h3>
                    <p class="body-sm" style="color:var(--on-surface-variant); margin-bottom:1rem;">Which factors moved the needle? Longer bars mean a larger impact.</p>
                ''',
                unsafe_allow_html=True,
            )
            if res["mean_shap"] is not None:
                fig_shap = plot_shap_bar(res["mean_shap"], res["feat_names"])
                st.plotly_chart(fig_shap, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("AI Logic Breakdown is not available for this scenario.")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_summary:
            st.markdown(
                f'''
                <div class="eco-card">
                    <h3 title="A quick summary of the model's accuracy, prediction target, and training speed.">
                        Scorecard
                        <span class="material-symbols-outlined" style="font-size:16px; vertical-align:middle; color:var(--outline); cursor:help;">info</span>
                    </h3>
                ''',
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div style="padding:0.75rem; background:var(--surface-container-low); border-radius:var(--rounded); border:1px solid var(--border); margin-bottom:0.75rem;" title="Root Mean Squared Error. The average absolute difference between predicted and actual values. Lower is better.">
                    <p class="label-caps" style="margin:0 0 0.2rem;">Avg Error (RMSE)</p>
                    <p class="mono-data" style="font-size:20px; font-weight:600; color:var(--primary); margin:0;">
                        {res['rmse']:.5f}
                    </p>
                </div>
                <div style="padding:0.75rem; background:var(--surface-container-low); border-radius:var(--rounded); border:1px solid var(--border); margin-bottom:0.75rem;" title="R-squared score. Measures how well the model predicts the target. 1.0 is perfect, 0.0 means it is guessing the average.">
                    <p class="label-caps" style="margin:0 0 0.2rem;">R² Score</p>
                    <p class="mono-data" style="font-size:20px; font-weight:600; color:var(--primary); margin:0;">
                        {res['r2']:.4f}
                    </p>
                </div>
                <div style="padding:0.75rem; background:var(--surface-container-low); border-radius:var(--rounded); border:1px solid var(--border); margin-bottom:0.75rem;" title="The specific column from your scenario sheet that the AI is attempting to predict.">
                    <p class="label-caps" style="margin:0 0 0.2rem;">What we predicted</p>
                    <div style="margin-top:0.4rem;">
                        <span class="target-badge primary">{res['target_col']}</span>
                    </div>
                </div>
                <div style="padding:0.75rem; background:var(--surface-container-low); border-radius:var(--rounded); border:1px solid var(--border);" title="The time it took for the AI model to train on the historical data.">
                    <p class="label-caps" style="margin:0 0 0.2rem;">Learning Speed</p>
                    <p class="mono-data" style="font-size:16px; font-weight:600; color:var(--primary); margin:0;">
                        {res['train_time']*1000:.0f}ms
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Footer: model metadata ─────────────────────────────────
        st.markdown(
            f"""
            <div class="footer-bar" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem; margin-top: 2rem; padding: 1.5rem; background: var(--card-bg); border: 1px solid var(--border); border-radius: var(--rounded-lg);">
                <div title="The underlying machine learning algorithm used. XGBoost is an advanced gradient boosting algorithm.">
                    <p class="label-caps">Brain Type</p>
                    <p class="body-sm" style="font-weight:700; color:var(--primary); margin:0;">XGBoost Regressor</p>
                </div>
                <div title="Indicates whether the model successfully learned from the data without encountering errors.">
                    <p class="label-caps">Study Status</p>
                    <div style="margin-top:0.2rem;">
                        <span class="status-chip success">Converged</span>
                    </div>
                </div>
                <div title="The total execution time for training the model on this scenario's data.">
                    <p class="label-caps">Calculation</p>
                    <p class="body-sm" style="font-weight:700; color:var(--primary); margin:0;">{res['train_time']*1000:.0f}ms Total</p>
                </div>
                <div title="The number of historical records used to train the AI. More rows generally lead to better predictions.">
                    <p class="label-caps">Data Volume</p>
                    <p class="body-sm" style="font-weight:700; color:var(--primary); margin:0;">{len(res['hist_df'])} Rows</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
