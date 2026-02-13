# CLAUDE.md — PizzaOps Intelligence Platform

## Project Identity

- **Name**: PizzaOps Intelligence
- **Tagline**: Operations Analytics for Food Delivery Businesses
- **Parent Company**: JLWanalytics — Africa's Premier Data Refinery
- **Version**: 1.0.0-mvp
- **Stack**: Python 3.11+ / Streamlit / Pandas / Plotly / Scikit-learn / XGBoost
- **Target**: Small-to-medium food delivery businesses in South Africa

---

## 1. PROJECT CONTEXT & BUSINESS PROBLEM

### 1.1 The Client

Jozi Pizza Co. — a delivery-only pizza store in Johannesburg experiencing:

- Inconsistent delivery times (30-min target frequently missed)
- Rising customer complaints, even when deliveries are fast
- Zero operational visibility — no dashboards, no KPIs, no tracking
- Staff stuck in fixed roles with no rotation or performance tracking
- Peak hour (lunch + dinner) overload with no forecasting
- Area E and Area C showing systematic delivery delays

### 1.2 What This App Must Solve

The platform transforms raw operational data (CSV/Excel uploads) into actionable intelligence across two domains:

**Domain A — In-Store Operations (Preparation Pipeline)**
- Base preparation time analysis
- Styling time patterns
- Oven temperature and cooking duration correlations
- Boxing time efficiency
- Staff role performance (Order Taker, Dough Prep, Stylist, Oven Operator, Boxer)

**Domain B — Delivery & Customer Experience**
- Delivery duration analysis and area-based patterns
- Delivery driver performance benchmarking
- Customer complaint root cause analysis
- Order mode analysis (App, WhatsApp, Phone)
- Time-of-day impact on service quality

### 1.3 Key Analytical Questions the App Must Answer

| Type | Question |
|------|----------|
| Diagnostic | Which pipeline stage contributes most to total delay? |
| Diagnostic | Does oven temperature correlate with complaint rate? |
| Diagnostic | Which staff combinations produce bottlenecks? |
| Predictive | What order volume should we expect at a given hour? |
| Predictive | Can we predict complaint risk before dispatch? |
| Prescriptive | What is the optimal staff rotation schedule? |
| Prescriptive | Which areas need route optimization? |

### 1.4 Non-Negotiable Constraints (from the client)

- Solutions must be cost-conscious — the owner said: "Would love ideas that don't cost a fortune to implement"
- Complaints happen even when delivery is fast → the app MUST look beyond delivery speed for root causes
- Performance tracking is informal → the app must establish baseline KPIs
- Staff are hardworking but bottlenecks are invisible → the app must surface them without assigning blame

---

## 2. ARCHITECTURE OVERVIEW

### 2.1 System Design Philosophy

```
┌─────────────────────────────────────────────────────────┐
│                    STREAMLIT FRONTEND                    │
│  (Multi-page app with sidebar navigation)               │
├─────────────┬──────────────┬──────────────┬─────────────┤
│  📊 Pages   │  🧠 ML       │  📦 Data     │  🎨 UI      │
│  (views)    │  (models)    │  (pipeline)  │  (components)│
├─────────────┴──────────────┴──────────────┴─────────────┤
│                    BUSINESS LOGIC LAYER                  │
│  (KPI calculations, process mining, alerting rules)     │
├─────────────────────────────────────────────────────────┤
│                    DATA ACCESS LAYER                     │
│  (Pandas DataFrames, SQLite for persistence, caching)   │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Design Principles

1. **Separation of Concerns**: Pages only handle layout. Business logic lives in `/core`. ML lives in `/ml`. Data processing lives in `/data`.
2. **Cache Everything Expensive**: Use `@st.cache_data` for data loads, `@st.cache_resource` for ML models.
3. **Fail Gracefully**: Every data operation wrapped in try/except. Show user-friendly errors. Never crash.
4. **Mobile-Aware**: Use `st.columns()` responsively. Test at 768px width. The store owner will check this on his phone.
5. **South African Context**: Currency in ZAR (R). Date format DD/MM/YYYY. Distance in km. Temperature in °C.

---

## 3. PROJECT FILE STRUCTURE

```
pizzaops-intelligence/
│
├── CLAUDE.md                          # THIS FILE — master reference
├── README.md                          # User-facing docs
├── requirements.txt                   # Python dependencies
├── .streamlit/
│   └── config.toml                    # Streamlit theme configuration
│
├── app.py                             # 🚀 MAIN ENTRY POINT — Streamlit multipage app root
│
├── pages/                             # 📊 STREAMLIT PAGES (auto-detected by Streamlit)
│   ├── 1_📊_Executive_Dashboard.py    # KPI overview, summary metrics, health score
│   ├── 2_🏭_Process_Analysis.py       # In-store pipeline breakdown
│   ├── 3_🚚_Delivery_Intelligence.py  # Delivery performance, area analysis
│   ├── 4_😤_Complaint_Engine.py       # Complaint root cause & prediction
│   ├── 5_👥_Staff_Analytics.py        # Staff performance & scheduling
│   ├── 6_🔮_Demand_Forecasting.py     # Time-series forecasting module
│   └── 7_📋_Report_Generator.py       # Auto-generate PDF/PPT reports
│
├── core/                              # 💼 BUSINESS LOGIC
│   ├── __init__.py
│   ├── kpi_engine.py                  # All KPI calculations
│   ├── process_mining.py              # Pipeline stage analysis
│   ├── bottleneck_detector.py         # Bottleneck identification algorithms
│   ├── alert_rules.py                 # Threshold-based alerting logic
│   └── constants.py                   # App-wide constants, thresholds, configs
│
├── data/                              # 📦 DATA PIPELINE
│   ├── __init__.py
│   ├── loader.py                      # CSV/Excel ingestion, validation, cleaning
│   ├── transformer.py                 # Feature engineering, computed columns
│   ├── schema.py                      # Expected column schemas & validation rules
│   ├── sample_data.py                 # Sample/demo dataset generator
│   └── cache_manager.py              # Session state & caching utilities
│
├── ml/                                # 🧠 MACHINE LEARNING
│   ├── __init__.py
│   ├── demand_forecast.py             # ARIMA, Prophet, XGBoost ensemble forecaster
│   ├── complaint_predictor.py         # XGBoost binary classifier for complaint risk
│   ├── delivery_estimator.py          # Delivery time regression model
│   ├── feature_engineering.py         # ML-specific feature creation
│   ├── model_evaluator.py             # Cross-validation, metrics, comparison
│   └── explainability.py              # SHAP values, feature importance viz
│
├── ui/                                # 🎨 REUSABLE UI COMPONENTS
│   ├── __init__.py
│   ├── metrics_cards.py               # KPI card components (styled)
│   ├── charts.py                      # Plotly chart factory functions
│   ├── tables.py                      # Styled dataframe displays
│   ├── filters.py                     # Sidebar filter components (date, area, staff)
│   ├── theme.py                       # Color palette, fonts, Plotly template
│   └── layout.py                      # Page header, footer, spacing helpers
│
├── reports/                           # 📋 REPORT GENERATION
│   ├── __init__.py
│   ├── pdf_builder.py                 # PDF report generation (FPDF2 or ReportLab)
│   └── pptx_builder.py               # PowerPoint generation (python-pptx)
│
├── assets/                            # 🖼️ STATIC ASSETS
│   ├── logo.png                       # PizzaOps logo
│   ├── jlw_logo.png                   # JLWanalytics branding
│   └── sample_dataset.xlsx            # Bundled demo dataset
│
└── tests/                             # ✅ TESTS
    ├── test_kpi_engine.py
    ├── test_loader.py
    ├── test_demand_forecast.py
    └── test_complaint_predictor.py
