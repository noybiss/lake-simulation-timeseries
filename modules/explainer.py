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

    Uses shap.TreeExplainer which is optimised for tree-based models and is
    fast even for large feature sets.

    Parameters
    ----------
    model : xgb.XGBRegressor
        The fitted XGBoost model.
    X_scenario : pd.DataFrame
        The scenario feature matrix (same columns used during training).

    Returns
    -------
    (mean_abs_shap, feature_names)
        mean_abs_shap : np.ndarray shape (n_features,) — mean |SHAP| per feature.
        feature_names : list[str] — corresponding feature names.
    """
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_scenario)          # shape (n_samples, n_features)

    mean_abs_shap = np.abs(shap_values).mean(axis=0)         # shape (n_features,)
    feature_names = list(X_scenario.columns)

    return mean_abs_shap, feature_names
