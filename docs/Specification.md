# App Specification: OmniSim AI (Universal Time-Series Scenario Engine)

## Project Overview

Build a web-based "What-If" simulation application for any multivariate time-series data. The user will upload historical tabular data (e.g., environmental, financial, or industrial) and a "Scenario" dataset. The goal is counterfactual simulation: the user will change specific controllable variables in the scenario file while leaving uncontrollable variables unchanged, to predict the exact impact on a missing target variable.

## Target Tech Stack

- **Language:** Python
- **Framework:** Streamlit
- **Data Processing:** Pandas, NumPy
- **Machine Learning:** XGBoost (`xgboost`)
- **Model Explainability:** SHAP (`shap`)
- **Visualization:** Plotly (`plotly.express` and `plotly.graph_objects`)

## Core Features & Logic Requirements

### 1. Data Ingestion & Multi-Sheet Handling

- **File Upload:** Create a Streamlit file uploader accepting `.xlsx` files.
- **Sheet Parsing:** \* Read all sheets in the uploaded Excel file.
  - **Index 0 (First Sheet):** Always treat this as the "Historical Data".
  - **Index 1+ (Subsequent Sheets):** Treat these as "Scenarios".
- **Scenario UI Selector:** If there are multiple scenario sheets, render a Streamlit selectbox or tab system so the user can select which scenario to analyze. Name them dynamically: "Scenario: [Sheet Name]".
- **Orientation Check:** Check if the data is transposed (e.g., Time is row 0 instead of column 0). Transpose to a standard column-based dataframe if necessary.
- **Time Column Handling (CRITICAL):**
  - Dynamically locate the column representing time (look for common names like "Time", "Date", "Datetime", or the first column if it contains datetime objects).
  - Force-parse this column into standard datetime format (`YYYY-MM-DD HH:MM:SS`) using `pandas.to_datetime`.
  - Set this datetime column as the DataFrame index and sort chronologically.

### 2. Dynamic Target Detection

- Scan the currently selected "Scenario" sheet.
- Find the single variable (column) that is completely empty (contains only NaNs or Nulls).
- Set this empty column as the **Target Variable (y)**.
- Set all other present columns as the **Feature Variables (X)**. The program must not assume any specific domain or variable names; it relies entirely on the dynamic column headers.

### 3. Advanced Feature Engineering

- Apply the following transformations to the X variables for _both_ the Historical dataframe and the selected Scenario dataframe:
  - **Cyclical Time Features:** Extract "Month" and "Hour" from the Datetime index. Apply Sine and Cosine transformations to these values to capture cyclical seasonality (e.g., `sin(2 * pi * month / 12)`) and append them as new columns.
  - **Lag & Rolling Features:** For all continuous numeric feature columns, automatically generate short-term rolling averages (e.g., 3-period and 7-period rolling means) to capture the system's delayed reactions.

### 4. Model Training & Scenario Prediction

- **Training:** Isolate the historical X (with engineered features) and historical y. Train an `XGBoostRegressor` model on this data.
- **Prediction:** Pass the active Scenario's X variables (which contain the user's manual "what-if" adjustments) through the trained XGBoost model to predict the missing Target Variable.
- Fill the empty column in the Scenario dataframe with these predictions.

### 5. Visualization & UI

- **Main Graph (Time-Series Comparison):** Render an interactive Plotly line chart.
  - Plot 1 (Solid Line): Historical actual data for the Target Variable.
  - Plot 2 (Dashed Line, contrasting color): Predicted scenario data for the Target Variable.
  - X-axis = Datetime index, Y-axis = Target Variable Value. Enable the native Plotly toolbar.
- **Secondary Graph (SHAP Feature Impact):** \* Calculate SHAP values for the trained XGBoost model using the scenario data.
  - Render a Plotly horizontal bar chart or SHAP summary plot below the main graph. This must show the user which variables had the greatest positive or negative impact on the scenario's predictions.

### 6. Data Export

- Provide a Streamlit download button (`st.download_button`) labeled "Download Current Scenario" to let the user download the active Scenario Dataset (with the newly predicted column filled in) as a `.csv` file.

## Error Handling

- `st.error` if the column names in a Scenario sheet don't perfectly match the Historical sheet.
- `st.error` if zero or more than one column is completely empty in a scenario sheet (the MVP must predict exactly one target).
- Handle missing data (NaNs) in the historical feature variables by utilizing XGBoost's native handling for missing values, or apply a forward-fill (`ffill`) interpolation before training.