```

---

## 4. CONFIGURATION & THEME

### 4.1 Streamlit Config (`.streamlit/config.toml`)

```toml
[theme]
primaryColor = "#FF6B35"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#1A1F2E"
textColor = "#FAFAFA"
font = "sans serif"

[server]
maxUploadSize = 50
enableCORS = false

[browser]
gatherUsageStats = false
```

### 4.2 Color Palette (`ui/theme.py`)

```python
COLORS = {
    # Primary brand
    "primary": "#FF6B35",         # Pizza orange
    "primary_dark": "#E55A2B",
    "primary_light": "#FF8F66",

    # Semantic
    "success": "#10B981",         # Green — on target
    "warning": "#F59E0B",         # Amber — approaching threshold
    "danger": "#EF4444",          # Red — breached threshold
    "info": "#3B82F6",            # Blue — informational

    # Neutral
    "bg_dark": "#0E1117",
    "bg_card": "#1A1F2E",
    "bg_hover": "#242B3D",
    "text_primary": "#FAFAFA",
    "text_secondary": "#94A3B8",
    "text_muted": "#64748B",
    "border": "#334155",

    # Chart palette (categorical — 8 distinct colors)
    "chart_palette": [
        "#FF6B35", "#3B82F6", "#10B981", "#F59E0B",
        "#8B5CF6", "#EC4899", "#06B6D4", "#84CC16"
    ],

    # Stage colors (consistent across all views)
    "stage_dough_prep": "#8B5CF6",   # Violet
    "stage_styling": "#06B6D4",       # Cyan
    "stage_oven": "#F59E0B",          # Amber
    "stage_boxing": "#10B981",        # Green
    "stage_delivery": "#EC4899",      # Pink
}

# Plotly template — apply to ALL charts for consistency
PLOTLY_TEMPLATE = {
    "layout": {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": "#94A3B8", "family": "DM Sans, sans-serif"},
        "xaxis": {"gridcolor": "#1E293B", "zerolinecolor": "#334155"},
        "yaxis": {"gridcolor": "#1E293B", "zerolinecolor": "#334155"},
        "colorway": COLORS["chart_palette"],
        "margin": {"l": 40, "r": 20, "t": 40, "b": 40},
    }
}
```

### 4.3 Constants (`core/constants.py`)

```python
# ── Delivery Thresholds ──
DELIVERY_TARGET_MINUTES = 30          # Client's target
DELIVERY_WARNING_MINUTES = 25         # Alert 5 min before breach
DELIVERY_CRITICAL_MINUTES = 40        # Severely late

# ── Stage Duration Benchmarks (minutes) ──
STAGE_BENCHMARKS = {
    "dough_prep": {"target": 5, "p95_max": 8},
    "styling": {"target": 4, "p95_max": 7},
    "oven": {"target": 10, "p95_max": 14},
    "boxing": {"target": 2, "p95_max": 4},
}

# ── Oven Temperature ──
OVEN_TEMP_MIN_C = 220                 # Below this → quality risk
OVEN_TEMP_OPTIMAL_C = 260
OVEN_TEMP_MAX_C = 300                 # Above this → burn risk

# ── Complaint Categories ──
COMPLAINT_CATEGORIES = [
    "late_delivery", "cold_food", "wrong_order",
    "poor_quality", "missing_items", "rude_driver", "other"
]

# ── Order Modes ──
ORDER_MODES = ["app", "whatsapp", "phone"]

# ── Delivery Areas ──
DELIVERY_AREAS = ["A", "B", "C", "D", "E"]

# ── Peak Hours ──
PEAK_LUNCH = (11, 14)                 # 11:00 - 14:00
PEAK_DINNER = (17, 21)               # 17:00 - 21:00

