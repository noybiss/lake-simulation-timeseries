"""
feature_engineering.py — Cyclical time features and rolling lag features.
Applied consistently to both historical and scenario DataFrames.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def engineer_features(
    df: pd.DataFrame,
    target_col: str | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Add cyclical time features and rolling lag features.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with a DatetimeIndex. All numeric columns are treated as
        feature candidates unless they match target_col.
    target_col : str | None
        Name of the target column. If provided it is excluded from lag/rolling
        feature generation but preserved untouched in the returned DataFrame.

    Returns
    -------
    (X, y_or_none)
        X : DataFrame of engineered features (target column excluded).
        y : Series of the target column values (or None if target_col is None).
    """
    df = df.copy()

    # ------------------------------------------------------------------ #
    # 1. Cyclical time features from DatetimeIndex (for Seasons)
    # ------------------------------------------------------------------ #
    idx = df.index
    month = idx.month.astype(float)
    hour = idx.hour.astype(float)

    df["month_sin"] = np.sin(2 * np.pi * month / 12)
    df["month_cos"] = np.cos(2 * np.pi * month / 12)
    df["hour_sin"] = np.sin(2 * np.pi * hour / 24)
    df["hour_cos"] = np.cos(2 * np.pi * hour / 24)

    # Also add day-of-year cyclical for added seasonality capture
    doy = idx.dayofyear.astype(float)
    df["doy_sin"] = np.sin(2 * np.pi * doy / 365)
    df["doy_cos"] = np.cos(2 * np.pi * doy / 365)

    # ------------------------------------------------------------------ #
    # 1b. Long-term trend features from DatetimeIndex (for Years)
    # ------------------------------------------------------------------ #
    # The actual year (e.g., 2015, 2016, 2017)
    df["year"] = idx.year.astype(float)
    
    # A cumulative time index (days since the very first record)
    # This helps XGBoost understand that time is continuously moving forward
    # which is crucial for capturing 10-year linear trends (like climate change).
    time_deltas = idx - idx.min()
    df["time_idx_days"] = time_deltas.days.astype(float)

    # ------------------------------------------------------------------ #
    # 2. Rolling / lag features for all numeric feature columns
    # ------------------------------------------------------------------ #
    feature_candidates = [
        c for c in df.columns
        if c != target_col
        and pd.api.types.is_numeric_dtype(df[c])
        and not c.endswith(("_rolling_3", "_rolling_7", "_sin", "_cos"))
    ]

    new_cols: dict[str, pd.Series] = {}
    for col in feature_candidates:
        new_cols[f"{col}_rolling_3"] = (
            df[col].rolling(3, min_periods=1).mean()
        )
        new_cols[f"{col}_rolling_7"] = (
            df[col].rolling(7, min_periods=1).mean()
        )

    df = pd.concat([df, pd.DataFrame(new_cols, index=df.index)], axis=1)

    # ------------------------------------------------------------------ #
    # 3. Fill any remaining NaNs from rolling windows — ffill then bfill
    # ------------------------------------------------------------------ #
    df = df.ffill().bfill()

    # ------------------------------------------------------------------ #
    # 4. Split into X and y
    # ------------------------------------------------------------------ #
    if target_col is not None and target_col in df.columns:
        y = df[target_col]
        X = df.drop(columns=[target_col])
        return X, y
    else:
        return df, None
