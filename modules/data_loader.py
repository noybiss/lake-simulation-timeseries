"""
data_loader.py — Excel ingestion, sheet separation, time-index normalization,
target detection, column validation, and data quality checks.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def detect_data_issues(
    sheets: dict[str, pd.DataFrame],
    missing_placeholders: list[float] | None = None,
    iqr_threshold: float = 3.0,
) -> dict[str, dict]:
    """Detect data quality issues in uploaded Excel sheets.

    Identifies:
    - Common missing data placeholders (e.g., -999, -9999, 999)
    - Statistical outliers using IQR method
    - Extreme values that may indicate data entry errors

    Parameters
    ----------
    sheets : dict[str, pd.DataFrame]
        Dictionary of sheet names to DataFrames.
    missing_placeholders : list[float] | None
        Values that represent missing data. Default: [-999.0, -9999.0, 999.0, 9999.0]
        Note: -1.0 is NOT included as it can be a valid value (e.g., temperature)
    iqr_threshold : float
        Number of IQRs from Q1/Q3 to consider as outlier. Default: 3.0.

    Returns
    -------
    dict[str, dict]
        Nested dictionary with sheet names as keys, each containing:
        - 'missing_placeholders': dict of {column: count} for placeholder values
        - 'outliers': dict of {column: count} for statistical outliers
        - 'extreme_values': dict of {column: (min, max)} for extreme ranges
        - 'total_issues': total number of problematic cells found
        - 'recommendations': list of suggested actions
    """
    if missing_placeholders is None:
        # Removed -1.0 as it can be a valid value (e.g., -1°C temperature)
        missing_placeholders = [-999.0, -9999.0, 999.0, 9999.0]

    issues_report = {}

    for sheet_name, df in sheets.items():
        sheet_issues = {
            'missing_placeholders': {},
            'outliers': {},
            'extreme_values': {},
            'total_issues': 0,
            'recommendations': []
        }

        # Get numeric columns only
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            col_data = df[col].dropna()

            if len(col_data) == 0:
                continue

            # 1. Check for missing data placeholders
            for placeholder in missing_placeholders:
                placeholder_count = (col_data == placeholder).sum()
                if placeholder_count > 0:
                    if col not in sheet_issues['missing_placeholders']:
                        sheet_issues['missing_placeholders'][col] = []
                    sheet_issues['missing_placeholders'][col].append({
                        'value': placeholder,
                        'count': int(placeholder_count),
                        'percentage': float(placeholder_count / len(col_data) * 100)
                    })

            # 2. Check for statistical outliers using IQR method
            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1

            if IQR > 0:  # Avoid division by zero
                lower_bound = Q1 - (iqr_threshold * IQR)
                upper_bound = Q3 + (iqr_threshold * IQR)

                outliers = col_data[(col_data < lower_bound) | (col_data > upper_bound)]
                if len(outliers) > 0:
                    sheet_issues['outliers'][col] = {
                        'count': len(outliers),
                        'percentage': float(len(outliers) / len(col_data) * 100),
                        'lower_bound': float(lower_bound),
                        'upper_bound': float(upper_bound),
                        'outlier_values': outliers.tolist()[:10]  # Show first 10
                    }

            # 3. Check for extreme values (very large or very small)
            col_min = float(col_data.min())
            col_max = float(col_data.max())
            col_range = col_max - col_min

            # Flag if range is extremely large or values are suspicious
            if abs(col_min) > 1e6 or abs(col_max) > 1e6 or col_range > 1e8:
                sheet_issues['extreme_values'][col] = {
                    'min': col_min,
                    'max': col_max,
                    'range': col_range,
                    'mean': float(col_data.mean()),
                    'std': float(col_data.std())
                }

        # Calculate total issues
        for col, placeholders in sheet_issues['missing_placeholders'].items():
            sheet_issues['total_issues'] += sum(p['count'] for p in placeholders)
        for col, outlier_info in sheet_issues['outliers'].items():
            sheet_issues['total_issues'] += outlier_info['count']

        # Generate recommendations
        if sheet_issues['missing_placeholders']:
            sheet_issues['recommendations'].append(
                f"Found {len(sheet_issues['missing_placeholders'])} column(s) with missing data placeholders. "
                "Consider replacing these with NaN values."
            )

        if sheet_issues['outliers']:
            sheet_issues['recommendations'].append(
                f"Found {len(sheet_issues['outliers'])} column(s) with statistical outliers. "
                "Review these values for data entry errors."
            )

        if sheet_issues['extreme_values']:
            sheet_issues['recommendations'].append(
                f"Found {len(sheet_issues['extreme_values'])} column(s) with extreme value ranges. "
                "Verify these are correct measurements."
            )

        issues_report[sheet_name] = sheet_issues

    return issues_report


def clean_data_issues(
    df: pd.DataFrame,
    issues: dict,
    replace_with_nan: list[float] | None = None,
    clean_outliers: bool = False,
) -> pd.DataFrame:
    """Clean detected data issues by replacing problematic values with NaN.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to clean.
    issues : dict
        Issues report from detect_data_issues().
    replace_with_nan : list[float] | None
        Values to replace with NaN. If None, uses all detected placeholders.
    clean_outliers : bool
        If True, also replaces statistical outliers with NaN.

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame with problematic values replaced by NaN.
    """
    df_clean = df.copy()

    if replace_with_nan is None and 'missing_placeholders' in issues:
        # Extract all placeholder values from the issues
        replace_with_nan = []
        for col, placeholders in issues['missing_placeholders'].items():
            for p in placeholders:
                replace_with_nan.append(p['value'])

    # Replace placeholders with NaN
    for placeholder in replace_with_nan:
        df_clean = df_clean.replace(placeholder, np.nan)

    # Replace outliers with NaN if requested
    if clean_outliers and 'outliers' in issues:
        for col, outlier_info in issues['outliers'].items():
            lower_bound = outlier_info['lower_bound']
            upper_bound = outlier_info['upper_bound']
            # Replace values outside the normal range with NaN
            df_clean.loc[df_clean[col] < lower_bound, col] = np.nan
            df_clean.loc[df_clean[col] > upper_bound, col] = np.nan

    return df_clean


def clean_specific_columns(
    sheets: dict[str, pd.DataFrame],
    issues_report: dict[str, dict],
    columns_to_clean: dict[str, list[tuple[str, str]]],
    missing_placeholders: list[float] | None = None,
) -> dict[str, pd.DataFrame]:
    """Clean specific columns in specific sheets based on user selection.

    Parameters
    ----------
    sheets : dict[str, pd.DataFrame]
        Dictionary of sheet names to DataFrames.
    issues_report : dict[str, dict]
        Issues report from detect_data_issues().
    columns_to_clean : dict[str, list[tuple[str, str]]]
        Dictionary with keys 'missing_placeholders' and 'outliers'.
        Each value is a list of (sheet_name, column_name) tuples.
    missing_placeholders : list[float] | None
        Values to replace with NaN for missing placeholders.

    Returns
    -------
    dict[str, pd.DataFrame]
        Dictionary of cleaned DataFrames.
    """
    cleaned_sheets = {}

    for sheet_name, df in sheets.items():
        df_clean = df.copy()
        sheet_issues = issues_report.get(sheet_name, {})

        # Clean missing placeholders for selected columns
        for clean_sheet_name, col_name in columns_to_clean['missing_placeholders']:
            if clean_sheet_name == sheet_name and col_name in sheet_issues.get('missing_placeholders', {}):
                placeholders = [p['value'] for p in sheet_issues['missing_placeholders'][col_name]]
                for placeholder in placeholders:
                    df_clean[col_name] = df_clean[col_name].replace(placeholder, np.nan)

        # Clean outliers for selected columns
        for clean_sheet_name, col_name in columns_to_clean['outliers']:
            if clean_sheet_name == sheet_name and col_name in sheet_issues.get('outliers', {}):
                outlier_info = sheet_issues['outliers'][col_name]
                lower_bound = outlier_info['lower_bound']
                upper_bound = outlier_info['upper_bound']
                df_clean.loc[df_clean[col_name] < lower_bound, col_name] = np.nan
                df_clean.loc[df_clean[col_name] > upper_bound, col_name] = np.nan

        cleaned_sheets[sheet_name] = df_clean

    return cleaned_sheets


def load_excel(file) -> dict[str, pd.DataFrame]:
    """Read all sheets from an uploaded Excel file.

    Supports both .xls (xlrd engine) and .xlsx (openpyxl engine).
    Returns a dict of {sheet_name: DataFrame}.
    """
    try:
        sheets = pd.read_excel(file, sheet_name=None, engine=_detect_engine(file))
    except Exception:
        # Fallback: try the other engine
        try:
            sheets = pd.read_excel(file, sheet_name=None, engine="xlrd")
        except Exception:
            sheets = pd.read_excel(file, sheet_name=None, engine="openpyxl")
    return sheets


def separate_sheets(
    sheets: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    """Split sheet dict into (historical_df, scenarios_dict).

    The first sheet is always historical; all subsequent sheets are scenarios.
    Raises ValueError if there are fewer than 2 sheets.
    """
    names = list(sheets.keys())
    if len(names) < 2:
        raise ValueError(
            f"The uploaded file must have at least 2 sheets (Historical + at least 1 Scenario). "
            f"Found {len(names)} sheet(s): {', '.join(names) if names else 'none'}."
        )
    historical = sheets[names[0]].copy()
    scenarios = {f"Scenario: {n}": sheets[n].copy() for n in names[1:]}
    return historical, scenarios


def normalize_time_index(df: pd.DataFrame) -> pd.DataFrame:
    """Detect the time column, parse it as datetime, set as index, sort."""
    df = df.copy()

    time_col = _find_time_column(df)
    if time_col is None:
        raise ValueError(
            "Cannot detect a time/date column. "
            "Rename it to 'Time', 'Date', or 'Datetime'."
        )

    df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
    df = df.set_index(time_col)
    df.index.name = "Time"
    df = df.sort_index()
    return df


def detect_target_column(scenario_df: pd.DataFrame) -> str:
    """Find the single column that is entirely NaN in a scenario sheet.

    Raises ValueError if 0 or more than 1 such column exists.
    """
    fully_nan = [col for col in scenario_df.columns if scenario_df[col].isna().all()]

    if len(fully_nan) == 0:
        raise ValueError(
            "No empty column found in this scenario. "
            "Exactly one column must be entirely NaN (the prediction target)."
        )
    if len(fully_nan) > 1:
        raise ValueError(
            f"Found {len(fully_nan)} empty columns ({', '.join(fully_nan)}). "
            "Exactly one column must be entirely NaN."
        )
    return fully_nan[0]


def validate_column_match(historical_df: pd.DataFrame, scenario_df: pd.DataFrame) -> None:
    """Raise ValueError if the column sets of historical and scenario don't match."""
    hist_cols = set(historical_df.columns)
    scen_cols = set(scenario_df.columns)
    if hist_cols != scen_cols:
        extra = scen_cols - hist_cols
        missing = hist_cols - scen_cols
        msg_parts = []
        if extra:
            msg_parts.append(f"extra in scenario: {sorted(extra)}")
        if missing:
            msg_parts.append(f"missing in scenario: {sorted(missing)}")
        raise ValueError(
            "Scenario columns don't match Historical. " + "; ".join(msg_parts) + "."
        )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

_TIME_KEYWORDS = {"time", "date", "datetime", "timestamp", "datum", "zeit"}


def _find_time_column(df: pd.DataFrame) -> str | None:
    """Return the name of the time column, or None if not found."""
    # 1. Check by known keyword names (case-insensitive)
    for col in df.columns:
        if str(col).strip().lower() in _TIME_KEYWORDS:
            return col

    # 2. Check if the first column contains datetime-like values
    first_col = df.columns[0]
    sample = df[first_col].dropna().head(5)
    try:
        pd.to_datetime(sample)
        return first_col
    except Exception:
        pass

    # 3. Scan all columns for datetime dtype
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return col

    return None


def _detect_engine(file) -> str:
    """Pick the correct Excel reading engine based on file extension."""
    name = getattr(file, "name", "")
    if isinstance(name, str) and name.lower().endswith(".xls"):
        return "xlrd"
    return "openpyxl"