# ── KPI Targets ──
KPI_TARGETS = {
    "on_time_pct": 85.0,              # % orders under 30 min
    "complaint_rate_pct": 5.0,         # % orders with complaints
    "avg_delivery_min": 25.0,          # Target average
    "avg_prep_min": 20.0,             # Total prep pipeline target
}
```

---

## 5. DATA LAYER — DETAILED SPECIFICATION

### 5.1 Expected Input Schema (`data/schema.py`)

The app must accept CSV or Excel files. The following columns are expected. The loader must handle missing columns gracefully (warn, don't crash) and be case-insensitive on column names.

```python
EXPECTED_COLUMNS = {
    # ── Order Identification ──
    "order_id":             {"type": "str",      "required": True,  "desc": "Unique order identifier"},
    "order_date":           {"type": "datetime",  "required": True,  "desc": "Date of order"},
    "order_time":           {"type": "time",      "required": True,  "desc": "Time order was placed"},
    "order_mode":           {"type": "category",  "required": True,  "desc": "app | whatsapp | phone"},

    # ── Staff Assignments ──
    "order_taker":          {"type": "str",      "required": False, "desc": "Name of order taker"},
    "dough_prep_staff":     {"type": "str",      "required": False, "desc": "Name of dough prep staff"},
    "stylist":              {"type": "str",      "required": False, "desc": "Name of pizza stylist"},
    "oven_operator":        {"type": "str",      "required": False, "desc": "Name of oven operator"},
    "boxer":                {"type": "str",      "required": False, "desc": "Name of boxer"},
    "delivery_driver":      {"type": "str",      "required": True,  "desc": "Name of delivery driver"},

    # ── Stage Durations (minutes) ──
    "dough_prep_time":      {"type": "float",    "required": True,  "desc": "Minutes for dough preparation"},
    "styling_time":         {"type": "float",    "required": True,  "desc": "Minutes for styling/topping"},
    "oven_time":            {"type": "float",    "required": True,  "desc": "Minutes in oven"},
    "boxing_time":          {"type": "float",    "required": True,  "desc": "Minutes to box"},

    # ── Oven Data ──
    "oven_temperature":     {"type": "float",    "required": False, "desc": "Oven temp in °C"},

    # ── Delivery Data ──
    "delivery_area":        {"type": "category",  "required": True,  "desc": "Delivery zone: A, B, C, D, E"},
    "delivery_duration":    {"type": "float",    "required": True,  "desc": "Minutes from dispatch to arrival"},

    # ── Complaint Data ──
    "complaint":            {"type": "bool",     "required": True,  "desc": "Whether a complaint was filed"},
    "complaint_reason":     {"type": "str",      "required": False, "desc": "Category or text of complaint"},
}
```

### 5.2 Data Loader (`data/loader.py`)

Responsibilities:
1. Accept `.csv`, `.xlsx`, `.xls` via `st.file_uploader`
2. Normalize column names: `strip().lower().replace(" ", "_")`
3. Validate against schema — log warnings for missing optional columns
4. Parse dates and times into proper datetime objects
5. Convert categorical columns to pandas Categorical type
6. Drop fully empty rows
7. Return a clean DataFrame + a validation report dict

```python
def load_and_validate(uploaded_file) -> tuple[pd.DataFrame, dict]:
    """
    Returns:
        df: Cleaned DataFrame
        report: {
            "rows_raw": int,
            "rows_clean": int,
            "rows_dropped": int,
            "missing_columns": list[str],
            "warnings": list[str],
            "status": "success" | "warning" | "error"
        }
    """
