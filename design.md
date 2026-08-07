# Claude Academy Design System Specification

## 1. Overview & Visual Identity

The **Claude Academy Design System** is an editorial, warm, and highly readable design language. It combines academic elegance with clean digital product utility. Key characteristics include:

- **Warm Neutral Foundation**: Soft ivory and cream backgrounds (`#F9F8F3`, `#F2EFE7`) replace stark whites or cold grays.
- **Editorial Typography**: A dual-family typography strategy pairing a Serif typeface for titles and headings with a high-legibility Sans-Serif typeface for body text and controls.
- **Minimalist Line-Art & Badging**: Clean monoline SVG/illustration containers coupled with crisp dark status tags (e.g. `Claude Code 101`).
- **Structured Progress & Checklist Components**: Distinct visual states for course modules (filled circle checkmarks for completed, hollow circles for pending) with soft hairline dividers.
- **Brand Accent Flexibility**: Preserving a primary blue accent (`#1648d8`) within the warm-neutral UI environment.

---

## 2. Typography System

### Font Families

- **Header Font (Serif)**: `Newsreader` → fallback `Georgia, serif`.
- **Body Font (Sans-Serif)**: `Inter` → fallback `system-ui, -apple-system, sans-serif`.
- **Monospace Font**: `Space Grotesk` or `JetBrains Mono` → fallback `"Courier New", monospace`.

> **Licensing note:** `Newsreader`, `Inter`, `Space Grotesk`, and `JetBrains Mono` are all free, self-hostable Google Fonts. `Tiempos Text`, `Galaxie Copernicus`, and `Styrene` (listed as alternates in earlier drafts of this spec) are **commercial, licensed typefaces** from Klim, Klim, and Commercial Type respectively — using them requires a paid license and cannot simply be pulled from Google Fonts. Section 5's implementation plan already defaults to the free set, so no action is needed unless you specifically want the licensed alternates.

### Type Scale & Hierarchy

| Element | Font Family | Size | Weight | Line Height | Letter Spacing | Color Token |
|---|---|---|---|---|---|---|
| **Hero Title (H1)** | Serif | `36px – 44px` | `600` | `1.15` | `-0.02em` | `--text-primary` |
| **Section Title (H2)** | Serif | `24px – 28px` | `600` | `1.25` | `-0.01em` | `--text-primary` |
| **Card Header (H3)** | Serif | `20px – 22px` | `600` | `1.30` | `0em` | `--text-primary` |
| **Module Group (H4)** | Sans-Serif | `16px – 18px` | `600` | `1.40` | `0em` | `--text-primary` |
| **Body Large** | Sans-Serif | `15px – 16px` | `400` | `1.55` | `0em` | `--text-secondary` |
| **Body Small** | Sans-Serif | `13px – 14px` | `400` | `1.50` | `0em` | `--text-secondary` |
| **Badge / Tag** | Sans-Serif | `11px – 12px` | `600` | `1.20` | `0.02em` | `--on-badge` |
| **List Item Text** | Serif | `16px` | `500` | `1.40` | `0em` | `--text-primary` |

> **Fixed:** the original table listed List Item Text as `Serif / Sans` at `16px`, while §4B's checklist markup separately specified `17px Serif`. Those two are now reconciled to a single value (`16px`, Serif, `500`) so the token table and the component spec don't drift apart.

---

## 3. Color Palette & Tokens

```css
:root {
  /* Surface & Backgrounds */
  --bg-app: #F9F8F3;                /* Main application canvas (warm ivory) */
  --bg-surface: #F2EFE7;            /* Sidebar & secondary background */
  --bg-card: #FFFFFF;               /* Primary card surface */
  --bg-card-alt: #F7F5EE;           /* Highlighted card / accordion container */
  --bg-badge: #191919;              /* Dark pill badge background */

  /* Text & Content */
  --text-primary: #191919;          /* Deep charcoal primary text */
  --text-secondary: #555555;        /* Neutral gray secondary text */
  --text-muted: #707070;            /* Muted detail text */
  --text-disabled: rgba(25, 25, 25, 0.38); /* Disabled-state text/icons */
  --on-badge: #FFFFFF;              /* Text on dark badges */

  /* Primary Brand Accent */
  --primary: #1648d8;
  --primary-hover: #1036aa;
  --primary-light: #E8EEFF;
  --primary-border: #9BB3FF;

  /* Borders & Dividers */
  --border-light: #E6E2D8;
  --border-subtle: #EAE6DD;
  --border-focus: #1648d8;

  /* Status & Checklist Colors */
  --status-complete: #191919;
  --status-pending: #888888;

  /* Shadow & Elevation */
  --shadow-card: 0 2px 8px rgba(0, 0, 0, 0.03);
  --shadow-hover: 0 4px 16px rgba(0, 0, 0, 0.06);

  /* Motion */
  --transition-fast: 120ms ease-out;   /* icon/state toggles */
  --transition-base: 200ms ease;       /* card hover, accordion expand */

  /* Spacing (4px base grid) */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-7: 32px;
  --space-8: 40px;
}
```

