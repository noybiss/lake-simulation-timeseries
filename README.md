# Lake Time-Series Forecasting

[![Python Version](https://img.shields.io/badge/Python-3.9+-blue.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit App](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B.svg?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![XGBoost Regressor](https://img.shields.io/badge/XGBoost-2.0+-green.svg?style=flat&logo=xgboost)](https://xgboost.readthedocs.io/)
[![SHAP Explainability](https://img.shields.io/badge/SHAP-Explainable_AI-orange.svg?style=flat)](https://shap.readthedocs.io/)
[![Developer](https://img.shields.io/badge/Developed%20by-Omid%20Abduli-1648D8.svg?style=flat)](https://github.com/omidabduli)

> **Lake Time-Series Forecasting** is an explainable environmental forecasting and scenario-analysis application for scientists, limnologists, analysts, and researchers. It combines structured Excel workflows, forward-only model validation, XGBoost forecasting, and SHAP explanations in a clear, reproducible interface.

---

## 🚀 Key Features

*   **⚡ Automated Machine Learning Pipeline**: Just upload your raw Excel file! The engine automatically parses historical records, aligns indices, runs target detection, and constructs features.
*   **🔍 Advanced Data Quality Auditing**: Scans data on-the-fly to discover missing placeholder values (e.g., `-999`, `-9999`) and statistical outliers using robust **Interquartile Range (IQR)** filtering.
*   **🧠 High-Performance Modeling**: Powered by **XGBoost** with automated **Time-Series Cross-Validation (TimeSeriesSplit)** hyperparameter optimization to prevent training leakages.
*   **🔮 SHAP Explainability (XAI)**: Demystifies the machine learning "black box" by calculating exact game-theory-based SHAP values, identifying which parameters drove the simulation outcomes.
*   **🎨 Professional Scientific Interface**: A responsive, high-contrast workspace inspired by the Roland Digital visual system, with accessible labels and clear training feedback.
*   **📁 Structured Run Logging**: Automatically serializes accuracy metrics ($R^2$, RMSE), model parameters, and top SHAP drivers into JSON files for future AI analysis.

---

## 🛠️ How It Works (Step-by-Step Workflow)

```mermaid
graph TD
    A[📂 Upload Excel File] --> B[🔍 Data Quality Check]
    B --> C{🛠️ Clean Data?}
    C -- Yes --> D[🧹 Mask Placeholders & Outliers]
    C -- No --> E[🧬 Raw Feature Engineering]
    D --> E
    E --> F[⏱️ Cyclical & Rolling Lag generation]
    F --> G[🚀 CV Hyperparameter Search]
    G --> H[🏆 Final Model Training]
    H --> I[🔮 Scenario Predictions & SHAP Analysis]
    I --> J[💾 JSON Logging & CSV Download]
```

1.  **Upload File 📂**: Drop your `.xls` or `.xlsx` workbook. The system reads **Sheet 1** as history and **Sheets 2+** as scenario conditions.
2.  **Audit Data 🔍**: Review detected missing placeholders and outliers. Choose to clean specific columns or proceed with raw values.
3.  **Optimize 🚀**: Watch the live model console evaluate candidate configurations with forward-only validation. Advanced mode can adjust search effort, validation rigor, tree complexity, and rolling context windows.
4.  **Analyze 📊**: Explore interactive Plotly projections comparing history with predictions, backed by horizontal SHAP feature impact rankings.
5.  **Export ⬇️**: Download prediction outcomes formatted as standardized CSVs for German locales (`;` delimiter, `,` decimals).

---

## ⚙️ Under The Hood (ML Pipeline Details)

### 1. Cyclical Time Representations ⏰
Standard integers represent months (1–12) or hours (0–23) poorly, making December (12) and January (1) seem far apart. Lake Time-Series Forecasting projects dates onto a unit circle:
$$\text{month\_sin} = \sin\left(\frac{2\pi \cdot \text{month}}{12}\right), \quad \text{month\_cos} = \cos\left(\frac{2\pi \cdot \text{month}}{12}\right)$$

### 2. Temporal Smoothing & Continuous Time 📉
The default model calculates 3-observation and 7-observation rolling statistics
for every predictor. Advanced mode can add 14- or 30-observation context when
the measured system responds more slowly. Scenario dates share the historical
time origin, so the long-term trend continues into the future instead of
resetting when a scenario begins.

### 3. Hyperparameter Tuning 🎛️
During training, a Time-Series Split cross-validation optimizes the learning rate, maximum tree depth, and estimator size to ensure high generalization scores.

Advanced mode includes an explained **Expert model tuning** panel:

- **Search effort** controls how many candidate models are evaluated.
- **Time-series validation** controls the number of forward-only historical splits.
- **Model complexity** controls the tree-depth search range.
- **Rolling context windows** control how much short- and long-term predictor history is represented.

Start with the recommended Balanced profile and change one setting at a time.
Compare validation R² and RMSE rather than judging a model by training fit alone.

---

## 📂 Project Directory Structure

```text
├── app.py                     # 🌐 Main Streamlit Application & UI Layer
├── run.command                # ⚡ One-click macOS/Linux Shell Launcher
├── requirements.txt           # 📦 Python Package Dependencies
├── .gitignore                 # 🚫 Git Exclude Patterns (filters large sheets)
├── modules/                   # 🧠 Core Backend Architecture
│   ├── __init__.py            # 📦 Module Package Setup
│   ├── data_loader.py         # 🗄️ Excel Ingestion & IQR Outlier Checks
│   ├── feature_engineering.py  # 🧬 Sine/Cosine Cyclicals & Rolling Lags
│   ├── model.py               # 🌲 XGBoost Trainer Wrapper
│   ├── explainer.py           # 🔮 SHAP TreeExplainer Logic
│   ├── visualizer.py          # 🎨 Plotly Scientific Visualization Templates
│   └── logger.py              # 📝 Serialized JSON Run Logging
└── docs/                      # 📖 Deep Academic Documentation
    ├── Design.md              # 📐 UI/UX Design System Layout
    ├── Specification.md       # 📋 Detailed Project Specifications
    ├── documentation_de.md    # 🇩🇪 Comprehensive German Academic Docs
    ├── explanation_de.md      # 🇩🇪 Quick German User Explanation
    └── explanation_fa.md      # 🇮🇷 Quick Persian User Explanation
```

---

## 💻 Installation & Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/omidabduli/lake-simulation-timeseries.git
cd lake-simulation-timeseries
```

### 🐳 Option A: Run with Docker (Recommended & Easiest)
You can run Lake Time-Series Forecasting in a container without installing Python, compilers, or packages locally.

#### Using Docker Compose
1. **Build and launch the container**:
   ```bash
   docker compose up --build
   ```
2. **Access the application**:
   Open your browser at [http://localhost:8501](http://localhost:8501) ⚡
   *(Any logs created during runs will automatically sync to your local `./logs/` directory)*

#### Using Standard Docker Commands
1. **Build the image**:
   ```bash
   docker build -t lake-time-series-forecasting .
   ```
2. **Run the container**:
   ```bash
   docker run -d -p 8501:8501 -v "$(pwd)/logs:/app/logs" --name lake-forecasting lake-time-series-forecasting
   ```
3. **Access the application**:
   Open your browser at [http://localhost:8501](http://localhost:8501) ⚡

---

### 🐍 Option B: Local Development Setup

#### Prerequisites
Make sure you have **Python 3.9+** installed. If you are using macOS, it is recommended to install `libomp` (required by XGBoost for multi-threading):
```bash
brew install libomp
```

#### Setup Steps
1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Streamlit Dashboard**:
   ```bash
   streamlit run app.py --server.port 8502
   ```
   *On macOS, you can also double-click `run.command` directly from the Finder to launch.*

---

## 📊 File Formatting Guidelines

### Try the bundled demo

To test the complete workflow immediately, upload
`Example/Lake_Time_Series_Forecasting_Demo_2000_Rows.xlsx` in the app. It contains:

- **Historical** — 2,000 daily lake observations across 10 variables.
- **Scenario_Warming** — a 365-day future scenario with
  `Dissolved_Oxygen_mg_L` intentionally blank for the application to predict.

No editing is required; select the file and the simulation starts automatically.

---

To get accurate simulations, structure your Excel workbook as follows:

*   **Sheet 1 (Historical data)**:
    *   Must contain a chronological index column named `Time`, `Date`, `Datetime`, `Timestamp`, `Datum`, or `Zeit`.
    *   All other columns must contain numeric values (e.g., `temperature`, `oxygen`, `ph`, `precipitation`).
*   **Sheets 2+ (Scenarios)**:
    *   Must have the **exact same columns** as Sheet 1.
    *   Exactly **one** column must be left **entirely empty (NaN)**. This is the variable the AI will automatically identify as the target and predict for you.

---

## Author

**Developed and maintained by [Omid Abduli](https://github.com/omidabduli)**

[Roland Digital](https://roland-digital.de/) · Germany

*Explainable environmental time-series simulation for research and scenario analysis.*