```

### 5.3 Feature Engineering (`data/transformer.py`)

Computed columns to add AFTER loading:

```python
COMPUTED_COLUMNS = {
    # ── Time-based ──
    "total_prep_time":      "dough_prep_time + styling_time + oven_time + boxing_time",
    "total_process_time":   "total_prep_time + delivery_duration",
    "delivery_target_met":  "total_process_time <= 30",
    "hour_of_day":          "extract hour from order_time",
    "day_of_week":          "extract day name from order_date",
    "is_peak_hour":         "hour_of_day in PEAK_LUNCH or PEAK_DINNER range",
    "is_weekend":           "day_of_week in ['Saturday', 'Sunday']",

    # ── Oven Quality ──
    "oven_temp_zone":       "'cold' if <220, 'optimal' if 220-300, 'hot' if >300",
    "oven_temp_deviation":  "abs(oven_temperature - OVEN_TEMP_OPTIMAL_C)",

    # ── Delay Classification ──
    "delay_category":       "'on_time' if <=25, 'at_risk' if 25-30, 'late' if 30-40, 'critical' if >40",

    # ── Stage Proportion ──
    "pct_dough_prep":       "dough_prep_time / total_prep_time * 100",
    "pct_styling":          "styling_time / total_prep_time * 100",
    "pct_oven":             "oven_time / total_prep_time * 100",
    "pct_boxing":           "boxing_time / total_prep_time * 100",
}
```

### 5.4 Sample Data Generator (`data/sample_data.py`)

Generate a realistic demo dataset with ~500 orders when no file is uploaded. Must include:
- Realistic distributions per stage (dough prep: mean=5, std=1.5)
- Area E and C with systematically higher delivery times
- Higher complaint rates during peak hours
- Some complaints even on fast deliveries (quality issues)
- 3-5 named staff per role
- Orders spread across 30 days, all three order modes
- Oven temperature variation with occasional cold ovens

This allows the app to be demo-ready without requiring a data upload.

---

## 6. PAGE SPECIFICATIONS — DETAILED

### 6.1 `app.py` — Main Entry Point

**Purpose**: Welcome page, data upload, session state initialization, navigation setup.

**Layout**:
```
┌─────────────────────────────────────┐
│  🍕 PizzaOps Intelligence           │
│  Operations Analytics Platform       │
│  by JLWanalytics                     │
├─────────────────────────────────────┤
│                                      │
│  [Upload your data]                  │
│  .csv or .xlsx file                  │
│                                      │
│  ── OR ──                            │
│                                      │
│  [▶ Load Demo Dataset]              │
│                                      │
├─────────────────────────────────────┤
│  Data Quality Report                 │
│  ✓ 487 orders loaded                 │
│  ✓ 12 columns validated             │
│  ⚠ 3 rows dropped (missing values)  │
│  ✓ Date range: 01/01 - 30/01/2026   │
├─────────────────────────────────────┤
│  Quick Stats (3 metric cards)        │
│  [Total Orders] [Date Range] [Areas]│
└─────────────────────────────────────┘
```

**Logic**:
1. Initialize `st.session_state.df` = None
2. Show file uploader (accept csv, xlsx, xls)
3. On upload: run `load_and_validate()` → `transform()` → store in session state
4. Show validation report
5. If data loaded: show quick stats and prompt user to navigate to pages
6. If no data: show demo option and explain what each page does

**Session State Keys**:
```python
st.session_state.df              # Main DataFrame (cleaned + engineered)
st.session_state.data_report     # Validation report dict
st.session_state.upload_time     # When data was loaded
st.session_state.filters         # Active global filters (date range, area, etc.)
```

---

### 6.2 Page 1: `📊 Executive Dashboard`

**Purpose**: High-level health check. The store owner opens this daily. Must answer: "How is my business doing right now?"

**Target User**: Store Owner (strategic view)

**Layout**:
```
┌────────────────────────────────────────────────────────────┐
│  EXECUTIVE DASHBOARD                     [Date Range Filter]│
├──────────┬──────────┬──────────┬──────────┬────────────────┤
│  📦 Total │  ⏱ Avg   │  ✅ On    │  😤 Comp- │  🔥 Peak     │
│  Orders   │  Delivery │  Time %  │  laint % │  Hour Load    │
│  487      │  27.3 min │  72.4%   │  8.2%    │  6PM: 34/hr  │
│  ↑12% wow │  ↓2.1 min │  ↑5.2pp  │  ↓1.1pp  │  ↑8 vs avg   │
├──────────┴──────────┴──────────┴──────────┴────────────────┤
│                                                             │
│  📈 Delivery Time Trend (line chart — daily avg over time)  │
│  [Shows 30-min target line in red dashed]                   │
│                                                             │
├─────────────────────────┬───────────────────────────────────┤
│  🥧 Complaint Breakdown │  📊 Orders by Area (bar chart)    │
│  (donut chart by reason)│  [Avg delivery time overlay]      │
│                          │                                   │
├─────────────────────────┴───────────────────────────────────┤
│  📋 Today's Alerts                                           │
│  🔴 Area E avg delivery: 38.2 min (target: 30 min)         │
│  🟡 Complaint rate at 9.1% (target: 5%)                    │
│  🟢 Oven temperature stable at 258°C                        │
└─────────────────────────────────────────────────────────────┘
```

**KPI Cards** (use `ui/metrics_cards.py`):
Each card displays: metric name, current value, trend vs previous period, color-coded status (green/amber/red based on thresholds from `constants.py`). Use `st.metric()` wrapped in styled containers.

**Charts**:
1. **Delivery Time Trend** — `plotly.express.line`: x=date, y=avg_total_process_time, add horizontal line at 30 min
2. **Complaint Breakdown** — `plotly.express.pie`: values=count per complaint_reason, hole=0.45 for donut
3. **Orders by Area** — `plotly.express.bar`: x=delivery_area, y=count, with secondary y-axis for avg delivery time
4. **Alerts Panel** — custom component: scan KPIs against thresholds, generate alert cards with severity colors

---

### 6.3 Page 2: `🏭 Process Analysis`

**Purpose**: Deep-dive into the preparation pipeline. Answers: "Where are the bottlenecks in our kitchen?"

**Target User**: Operations Manager

**Layout**:
```
┌──────────────────────────────────────────────────────────────┐
│  PROCESS ANALYSIS                    [Date] [Hour] [Staff]   │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Pipeline Stage Breakdown (stacked bar chart)                │
│  [Dough Prep | Styling | Oven | Boxing] per order            │
│  Shows which stage dominates total prep time                 │
│                                                               │
├──────────────────────────────┬────────────────────────────────┤
│  Stage Duration Distributions│  Bottleneck Heatmap            │
│  (box plots — one per stage) │  (stage × hour_of_day)        │
│  Shows P25, median, P75, P95│  Color = avg duration          │
│  + outlier detection         │  Red cells = bottleneck        │
│                              │                                │
├──────────────────────────────┴────────────────────────────────┤
│                                                               │
│  ⚠ Bottleneck Detection Results                              │
│  "Oven stage is the primary bottleneck during 17:00-20:00,   │
│   with P95 duration of 16.2 min (benchmark: 14 min).         │
│   Styling is secondary bottleneck during lunch (P95: 8.1 min │
│   vs benchmark 7 min)."                                      │
│                                                               │
├──────────────────────────────────────────────────────────────┤
│  Oven Temperature Analysis                                    │
│  Scatter: x=oven_temp, y=oven_time, color=complaint          │
│  "Orders at <230°C have 3x higher complaint rate"            │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

**Key Analysis Functions** (`core/process_mining.py`):

```python
def get_stage_breakdown(df) -> pd.DataFrame:
    """Aggregate mean, median, P95, std for each stage."""

def detect_bottlenecks(df) -> list[dict]:
    """
    For each stage, check if P95 exceeds benchmark.
    Returns list of {stage, p95_actual, benchmark, severity, peak_hours}.
    """

def stage_by_hour_heatmap(df) -> pd.DataFrame:
    """Pivot: rows=hour_of_day, cols=stage, values=avg duration."""

def oven_temp_analysis(df) -> dict:
    """
    Correlate oven_temperature with:
    - oven_time (should be inverse — hotter = faster)
    - complaint rate (cold oven → quality complaints)
    Returns correlation coefficients + segmented complaint rates.
    """
```