> **Accessibility fix — `--text-muted` changed from `#767676` to `#707070`.**
> Checked against `--bg-app` (`#F9F8F3`) using WCAG 2.1 relative luminance:
> - `#767676` on `#F9F8F3` → **4.27:1** — fails the 4.5:1 minimum for normal text (only passes at large-text sizes, 18px+/14px bold+).
> - `#707070` on `#F9F8F3` → **4.66:1** — passes AA for normal text.
>
> All other body/heading pairings in this palette were checked and pass comfortably:
> - `--text-primary` on `--bg-app`: **16.5:1** (AAA)
> - `--text-secondary` on `--bg-app`: **7.0:1** (AAA)
> - `--primary` on `--bg-app` (links): **6.7:1** (AA)
> - White on `--primary` (button text): **7.1:1** (AAA)
> - White on `--bg-badge` (badge text): **17.6:1** (AAA)
> - `--status-pending` stroke on `--bg-card` (non-text graphical object): **3.5:1** — passes the 3:1 minimum for UI components.

---

## 4. Component Patterns & Anatomy

### A. Course / Feature Card Container

- **Background**: `var(--bg-card)` or `var(--bg-card-alt)`
- **Border**: `1px solid var(--border-light)`
- **Border Radius**: `16px`
- **Padding**: `var(--space-6) var(--space-7)` (`24px 32px`)
- **Shadow**: `var(--shadow-card)`; on hover, `var(--shadow-hover)` with `transform: translateY(-2px)`, transition `var(--transition-base)`
- **Focus (keyboard nav)**: `outline: 2px solid var(--border-focus); outline-offset: 2px` — required if cards are interactive links, not just visual containers
- **Icon Box**: Line-art monoline icon container (`~72px × 72px`):
  - Stroke `1.5px–2px`, `var(--text-primary)`
  - Small dark badge pill (e.g. `Claude Code 101`) overlaid top-left
- **Card Content**:
  - Title: 22px Serif, `600`, `var(--text-primary)`
  - Description: 15px Sans-Serif, `var(--text-secondary)`, line-height `1.5`

```html
<a class="claude-card" href="..." tabindex="0">
  <div class="claude-card-icon-wrapper">
    <span class="claude-badge">Claude Code 101</span>
    <svg class="claude-icon" aria-hidden="true">...</svg>
  </div>
  <div class="claude-card-content">
    <h3 class="claude-card-title">Claude Code 101</h3>
    <p class="claude-card-desc">Learn how to use Claude Code effectively in your daily development workflow.</p>
  </div>
</a>
```

---

### B. Course Overview / Checklist (read-only progress display)

This component is a **status display, not an input control** — it shows a learner's progress through a course, it isn't meant to be toggled by clicking. That distinction matters for §5 below, so the markup here deliberately avoids `<input>`/checkbox semantics and uses accessible static markup instead.

- **Container**: vertical stack, `var(--bg-card)` background
- **Category Header** (collapsible trigger):
  - Chevron `▼` / `▶`, rotates with `var(--transition-fast)` on toggle
  - Font: 18px **Sans-Serif**, `600`, `var(--text-primary)` — *(the original spec said "Sans-Serif / Serif"; standardized to Sans-Serif to match the H4/Module Group row in the type table)*
  - `aria-expanded` reflects open/closed state on the trigger element
- **Checklist Item Row**:
  - Padding: `var(--space-4) 0` (`16px 0`) — *adjusted from `14px 0` so it sits on the 4px spacing grid; purely cosmetic, revert if you have a reason to keep 14px*
  - Border: `border-bottom: 1px solid var(--border-subtle)`
  - Status Icon (20px):
    - **Completed**: filled circle, `var(--status-complete)` fill, white checkmark
    - **Pending**: hollow circle, `2px` stroke, `var(--status-pending)`
  - Item Title: 16px Serif, `500`, `var(--text-primary)`

