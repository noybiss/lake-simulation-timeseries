---
name: Environmental Simulation System
colors:
  surface: "#f7f9fb"
  surface-dim: "#d8dadc"
  surface-bright: "#f7f9fb"
  surface-container-lowest: "#ffffff"
  surface-container-low: "#f2f4f6"
  surface-container: "#eceef0"
  surface-container-high: "#e6e8ea"
  surface-container-highest: "#e0e3e5"
  on-surface: "#191c1e"
  on-surface-variant: "#41484d"
  inverse-surface: "#2d3133"
  inverse-on-surface: "#eff1f3"
  outline: "#71787d"
  outline-variant: "#c0c7cd"
  surface-tint: "#2c6480"
  primary: "#00354a"
  on-primary: "#ffffff"
  primary-container: "#0a4d68"
  on-primary-container: "#88bddc"
  inverse-primary: "#98cded"
  secondary: "#006877"
  on-secondary: "#ffffff"
  secondary-container: "#8debff"
  on-secondary-container: "#006b7a"
  tertiary: "#003740"
  on-tertiary: "#ffffff"
  tertiary-container: "#004f5c"
  on-tertiary-container: "#23c7e3"
  error: "#ba1a1a"
  on-error: "#ffffff"
  error-container: "#ffdad6"
  on-error-container: "#93000a"
  primary-fixed: "#c3e8ff"
  primary-fixed-dim: "#98cded"
  on-primary-fixed: "#001e2c"
  on-primary-fixed-variant: "#084c67"
  secondary-fixed: "#a3eeff"
  secondary-fixed-dim: "#76d4e7"
  on-secondary-fixed: "#001f25"
  on-secondary-fixed-variant: "#004e5a"
  tertiary-fixed: "#a7eeff"
  tertiary-fixed-dim: "#41d8f4"
  on-tertiary-fixed: "#001f25"
  on-tertiary-fixed-variant: "#004e5b"
  background: "#f7f9fb"
  on-background: "#191c1e"
  surface-variant: "#e0e3e5"
typography:
  h1:
    fontFamily: Inter
    fontSize: 30px
    fontWeight: "600"
    lineHeight: 38px
    letterSpacing: -0.02em
  h2:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: "600"
    lineHeight: 32px
    letterSpacing: -0.01em
  h3:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: "600"
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: "400"
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: "400"
    lineHeight: 20px
  label-caps:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: "700"
    lineHeight: 16px
    letterSpacing: 0.05em
  mono-data:
    fontFamily: Space Grotesk
    fontSize: 13px
    fontWeight: "400"
    lineHeight: 18px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 4px
  sidebar_width: 320px
  container_max_width: 1440px
  gutter: 24px
  card_padding: 20px
  stack_gap: 12px
---

## Brand & Style

This design system is engineered for precision, clarity, and authority. It targets environmental scientists and researchers who require a high-density information environment that remains legible and stress-free during prolonged analysis.

The visual style is **Corporate / Modern** with a lean toward **Scientific Minimalism**. It prioritizes functional aesthetics over decorative elements, using purposeful color application to guide the eye through complex simulation outputs. The interface should feel like a sophisticated laboratory instrument—robust, reliable, and transparent.

## Colors

The palette is grounded in "Authoritative Water Blue" to establish trust and "Natural Green" to reflect the environmental context.

- **Primary & Secondary:** Use for navigational headers, primary actions, and brand identification.
- **Neutral:** The background (#F7F9FB) is slightly cool-toned to reduce eye strain compared to pure white.
- **Data Accents:** Use the dedicated Orange and Bright Blue specifically for time-series comparisons (Predicted vs. Actual) to ensure immediate cognitive mapping.
- **Semantic Colors:** Standard red for error states and green for success should be used sparingly to maintain the professional tone.

## Typography

The system utilizes **Inter** for its exceptional legibility in data-heavy UI. For technical metadata, coordinate readouts, and CSV previews, **Space Grotesk** is employed to provide a rhythmic, technical feel that distinguishes raw data from UI labels.

Maintain high contrast between headers and body text. Use `label-caps` for table headers and sidebar category titles to create clear structural hierarchy.

## Layout & Spacing

The layout follows a **Streamlit-inspired sidebar model**.

- **Sidebar:** Fixed to the left (320px), containing all simulation parameters, file uploads, and configuration toggles. It should have a slightly darker background (#EDF2F7) than the main canvas.
- **Main Canvas:** A fluid grid that expands to fill available width, optimized for large Plotly visualizations.
- **Rhythm:** Use an 8px baseline grid. Components within cards should use a tight 12px vertical gap (`stack_gap`) to maximize information density without clutter.

## Elevation & Depth

This system uses **Tonal Layers** and **Low-Contrast Outlines** rather than heavy shadows.

- **Surface 0 (Background):** #F7F9FB.
- **Surface 1 (Cards/Sidebar):** Pure white (#FFFFFF) with a 1px solid border (#E2E8F0).
- **Depth:** Reserve soft, ambient shadows (0px 4px 12px rgba(10, 77, 104, 0.05)) exclusively for floating modals or active dropdown menus. This flat approach ensures that the focus remains on the data visualizations.

## Shapes

A **Soft (0.25rem)** roundedness is applied across the system. This subtle rounding prevents the UI from feeling aggressive or "brutalist" while maintaining a precise, engineered appearance. Large containers like data cards may use `rounded-lg` (0.5rem) to softly frame complex charts.

## Components

- **Buttons:**
  - _Primary (Run Simulation):_ Solid #0A4D68 background, white text, bold weight.
  - _Secondary (Download CSV):_ Outline style with #088395 border and text.
- **Data Cards:** White background, subtle 1px border. Use a top-accent bar (3px height) in the primary teal to denote active status. Include a header area for "SHAP Insights" with an info-icon tooltip.
- **Input Fields:** Flat styling with #E2E8F0 borders. On focus, use a 2px stroke of #088395. Labels should always be visible above the input.
- **Charts:**
  - Thin, light-gray grid lines (#EDF2F7).
  - No outer borders on chart canvases.
  - Interactive legends positioned at the top-right.
- **Data Tables:** Zebra-striping with #F7F9FB on alternate rows. High-contrast #1A202C text for cell values, using the Monospace font for numerical columns.
- **Status Chips:** Small, pill-shaped indicators for model status (e.g., "Converged", "Running", "Failed") using muted semantic background colors with high-contrast text.