---

### 6.4 Page 3: `🚚 Delivery Intelligence`

**Purpose**: Analyze delivery performance by area, driver, time. Answers: "Why are Area E deliveries always late?"

**Target User**: Operations Manager

**Layout**:
```
┌──────────────────────────────────────────────────────────────┐
│  DELIVERY INTELLIGENCE                [Date] [Area] [Driver] │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Area Performance Comparison (grouped bar + box)             │
│  [Bar: avg delivery time per area]                           │
│  [Overlay: % on-time per area]                               │
│  [Highlight Area E and C in red]                             │
│                                                               │
├──────────────────────────────┬────────────────────────────────┤
│  Delivery Time by Hour       │  Area × Hour Heatmap          │
│  (line chart per area)       │  (red = delayed, green = ok)  │
│  Shows peak overlap clearly  │  Drill into worst combos      │
│                              │                                │
├──────────────────────────────┴────────────────────────────────┤
│                                                               │
│  Driver Performance Scorecards                                │
│  ┌──────────┬──────────┬──────────┬──────────┐              │
│  │ Driver A  │ Driver B  │ Driver C  │ Driver D │              │
│  │ 23.4 min  │ 28.7 min  │ 31.2 min  │ 26.1 min│              │
│  │ 91% on-time│ 78%      │ 65%       │ 84%     │              │
│  │ 2% compl  │ 5% compl │ 12% compl │ 3% compl│              │
│  └──────────┴──────────┴──────────┴──────────┘              │
│                                                               │
├──────────────────────────────────────────────────────────────┤
│  Order Mode Analysis                                          │
│  Bar chart: avg delivery time by order_mode                   │
│  "WhatsApp orders average 2.3 min faster — likely more       │
│   complete order info reduces prep clarification delays"      │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

**Key Analysis Functions** (`core/kpi_engine.py`):

```python
def delivery_by_area(df) -> pd.DataFrame:
    """Group by area: avg, median, P95 delivery time, on_time_pct, complaint_rate."""

def driver_scorecards(df) -> pd.DataFrame:
    """Group by driver: total deliveries, avg time, on_time_pct, complaint_rate, areas served."""

def area_hour_matrix(df) -> pd.DataFrame:
    """Pivot: rows=area, cols=hour, values=avg delivery time. Highlight cells > 30 min."""

def order_mode_comparison(df) -> pd.DataFrame:
    """Group by order_mode: avg total time, avg delivery time, complaint rate."""
```

---

### 6.5 Page 4: `😤 Complaint Engine`

**Purpose**: Root cause analysis for complaints. THE MOST IMPORTANT PAGE. Directly addresses: "We get complaints even when delivery is fast."

**Target User**: Store Owner + Operations Manager

**Layout**:
```
┌──────────────────────────────────────────────────────────────┐
│  COMPLAINT INTELLIGENCE ENGINE       [Date] [Area] [Reason]  │
├──────────────────────────────────────────────────────────────┤
│  KPI Row                                                      │
│  [Total Complaints] [Complaint Rate] [Top Reason] [Worst Area]│
├──────────────────────────────┬────────────────────────────────┤
│  Complaints by Reason        │  Complaints by Hour of Day     │
│  (horizontal bar chart)      │  (bar chart)                   │
│  Ranked by frequency         │  Peaks visible at lunch/dinner │
│                              │                                │
├──────────────────────────────┴────────────────────────────────┤
│                                                               │
│  🔍 Root Cause Matrix (THE KEY INSIGHT)                      │
│  Cross-tabulation heatmap:                                    │
│  Rows: complaint_reason                                       │
│  Cols: delivery_target_met (Yes / No)                        │
│  "34% of complaints come from ON-TIME deliveries.            │
│   These are QUALITY complaints (cold food, wrong order),     │
│   not speed complaints."                                      │
│                                                               │
├──────────────────────────────────────────────────────────────┤
│  Feature Importance (from ML model)                           │
│  SHAP bar chart: which features predict complaints?           │
│  Top predictors: oven_temp, is_peak_hour, stylist,           │
│  delivery_area, total_prep_time                              │
│                                                               │
├──────────────────────────────────────────────────────────────┤
│  🎯 Complaint Risk Scorer (Interactive)                      │
│  Input sliders: oven_temp, area, hour, staff                 │
│  Output: "Predicted complaint probability: 23%"              │
│  + SHAP waterfall explaining why                             │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

**Key Insight to Surface**: The owner said complaints happen even when delivery is fast. The Root Cause Matrix MUST clearly show that a significant portion of complaints are quality-driven (cold food from low oven temp, wrong orders from certain stylists), not just speed-driven. This is the "aha moment" of the app.

**ML Model** (`ml/complaint_predictor.py`):

```python
class ComplaintPredictor:
    """
    Binary classifier: complaint = True/False

    Features:
        - total_prep_time
        - delivery_duration
        - oven_temperature
        - is_peak_hour
        - delivery_area (one-hot encoded)
        - order_mode (one-hot encoded)
        - hour_of_day
        - day_of_week
        - stylist (label encoded)
        - oven_operator (label encoded)

    Model: XGBoost with class_weight='balanced' (complaints are minority class)

    Outputs:
        - probability: float (0-1)
        - prediction: bool
        - shap_values: array (for explainability)
        - feature_importance: dict

    Evaluation:
        - Stratified 5-fold CV
        - Metrics: F1 (primary), Precision, Recall, AUC-ROC
        - Confusion matrix visualization
    """

    def train(self, df: pd.DataFrame) -> dict:
        """Train model, return metrics dict."""

    def predict_proba(self, features: pd.DataFrame) -> np.ndarray:
        """Return complaint probability for each row."""

    def explain(self, features: pd.Series) -> dict:
        """SHAP waterfall for a single order."""
```