```html
<div class="claude-list-item complete">
  <span class="claude-check-icon complete" role="img" aria-label="Completed">✔</span>
  <span class="claude-list-title">What is the Claude Platform?</span>
</div>
<div class="claude-list-item pending">
  <span class="claude-check-icon pending" role="img" aria-label="Not started">○</span>
  <span class="claude-list-title">Choosing the right model</span>
</div>
```

> **Accessibility fix:** the original markup used bare `<span>` icons with no text alternative — a screen reader would announce nothing about completion state, only the glyph or nothing at all. Adding `role="img" aria-label="…"` gives assistive tech a status to announce. If a row is ever made clickable (e.g., "mark as complete"), use a real `<button aria-pressed="...">` instead of a styled `<span>`.

---

### C. Controls, Buttons & Inputs

- **Primary Buttons**:
  - Background: `var(--primary)` (or `var(--text-primary)` for a dark variant)
  - Text: White, Sans-Serif, `600`
  - Border Radius: `8px`; Padding: `10px 20px`
  - Hover: `var(--primary-hover)`, transition `var(--transition-fast)`
  - Focus-visible: `2px solid var(--border-focus)`, `outline-offset: 2px`
  - Disabled: `opacity: 0.38` (matches `--text-disabled`), `cursor: not-allowed`, no hover/focus styling
- **Secondary Buttons & Inputs**:
  - Background: `var(--bg-card)` or `var(--bg-surface)`
  - Border: `1px solid var(--border-light)`
  - Focus Ring: `2px solid var(--border-focus)`
  - Disabled: same treatment as above

---

## 5. Implementation Guidelines for Streamlit (`app.py`)

1. **Import Fonts**: Load Google Fonts `Newsreader`, `Inter`, and `Space Grotesk`/`JetBrains Mono` — all free, no licensing blockers (see §2).
2. **Theme Variables**: Configure `.streamlit/config.toml` with `backgroundColor = "#F9F8F3"` and `primaryColor = "#1648d8"`.
3. **Custom CSS Injection**:
   - Serif font (`Newsreader, Georgia, serif`) on `h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3`.
   - Warm backgrounds on `.stApp` (`--bg-app`) and the sidebar (`--bg-surface`).
   - Style `st.expander` as a bordered card: `1px solid var(--border-light)`, `16px` radius, custom chevron.
   - Style metrics/cards with `16px` radius, `1px solid var(--border-light)`, `var(--bg-card)` background.
4. **Rebuild the checklist as static HTML, not a restyled `st.checkbox`.**
   This is a change from the earlier draft, which said to reskin `[data-testid="stCheckbox"]` into the circular checkmark rows. Two problems with that:
   - **It's the wrong widget.** §4B's own markup is a read-only status row, not a toggle — `st.checkbox` is an interactive input with `checked`/`unchecked` boolean state tied to `st.session_state`, which is a mismatch for "show the learner what they've completed."
   - **It's fragile even if it were the right widget.** Streamlit's checkbox DOM is wrapped in auto-generated `st-emotion-cache-*` classes that change between releases and aren't meant to be styled against — the `data-testid` attributes (`stCheckbox`) are more stable, but deep visual overrides (turning a native checkbox into a filled/hollow circle with a custom checkmark) routinely break on Streamlit version upgrades, per Streamlit's own community/GitHub reports.

   Instead, render each row with `st.markdown(..., unsafe_allow_html=True)` using the markup in §4B directly — you get pixel-exact control and nothing to maintain against Streamlit's internal CSS. If a row does need to be clickable later, use `st.button` (which has a stabler `data-testid`) styled as the row, rather than reskinning `st.checkbox`.

---

## Changelog

- Fixed `List Item Text` size/family conflict between the type table (`16px`, ambiguous family) and §4B (`17px Serif`) — standardized to `16px Serif`.
- Fixed `--text-muted` (`#767676` → `#707070`): failed WCAG AA (4.27:1) for normal text on `--bg-app`; new value passes at 4.66:1. Documented full contrast audit for the palette.
- Standardized Category Header to Sans-Serif only (previously "Sans-Serif / Serif").
- Added a spacing scale (`--space-1`–`--space-8`) and adjusted checklist row padding (`14px`→`16px`) to sit on the grid.
- Added motion tokens (`--transition-fast`, `--transition-base`) and hover/focus/disabled states, which the original spec didn't define.
- Added a font-licensing note distinguishing free Google Fonts from commercial alternates (Tiempos Text, Galaxie Copernicus, Styrene).
- Flagged and fixed a missing screen-reader affordance on the checklist status icons.
- Replaced the `st.checkbox`-reskinning implementation plan with static HTML rendering, since the checklist is a status display and the checkbox-restyling approach is both semantically wrong and fragile across Streamlit versions.