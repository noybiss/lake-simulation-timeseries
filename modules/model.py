"""
model.py — XGBoost training and prediction.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import xgboost as xgb


# ---------------------------------------------------------------------------
# Sensible default hyperparameters for general time-series regression
# ---------------------------------------------------------------------------
DEFAULT_PARAMS: dict = dict(
    n_estimators=400,
    learning_rate=0.05,
    max_depth=5,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=0.1,
    reg_lambda=1.0,
    random_state=42,
    n_jobs=-1,
)


def train(
    X_hist: pd.DataFrame,
    y_hist: pd.Series,
    params: dict | None = None,
) -> xgb.XGBRegressor:
    """Train an XGBoostRegressor on historical data.

    XGBoost handles NaN values natively — no imputation required.

    Parameters
    ----------
    X_hist : pd.DataFrame
        Engineered feature matrix for the historical period.
    y_hist : pd.Series
        Target variable values for the historical period.
    params : dict | None
        Override any default hyperparameters.

    Returns
    -------
    xgb.XGBRegressor — fitted model.
    """
    hp = {**DEFAULT_PARAMS, **(params or {})}
    model = xgb.XGBRegressor(**hp)
    model.fit(X_hist, y_hist, verbose=False)
    return model


def predict(
    model: xgb.XGBRegressor,
    X_scenario: pd.DataFrame,
) -> np.ndarray:
    """Run inference on the scenario feature matrix.

    Returns a 1-D array of predictions aligned to X_scenario's index.
    """
    return model.predict(X_scenario)