---

### 6.6 Page 5: `👥 Staff Analytics`

**Purpose**: Performance tracking per staff member. Addresses: "No performance tracking exists."

**Target User**: Operations Manager

**Layout**:
```
┌──────────────────────────────────────────────────────────────┐
│  STAFF ANALYTICS                     [Role Filter] [Date]    │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Staff Performance Table (sortable, filterable)              │
│  | Name | Role | Orders | Avg Time | P95 | Complaint% | Trend│
│  Shows all staff with color-coded performance cells          │
│                                                               │
├──────────────────────────────┬────────────────────────────────┤
│  Performance by Role         │  Fatigue Analysis              │
│  (box plot: duration per     │  (line: performance vs hours   │
│   staff within each role)    │   into shift)                  │
│  Identifies fast vs slow     │  "Driver C degrades after      │
│  performers                  │   4 hours on shift"            │
│                              │                                │
├──────────────────────────────┴────────────────────────────────┤
│                                                               │
│  Staff Combination Analysis                                   │
│  Heatmap: stylist × oven_operator → avg total prep time      │
│  "When Stylist B works with Oven Op A, prep is 22% faster"   │
│                                                               │
├──────────────────────────────────────────────────────────────┤
│  📋 Recommendations                                          │
│  • Rotate Driver C to less demanding areas after hour 4      │
│  • Pair Stylist B with Oven Op A during peak hours           │
│  • Dough Prep staff are consistent — no action needed        │
└──────────────────────────────────────────────────────────────┘
```

**Important**: Frame staff insights constructively. Never say "Staff X is bad." Say "Staff X may benefit from additional support during peak hours" or "Staff X shows opportunity for improvement in [specific metric]." The app is a tool for optimization, not blame.

---

### 6.7 Page 6: `🔮 Demand Forecasting`

**Purpose**: Predict future order volumes using time-series ML. DIRECTLY applies the HealthForecast AI methodology (ARIMA + LSTM + XGBoost ensemble).

**Target User**: Operations Manager + Store Owner

**Layout**:
```
┌──────────────────────────────────────────────────────────────┐
│  DEMAND FORECASTING ENGINE           [Forecast Horizon]      │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Historical Demand Pattern                                    │
│  (line chart: orders per hour over historical period)        │
│  Seasonal decomposition: trend + weekly + daily + residual   │
│                                                               │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  📈 Forecast (next 24h / 7 days)                            │
│  Line chart: actual (solid) + forecast (dashed) +            │
│  confidence interval (shaded band)                           │
│                                                               │
│  Model selector: [ARIMA] [Prophet] [XGBoost] [Ensemble]     │
│  Show all models overlaid for comparison                     │
│                                                               │
├──────────────────────────────┬────────────────────────────────┤
│  Model Comparison Table      │  Staffing Recommendation      │
│  | Model  | RMSE | MAE |MAPE│  Based on forecast:            │
│  | ARIMA  | 3.2  | 2.4 |8% │  "Tomorrow 6PM: expect 38      │
│  | Prophet| 2.8  | 2.1 |7% │   orders/hr. Recommend 3       │
│  | XGBoost| 2.5  | 1.9 |6% │   prep staff + 4 drivers."     │
│  | Ensemble| 2.3 | 1.7 |5% │                                │
│                              │  "Start extra dough at 17:00"  │
└──────────────────────────────┴────────────────────────────────┘
```

**ML Models** (`ml/demand_forecast.py`):

```python
class DemandForecaster:
    """
    Ensemble forecaster combining three approaches:
    1. ARIMA (statsmodels) — captures linear trends + seasonality
    2. Prophet (prophet) — handles holidays, multiple seasonalities
    3. XGBoost (xgboost) — captures nonlinear patterns via lag features

    Ensemble: Weighted average based on validation RMSE (inverse weighting)

    Input: Time series of order counts (hourly or daily granularity)

    Feature engineering for XGBoost:
        - hour_of_day, day_of_week, is_weekend, is_peak
        - lag_1h, lag_2h, lag_24h (same hour yesterday)
        - rolling_mean_3h, rolling_mean_24h
        - lag_168h (same hour last week)

    Evaluation: TimeSeriesSplit (no lookahead leakage)
    Metrics: RMSE (primary), MAE, MAPE
    """

    def fit(self, ts: pd.Series) -> dict:
        """Train all three models, compute ensemble weights."""

    def predict(self, horizon: int) -> pd.DataFrame:
        """
        Returns DataFrame with columns:
        timestamp, arima_pred, prophet_pred, xgboost_pred,
        ensemble_pred, lower_ci, upper_ci
        """

    def compare_models(self) -> pd.DataFrame:
        """Return metrics table comparing all models."""

    def staffing_recommendation(self, forecast: pd.DataFrame) -> list[dict]:
        """
        Map predicted order volume to staffing needs.
        Rules: 1 prep staff per 10 orders/hr, 1 driver per 5 orders/hr.
        Returns list of {hour, predicted_orders, recommended_prep, recommended_drivers}.
        """
```

---

### 6.8 Page 7: `📋 Report Generator`

**Purpose**: Auto-generate the client-ready deliverable. Outputs a PDF or PowerPoint matching the Vuuma case study requirements.

**Target User**: Analyst / Consultant (you presenting to the client)

