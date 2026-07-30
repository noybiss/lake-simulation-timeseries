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
    seasonal: bool = True,
    rolling_windows: tuple[int, ...] = (3, 7),
    time_origin: pd.Timestamp | None = None,
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
    seasonal : bool
        When True (default), generate cyclical calendar features — month,
        hour, and day-of-year projected onto sine/cosine pairs — so seasonal
        effects (cold winters, warm summers) are captured with correct
        wrap-around continuity. When False, these cyclical features are skipped
        (useful for non-seasonal data). Long-term trend (`year`, `time_idx_days`)
        and rolling lag features are always generated, since they capture trend
        and smoothing rather than seasonality.
    rolling_windows : tuple[int, ...]
        Observation windows used for rolling predictor means. Larger windows
        provide slower context; smaller windows preserve short-term movement.
    time_origin : pd.Timestamp | None
        Shared origin for the continuous time index. Pass the historical start
        date when engineering scenario features so future dates continue the
        same trend scale instead of resetting to zero.

    Returns
    -------
    (X, y_or_none)
        X : DataFrame of engineered features (target column excluded).
        y : Series of the target column values (or None if target_col is None).
    """
    df = df.copy()

    # ------------------------------------------------------------------ #
    # 1. Cyclical time features from DatetimeIndex (for Seasons/Time-of-day)
    # ------------------------------------------------------------------ #
    # Simple integer representations of time (e.g. Month 12 and Month 1)
    # appear far apart to machine learning models. By projecting them onto a
    # unit circle using sine and cosine, we maintain the correct cyclical proximity:
    # December (12) and January (1) become close numerical neighbors.
    idx = df.index

    if seasonal:
        month = idx.month.astype(float)
        hour = idx.hour.astype(float)

        # Month cycles (12-month period)
        df["month_sin"] = np.sin(2 * np.pi * month / 12)
        df["month_cos"] = np.cos(2 * np.pi * month / 12)

        # Hour cycles (24-hour daily period)
        df["hour_sin"] = np.sin(2 * np.pi * hour / 24)
        df["hour_cos"] = np.cos(2 * np.pi * hour / 24)

        # Day-of-year cycle (365-day seasonal period)
        # Essential for high-resolution seasonal effects like water temperature changes
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
    origin = pd.Timestamp(time_origin) if time_origin is not None else idx.min()
    time_deltas = idx - origin
    df["time_idx_days"] = time_deltas.total_seconds().astype(float) / 86_400.0

    # ------------------------------------------------------------------ #
    # 2. Rolling / lag features for all numeric feature columns
    # ------------------------------------------------------------------ #
    # Rolling averages provide the model with historical context and smooth
    # out short-term fluctuations.
    windows = tuple(sorted({int(window) for window in rolling_windows if int(window) > 1}))
    feature_candidates = [
        c for c in df.columns
        if c != target_col
        and pd.api.types.is_numeric_dtype(df[c])
        and "_rolling_" not in c
        and not c.endswith(("_sin", "_cos"))
    ]

    new_cols: dict[str, pd.Series] = {}
    for col in feature_candidates:
        # min_periods=1 ensures we get values even at the beginning of the series
        for window in windows:
            new_cols[f"{col}_rolling_{window}"] = (
                df[col].rolling(window, min_periods=1).mean()
            )

    # Combine newly engineered rolling features with the original DataFrame
    df = pd.concat([df, pd.DataFrame(new_cols, index=df.index)], axis=1)

    # ------------------------------------------------------------------ #
    # 3. Fill any remaining NaNs from rolling windows — ffill then bfill
    # ------------------------------------------------------------------ #
    # forward-fill then backward-fill handles boundary values where rolling
    # windows might generate NaNs.
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
