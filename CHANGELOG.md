# Changelog

All notable changes to Lake Time-Series Forecasting are documented here.

## [2.0.0] — 2026-08-01

Version 2.0.0 is a major product release that introduces a complete visual
redesign, a clearer forecasting workflow, expanded model controls, and a
verified Docker deployment path.

### Complete interface redesign

- Rebuilt the application around a professional Roland Digital-inspired visual
  system with warm neutral surfaces, electric-blue accents, and consistent
  scientific typography.
- Improved contrast and readability across metrics, target labels, status
  badges, outlier values, expanders, charts, upload controls, and messages.
- Restored reliable sidebar collapse and reopen controls.
- Removed non-functional heading link icons and legacy dark-theme styling.
- Added responsive layouts for smaller screens and clearer empty, loading,
  validation, training, success, and error states.

### Better training experience

- Added an animated live-training console so users can see candidate models,
  forward-only validation progress, and the best score while optimization runs.
- Replaced generic progress feedback with scenario-specific model status and
  clearer explanations of each stage.
- Improved result cards, scorecards, feature labels, and SHAP visualizations.

### Forecasting and model-control improvements

- Added explained Advanced-mode controls for search effort, validation folds,
  model complexity, and rolling context windows.
- Preserved a continuous historical time origin when generating future scenario
  features, preventing the future trend index from restarting at zero.
- Added configurable seasonal feature engineering and extended rolling windows.
- Added focused regression tests for continuous time and rolling-window logic.

### Reliability fixes

- Corrected Streamlit uploader styling selectors and sidebar behavior.
- Fixed low-contrast text on dark badges and inline outlier values.
- Improved long target-variable and scientific feature-name presentation.
- Updated documentation and labels to match actual application behavior.
- Standardized the product name as **Lake Time-Series Forecasting** throughout
  the application and documentation.

### Demo and deployment

- Added a ready-to-run workbook with 2,000 historical rows and a future warming
  scenario for immediate evaluation.
- Added Docker Compose deployment with persistent logs and automatic restart.
- Included the production Streamlit theme inside the Docker image.
- Added a built-in container health check using Streamlit's health endpoint.
- Verified the v2.0.0 image by building it locally, starting the application,
  and confirming a healthy container state.

[2.0.0]: https://github.com/omidabduli/lake-simulation-timeseries/releases/tag/v2.0.0