**Layout**:
```
┌──────────────────────────────────────────────────────────────┐
│  REPORT GENERATOR                                            │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Report Configuration                                        │
│  Format: [PDF] [PowerPoint]                                  │
│  Date Range: [Start] → [End]                                │
│  Include Sections:                                           │
│    ☑ Executive Summary                                       │
│    ☑ Data Insights & Charts                                  │
│    ☑ Complaint Root Cause Analysis                           │
│    ☑ Recommendations                                         │
│    ☐ Demand Forecast                                         │
│    ☐ Staff Analytics                                         │
│                                                               │
│  [🔨 Generate Report]                                        │
│                                                               │
├──────────────────────────────────────────────────────────────┤
│  Preview                                                      │
│  [Rendered preview of key slides/pages]                      │
│                                                               │
├──────────────────────────────────────────────────────────────┤
│  [⬇ Download Report]                                         │
└──────────────────────────────────────────────────────────────┘
```

**Report Structure (matches Vuuma deliverable requirements)**:

- **Slide/Page 1: Executive Summary** — Top KPIs, key question addressed, 2-3 headline findings
- **Slide/Page 2: Data Insights** — Charts: delivery time by area, complaints by time of day, stage breakdown
- **Slide/Page 3: Root Cause Analysis** — The complaint matrix, oven temp correlation, staff patterns
- **Slide/Page 4: Recommendations** — Prioritized actions with expected impact, cost, and risk
- **Slide/Page 5 (Optional): Next Steps & Data Gaps** — What needs more investigation, what data to start collecting

---

## 7. ML PIPELINE — DETAILED

### 7.1 Feature Engineering (`ml/feature_engineering.py`)

```python
def create_ml_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform raw DataFrame into ML-ready feature matrix.

    Numerical features (keep as-is):
        - dough_prep_time, styling_time, oven_time, boxing_time
        - delivery_duration, total_prep_time, total_process_time
        - oven_temperature, oven_temp_deviation
        - hour_of_day

    Categorical features (encode):
        - delivery_area → one-hot (5 columns)
        - order_mode → one-hot (3 columns)
        - stylist → label encode (or target encode if >10 categories)
        - oven_operator → label encode
        - delivery_driver → label encode
        - day_of_week → cyclical encode (sin/cos)

    Binary features:
        - is_peak_hour, is_weekend

    Interaction features:
        - peak_x_area_E: is_peak_hour & (delivery_area == 'E')
        - oven_temp_x_oven_time: oven_temperature * oven_time
    """
```

### 7.2 Model Evaluation (`ml/model_evaluator.py`)

```python
def evaluate_classifier(model, X, y, cv=5) -> dict:
    """
    Stratified K-Fold cross-validation for complaint predictor.
    Returns: {
        'f1_mean', 'f1_std',
        'precision_mean', 'recall_mean',
        'auc_roc_mean',
        'confusion_matrix': np.ndarray,
        'cv_scores': list[float]
    }
    """

def evaluate_forecaster(model, ts, n_splits=3) -> dict:
    """
    TimeSeriesSplit cross-validation for demand forecaster.
    Returns: {
        'rmse_mean', 'rmse_std',
        'mae_mean', 'mape_mean',
        'fold_results': list[dict]
    }
    """
```

### 7.3 Explainability (`ml/explainability.py`)

```python
def shap_feature_importance(model, X) -> plotly.Figure:
    """Global SHAP bar chart — top 10 features by mean |SHAP value|."""

def shap_waterfall(model, X_single_row) -> plotly.Figure:
    """Single-order SHAP waterfall — explains one prediction."""

def shap_dependence(model, X, feature_name) -> plotly.Figure:
    """SHAP dependence plot — how one feature affects predictions."""
```

---

## 8. REUSABLE UI COMPONENTS

### 8.1 Metric Cards (`ui/metrics_cards.py`)

```python
def render_kpi_card(
    title: str,
    value: str,
    delta: str = None,              # e.g., "+12%" or "-2.1 min"
    delta_is_good: bool = True,     # True if increase is positive
    status: str = "neutral",        # "good" | "warning" | "danger" | "neutral"
    icon: str = None,               # Emoji
    target: str = None              # e.g., "Target: 30 min"
):
    """Render a styled KPI card using st.markdown with custom CSS."""
```

### 8.2 Chart Factory (`ui/charts.py`)

All chart functions return `plotly.graph_objects.Figure` with the app theme applied.

```python
def line_chart(df, x, y, title, target_line=None, color=None) -> go.Figure
def bar_chart(df, x, y, title, color=None, orientation="v") -> go.Figure
def box_plot(df, x, y, title, color=None) -> go.Figure
def heatmap(df, x, y, z, title, colorscale="RdYlGn_r") -> go.Figure
def donut_chart(df, names, values, title) -> go.Figure
def scatter(df, x, y, title, color=None, size=None, trendline=None) -> go.Figure
def stacked_bar(df, x, y_cols, title) -> go.Figure
```

### 8.3 Global Filters (`ui/filters.py`)

Sidebar filters that persist via session state and apply across all pages:

```python
def render_global_filters(df: pd.DataFrame) -> dict:
    """
    Renders in st.sidebar:
    - Date range picker (min/max from data)
    - Area multi-select (default: all)
    - Order mode multi-select (default: all)
    - Peak hours toggle

    Returns filter dict. All pages use this to filter their DataFrames.
    """

def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Apply the filter dict to a DataFrame. Returns filtered copy."""
```

---

## 9. DEPLOYMENT

### 9.1 Requirements (`requirements.txt`)

```
streamlit>=1.31.0
pandas>=2.1.0
numpy>=1.24.0
plotly>=5.18.0
scikit-learn>=1.3.0
xgboost>=2.0.0
statsmodels>=0.14.0
prophet>=1.1.5
shap>=0.44.0
openpyxl>=3.1.0
python-pptx>=0.6.21
fpdf2>=2.7.0
```

### 9.2 Streamlit Cloud Deployment

1. Push to GitHub repository
2. Connect to share.streamlit.io
3. Set `app.py` as entry point
4. No secrets needed for MVP (all data is uploaded by user)

