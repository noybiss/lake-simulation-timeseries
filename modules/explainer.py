"""
explainer.py — SHAP-based model explanation using TreeExplainer.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import shap
import xgboost as xgb


def compute_shap_values(
    model: xgb.XGBRegressor,
    X_scenario: pd.DataFrame,
) -> tuple[np.ndarray, list[str]]:
    """Compute mean absolute SHAP values for each feature.

    SHAP (SHapley Additive exPlanations) values assign an importance score
    to each feature for each prediction. It is based on cooperative game theory,
    fairly allocating the 'payout' (the prediction deviation from baseline) 
    among the player features.

    Uses shap.TreeExplainer, a high-performance variant optimized specifically 
    for tree-based ensembles (like XGBoost, LightGBM, and Random Forests).
    Unlike kernel explainer approximations, TreeExplainer computes exact SHAP
    values in polynomial time, making it exceptionally fast even with many features.

    Parameters
    ----------
    model : xgb.XGBRegressor
        The fitted XGBoost model.
    X_scenario : pd.DataFrame
        The scenario feature matrix (same columns used during training).

    Returns
    -------
    (mean_abs_shap, feature_names)
        mean_abs_shap : np.ndarray shape (n_features,) — average absolute |SHAP| impact per feature.
        feature_names : list[str] — corresponding feature names.
    """
    # Initialize the TreeExplainer with the trained XGBoost model
    explainer = shap.TreeExplainer(model)
    
    # Calculate SHAP values for the scenario data (yields matrix of shape [n_samples, n_features])
    shap_values = explainer.shap_values(X_scenario)          # shape (n_samples, n_features)

    # Compute the average absolute impact of each feature across all scenario timesteps
    mean_abs_shap = np.abs(shap_values).mean(axis=0)         # shape (n_features,)
    feature_names = list(X_scenario.columns)

    return mean_abs_shap, feature_names
