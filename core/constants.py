"""
App-wide constants, thresholds, and configurations for PizzaOps Intelligence.
"""

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
    "poor_quality", "missing_items", "rude_driver",
    "wrong_size", "other"
]

# ── Order Modes ──
ORDER_MODES = ["app", "phone", "email"]

# ── Delivery Areas ──
DELIVERY_AREAS = ["A", "B", "C", "D", "E"]

# ── Peak Hours ──
PEAK_LUNCH = (11, 14)                 # 11:00 - 14:00
PEAK_DINNER = (17, 21)                # 17:00 - 21:00

# ── KPI Targets ──
KPI_TARGETS = {
    "on_time_pct": 85.0,              # % orders under 30 min
    "complaint_rate_pct": 5.0,         # % orders with complaints
    "avg_delivery_min": 25.0,          # Target average
    "avg_prep_min": 20.0,              # Total prep pipeline target
}

# ── Staff Roles ──
STAFF_ROLES = [
    "order_taker",
    "dough_prep_staff",
    "stylist",
    "oven_operator",
    "boxer",
    "delivery_driver"
]

# ── Pipeline Stages ──
PIPELINE_STAGES = ["dough_prep", "styling", "oven", "boxing", "delivery"]

# ── Delay Categories ──
DELAY_THRESHOLDS = {
    "on_time": 25,      # ≤ 25 min
    "at_risk": 30,      # 25-30 min
    "late": 40,         # 30-40 min
    "critical": 999,    # > 40 min
}

# ── Chart Color Palette ──
STAGE_COLORS = {
    "dough_prep": "#8B5CF6",   # Violet
    "styling": "#06B6D4",       # Cyan
    "oven": "#F59E0B",          # Amber
    "boxing": "#10B981",        # Green
    "delivery": "#EC4899",      # Pink
}

# ── Status Colors ──
STATUS_COLORS = {
    "good": "#10B981",          # Green
    "warning": "#F59E0B",       # Amber
    "danger": "#EF4444",        # Red
    "neutral": "#94A3B8",       # Gray
}