### 9.3 Performance Guidelines

- Max dataset size for smooth UX: ~10,000 rows
- Use `@st.cache_data(ttl=300)` for data operations (5-min cache)
- Use `@st.cache_resource` for ML model objects (persist across sessions)
- Lazy-load ML models: only train when user navigates to forecasting/complaint pages
- Use `st.spinner()` for any operation >1 second
- Charts: limit to <5,000 data points per chart. Aggregate if larger.

---

## 10. CODE PATTERNS & CONVENTIONS

### 10.1 Page Template

Every page file follows this structure:

```python
"""
Page: [Page Name]
Purpose: [One sentence]
Target User: [Persona]
"""
import streamlit as st
import pandas as pd
from core.kpi_engine import relevant_function
from ui.charts import chart_function
from ui.filters import render_global_filters, apply_filters
from ui.layout import page_header

# ── Page Config ──
page_header(
    title="Page Title",
    icon="📊",
    description="What this page shows"
)

# ── Guard: Check Data Loaded ──
if "df" not in st.session_state or st.session_state.df is None:
    st.warning("⚠️ Please upload data on the Home page first.")
    st.stop()

# ── Load & Filter Data ──
df = st.session_state.df.copy()
filters = render_global_filters(df)
df_filtered = apply_filters(df, filters)

# ── KPI Row ──
col1, col2, col3, col4 = st.columns(4)
# ... render KPI cards

# ── Charts ──
# ... render visualizations

# ── Insights ──
# ... render automated insights text
```

### 10.2 Naming Conventions

```
Files:          snake_case.py
Classes:        PascalCase
Functions:      snake_case()
Constants:      UPPER_SNAKE_CASE
Session keys:   snake_case (no prefix)
CSS classes:    kebab-case
```

### 10.3 Error Handling Pattern

```python
def safe_compute(func, df, fallback="N/A"):
    """Wrap any computation that might fail on bad data."""
    try:
        return func(df)
    except Exception as e:
        st.warning(f"⚠️ Could not compute: {str(e)}")
        return fallback
```

### 10.4 Docstring Standard

Use Google-style docstrings on every public function:

```python
def detect_bottlenecks(df: pd.DataFrame, threshold_pct: float = 95) -> list[dict]:
    """Identify pipeline stages that exceed performance benchmarks.

    Args:
        df: DataFrame with stage duration columns.
        threshold_pct: Percentile to check against benchmarks.

    Returns:
        List of dicts with keys: stage, actual_p95, benchmark, severity, peak_hours.
    """
```

---

## 11. TESTING APPROACH

### 11.1 Critical Tests

```python
# test_kpi_engine.py
- test_on_time_percentage_calculation
- test_complaint_rate_handles_zero_orders
- test_delivery_by_area_returns_all_areas
- test_kpi_targets_threshold_logic

# test_loader.py
- test_csv_load_success
- test_xlsx_load_success
- test_missing_required_column_raises_warning
- test_column_name_normalization
- test_empty_file_handled_gracefully

# test_demand_forecast.py
- test_arima_fit_predict
- test_xgboost_lag_features_correct
- test_ensemble_weights_sum_to_one
- test_forecast_horizon_matches_request

# test_complaint_predictor.py
- test_model_trains_without_error
- test_prediction_returns_probability
- test_shap_values_align_with_features
- test_handles_unseen_categories
```

### 11.2 Run Tests

```bash
python -m pytest tests/ -v --tb=short
```

---

## 12. FUTURE SCALE PATH (Post-MVP)

This section is NOT for the Streamlit MVP but documents the evolution path:

| Phase | Trigger | Migration |
|-------|---------|-----------|
| **Phase 2** | First paying customer | Add SQLite persistence, basic auth |
| **Phase 3** | 5+ stores | Migrate to Next.js + FastAPI + PostgreSQL |
| **Phase 4** | 20+ stores | Multi-tenant, Paystack billing, WhatsApp API |

The Python ML code (`/ml` and `/core`) transfers DIRECTLY to FastAPI. Only the frontend changes. This is the key architectural advantage of keeping business logic separate from Streamlit pages.

---

## 13. QUICK REFERENCE — BUILD ORDER

When building this app, follow this sequence:

```
1. core/constants.py          → Define all thresholds and configs
2. data/schema.py             → Define expected columns
3. data/loader.py             → Build data ingestion
4. data/transformer.py        → Build feature engineering
5. data/sample_data.py        → Generate demo dataset
6. ui/theme.py                → Set up color palette & Plotly template
7. ui/metrics_cards.py        → Build KPI card component
8. ui/charts.py               → Build chart factory functions
9. ui/filters.py              → Build global filter sidebar
10. ui/layout.py              → Build page header/footer
11. app.py                    → Build main entry point with upload
12. core/kpi_engine.py        → Build KPI calculations
13. pages/1_Executive.py      → Build executive dashboard
14. core/process_mining.py    → Build bottleneck detection
15. pages/2_Process.py        → Build process analysis page
16. pages/3_Delivery.py       → Build delivery intelligence
17. pages/4_Complaint.py      → Build complaint analysis (no ML yet)
18. pages/5_Staff.py          → Build staff analytics
19. ml/feature_engineering.py → Build ML feature pipeline
20. ml/complaint_predictor.py → Build & integrate complaint ML
21. ml/demand_forecast.py     → Build forecasting models
22. ml/explainability.py      → Add SHAP explanations
23. pages/6_Forecasting.py    → Build forecast page
24. reports/pdf_builder.py    → Build PDF report generation
25. reports/pptx_builder.py   → Build PowerPoint generation
26. pages/7_Reports.py        → Build report generator page
27. tests/                    → Write and run tests
28. Deploy to Streamlit Cloud
```

---

*Built with purpose by JLWanalytics. Turning operational chaos into intelligence.*
