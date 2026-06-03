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
# These parameters are tuned specifically to prevent overfitting on time-series
# data, which typically has highly correlated observations.
DEFAULT_PARAMS: dict = dict(
    # n_estimators: The number of gradient boosted trees. 400 provides a good
    # balance between training speed and the ability to capture complex patterns.
    n_estimators=400,
    
    # learning_rate (shrinkage): Step size shrinkage used in update to prevent overfitting.
    # A smaller learning rate (0.05) requires more trees but makes the model more robust.
    learning_rate=0.05,
    
    # max_depth: Maximum decision depth of a tree. Depth 5 allows the model to
    # model interactions between up to 5 variables without over-learning noise.
    max_depth=5,
    
    # subsample: Fraction of training instances to randomly sample prior to growing trees.
    # 0.8 introduces stochastic gradient boosting, which helps reduce overfitting.
    subsample=0.8,
    
    # colsample_bytree: Fraction of features (columns) to randomly sample per tree.
    # 0.8 helps decorrelate the trees, making the ensemble more robust.
    colsample_bytree=0.8,
    
    # reg_alpha: L1 regularization term on weights (Lasso). Encourages sparsity.
    reg_alpha=0.1,
    
    # reg_lambda: L2 regularization term on weights (Ridge). Prevents extreme weights.
    reg_lambda=1.0,
    
    # random_state: Set seed for reproducible results across runs.
    random_state=42,
    
    # n_jobs: Number of parallel threads used to run XGBoost (-1 uses all cores).
    n_jobs=-1,
)


def train(
    X_hist: pd.DataFrame,
    y_hist: pd.Series,
    params: dict | None = None,
) -> xgb.XGBRegressor:
    """Train an XGBoostRegressor on historical data.

    XGBoost handles NaN values natively — it automatically learns the best
    default direction for missing values during node splits, meaning no manual
    imputation is required.

    Parameters
    ----------
    X_hist : pd.DataFrame
        Engineered feature matrix for the historical period.
    y_hist : pd.Series
        Target variable values for the historical period.
    params : dict | None
        Override any default hyperparameters (e.g., from cross-validation).

    Returns
    -------
    xgb.XGBRegressor — fitted model ready for inference.
    """
    # Merge user-supplied overrides with the default parameter dictionary
    hp = {**DEFAULT_PARAMS, **(params or {})}
    
    # Initialize the Scikit-learn wrapper for XGBoost regression
    model = xgb.XGBRegressor(**hp)
    
    # Fit the model to the historical features and target labels
    model.fit(X_hist, y_hist, verbose=False)
    return model


def predict(
    model: xgb.XGBRegressor,
    X_scenario: pd.DataFrame,
) -> np.ndarray:
    """Run inference on the scenario feature matrix.

    Parameters
    ----------
    model : xgb.XGBRegressor
        The trained model.
    X_scenario : pd.DataFrame
        The scenario feature matrix aligned to the training columns.

    Returns
    -------
    np.ndarray
        A 1-D array of predictions aligned to X_scenario's Datetime index.
    """
    return model.predict(X_scenario)
