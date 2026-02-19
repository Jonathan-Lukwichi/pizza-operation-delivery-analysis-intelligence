# CLAUDE.md — PizzaOps Intelligence Platform

## Project Identity

- **Name**: PizzaOps Intelligence
- **Tagline**: Operations Analytics for Food Delivery Businesses
- **Parent Company**: JLWanalytics — Africa's Premier Data Refinery
- **Version**: 2.0.0 (Pure Python Analytics)
- **Stack**: Python 3.11+ / Streamlit / Pandas / Plotly / Scikit-learn
- **Target**: Small-to-medium food delivery businesses in South Africa

---

## Key Features

- **100% Offline** — Works during load shedding, no internet required
- **Zero Configuration** — Upload CSV/Excel, get instant insights
- **Smart Data Profiler** — Auto-detects column types and issues
- **Rule-Based Analytics** — Bottleneck detection, KPI tracking, alerts
- **WhatsApp Export** — One-click summary sharing with team
- **PDF Reports** — Professional reports for stakeholders

---

## Project Structure

```
pizzaops-intelligence/
├── Welcome.py                    # Landing page (entry point)
├── pages/
│   ├── 0_Process Configuration.py  # Setup targets FIRST
│   ├── 1_Home.py                   # Data upload & cleaning
│   ├── 2_Dashboard.py              # KPIs, trends, alerts
│   ├── 3_Problems.py               # Bottlenecks, issues
│   └── 4_Actions.py                # Recommendations, export
├── core/
│   ├── config.py                 # BusinessConfig dataclass
│   ├── local_analytics.py        # Rule-based analytics engine
│   └── data_profiler.py          # Smart data profiling
├── data/
│   ├── loader.py                 # CSV/Excel ingestion
│   └── transformer.py            # Feature engineering
├── ui/
│   ├── theme.py                  # Colors, Plotly template
│   ├── layout.py                 # Page headers, spacers
│   ├── metrics_cards.py          # KPI card components
│   ├── charts.py                 # Chart factory functions
│   └── filters.py                # Global filter sidebar
├── reports/
│   ├── pdf_builder.py            # PDF report generation
│   ├── pptx_builder.py           # PowerPoint generation
│   └── whatsapp_export.py        # WhatsApp summary
├── requirements.txt
└── .streamlit/config.toml
```

---

## User Flow

```
1. Welcome Page → Get Started
2. Process Configuration → Set delivery targets, thresholds
3. Home → Upload data, clean/validate, explore (EDA)
4. Dashboard → View KPIs, trends, alerts
5. Problems → Identify bottlenecks, staff gaps
6. Actions → Get recommendations, export reports
```

---

## Core Modules

### LocalAnalytics (`core/local_analytics.py`)

Rule-based analytics engine - NO AI required.

```python
class LocalAnalytics:
    def get_kpis(df) -> KPIResult           # Total orders, on-time %, complaint %
    def detect_bottlenecks(df) -> list      # Stages exceeding benchmarks
    def generate_alerts(df) -> list         # Threshold-based alerts
    def generate_recommendations(df) -> list # Prioritized actions
    def get_area_performance(df) -> list    # Performance by delivery area
    def get_stage_breakdown(df) -> dict     # Avg time per stage
    def get_trend_data(df, days) -> dict    # Daily trend data
```

### DataProfiler (`core/data_profiler.py`)

Intelligent data profiling without AI.

```python
class DataProfiler:
    def profile_column(col) -> ColumnProfile  # Type, issues, suggestions
    def get_issues() -> list                  # All detected issues
    def apply_action(df, action) -> df        # One-click fixes
```

### BusinessConfig (`core/config.py`)

Central configuration for business parameters.

```python
@dataclass
class BusinessConfig:
    business_name: str = "Pizza Business"
    delivery_target_minutes: int = 30
    on_time_target_pct: float = 85.0
    complaint_target_pct: float = 5.0
    stages: List[StageConfig]  # Pipeline stages with benchmarks
```

---

## Page Specifications

### 0. Process Configuration
- Set business name, tagline
- Configure delivery targets (30 min default)
- Set KPI thresholds (on-time %, complaint %)
- Define peak hours (lunch, dinner)
- Configure pipeline stages with benchmarks

### 1. Home (Data Upload)
- File upload (CSV/Excel)
- Data validation report
- Smart data profiler with one-click fixes
- EDA section with charts
- Mark data as clean to unlock other pages

### 2. Dashboard
- 4 KPI cards: Orders, On-Time %, Complaint %, Avg Delivery
- Alerts section (threshold-based)
- Stage performance chart (actual vs benchmark)
- Area performance chart
- 7-day trend chart

### 3. Problems
- Pipeline bottlenecks (ranked by severity)
- Area performance issues
- Staff performance gaps
- Complaint patterns

### 4. Actions
- Quick summary (3 KPIs)
- Prioritized recommendations
- WhatsApp export section
- PDF report generation
- Today's checklist

---

## Dependencies

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
holidays>=0.40
python-dotenv>=1.0.0
```

---

## Expected Data Schema

Required columns:
- `order_id` — Unique identifier
- `order_date` — Date of order
- `delivery_area` — Delivery zone (A, B, C, D, E)
- `delivery_duration` — Minutes from dispatch to arrival
- `dough_prep_time`, `styling_time`, `oven_time`, `boxing_time` — Stage durations
- `complaint` — Boolean (0/1)

Optional columns:
- `complaint_reason` — Category of complaint
- `driver_name`, `chef_name` — Staff assignments
- `order_mode` — app, whatsapp, phone
- `oven_temperature` — Oven temp in °C

---

## Computed Columns (auto-generated)

```python
total_prep_time = dough_prep_time + styling_time + oven_time + boxing_time
total_process_time = total_prep_time + delivery_duration
delivery_target_met = total_process_time <= delivery_target_minutes
hour_of_day = extract from order_time
is_peak_hour = lunch (11-14) or dinner (17-21)
```

---

## Deployment

### Streamlit Cloud
1. Push to GitHub
2. Connect to share.streamlit.io
3. Entry point: `Welcome.py`
4. No secrets required (all data uploaded by user)

### Important Notes
- All pages have `sys.path.insert()` for module imports
- Avoid singleton patterns (causes caching issues)
- Create fresh LocalAnalytics instances each call

---

## Color Palette

```python
COLORS = {
    "primary": "#3B82F6",      # Blue
    "secondary": "#8B5CF6",    # Purple
    "success": "#22C55E",      # Green
    "warning": "#F59E0B",      # Amber
    "danger": "#EF4444",       # Red
    "info": "#06B6D4",         # Cyan
    "bg_dark": "#0F172A",
    "text_primary": "#F8FAFC",
    "text_secondary": "#94A3B8",
    "text_muted": "#64748B",
}
```

---

## Value Proposition vs Power BI

| Feature | PizzaOps | Power BI |
|---------|----------|----------|
| Setup Time | 5 minutes | Days/weeks |
| Technical Skill | Zero | DAX, modeling |
| Cost | Low/Free | R2,500+/month |
| Load Shedding | Works offline | Needs internet |
| Domain Knowledge | Built-in | Build from scratch |
| Recommendations | Tells you what to DO | Just shows data |
| WhatsApp Export | One-click | Manual |

---

*Built with purpose by JLWanalytics. Turning operational chaos into intelligence.*
