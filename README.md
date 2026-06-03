# Lake Simulation TimeSeries v.2 (OmniSim AI)

**Made and Designed by OA.**

OmniSim AI is an Environmental Simulation System built with Python, Streamlit, and XGBoost. It provides a universal time-series simulation engine specifically engineered for environmental scientists and researchers requiring high-density, precise information.

## Key Features

- **Automated ML Pipeline**: Upload an Excel file with historical data and scenario definitions. The engine automatically identifies targets, aligns time-series data, and engineers features.
- **Robust Data Cleaning**: Intelligently detects and offers cleaning options for missing placeholders (like -9999), statistical outliers, and extreme value ranges.
- **High-Performance Modeling**: Powered by XGBoost, ensuring rapid convergence and highly accurate predictions for complex environmental data.
- **SHAP Explainability**: Demystifies AI decisions by providing detailed SHAP value breakdowns, showing exactly which historical factors drove the predictions.
- **Scientific Dark Mode**: A custom, high-contrast "Dark Mode" UI designed with Inter and Space Grotesk typography to reduce eye strain during prolonged analysis.
- **Detailed Logging**: Automatically saves simulation metrics (R², RMSE), configurations, and SHAP insights to structured JSON log files for future AI analysis.

## Project Structure

- `app.py`: The main Streamlit application and UI layer.
- `modules/`: Core backend logic.
  - `data_loader.py`: Excel parsing, time index normalization, and rigorous data quality checking.
  - `feature_engineering.py`: Automated generation of lag and rolling window features.
  - `model.py`: XGBoost training and prediction wrapper.
  - `explainer.py`: SHAP value computation.
  - `visualizer.py`: Custom, dark-themed Plotly chart generation.
  - `logger.py`: JSON-based simulation result logging.

## Installation and Usage

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the Streamlit application:
   ```bash
   streamlit run app.py
   ```
   *(Alternatively, you can run the included `run.command` script on macOS/Linux).*

3. **Data Format**: 
   Upload a standard `.xls` or `.xlsx` file:
   - **Sheet 1 (Historical)**: Must contain your historical training data with a time-based index.
   - **Sheet 2+ (Scenarios)**: Must contain scenario projections. Exactly **one** column should be left empty; the AI will automatically target and predict this column.
