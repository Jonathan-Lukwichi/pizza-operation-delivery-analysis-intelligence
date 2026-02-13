"""
Expected column schemas and validation rules for PizzaOps Intelligence.
Handles mapping from raw dataset columns to standardized names.
"""

from typing import Literal

# ── Column Mapping: Raw Dataset → Standardized Names ──
COLUMN_MAPPING = {
    "Pizza No.": "order_id",
    "Order Date": "order_date",
    "Order Time": "order_time",
    "Ord - Del time": "total_process_time",
    "Order Receipt (mins)": "order_receipt_time",
    " Base prep (mins)": "dough_prep_time",      # Note: leading space in raw data
    " Styling (mins)": "styling_time",            # Note: leading space in raw data
    " Cooking Time (mins)": "oven_time",          # Note: leading space in raw data
    "Boxing (mins)": "boxing_time",
    "Delivery (mins)": "delivery_duration",
    "Oven Temp °C": "oven_temperature",           # Handle encoding variations
    "Oven Temp �C": "oven_temperature",           # Handle encoding variations
    "Order Mode": "order_mode",
    "Size": "pizza_size",
    "Area": "delivery_area",
    "Order Taker": "order_taker",
    "Dough Prep": "dough_prep_staff",
    "Stylist": "stylist",
    "Oven": "oven_operator",
    "Boxer": "boxer",
    "Deliverer": "delivery_driver",
    "Cust. complaint": "complaint",
    "Reason": "complaint_reason",
}

# ── Expected Columns Schema ──
EXPECTED_COLUMNS = {
    # ── Order Identification ──
    "order_id": {
        "type": "str",
        "required": True,
        "desc": "Unique order identifier"
    },
    "order_date": {
        "type": "datetime",
        "required": True,
        "desc": "Date of order"
    },
    "order_time": {
        "type": "time",
        "required": True,
        "desc": "Time order was placed"
    },
    "order_mode": {
        "type": "category",
        "required": True,
        "desc": "app | phone | email",
        "valid_values": ["app", "phone", "email"]
    },

    # ── Staff Assignments ──
    "order_taker": {
        "type": "str",
        "required": False,
        "desc": "Name of order taker"
    },
    "dough_prep_staff": {
        "type": "str",
        "required": False,
        "desc": "Name of dough prep staff"
    },
    "stylist": {
        "type": "str",
        "required": False,
        "desc": "Name of pizza stylist"
    },
    "oven_operator": {
        "type": "str",
        "required": False,
        "desc": "Name of oven operator"
    },
    "boxer": {
        "type": "str",
        "required": False,
        "desc": "Name of boxer"
    },
    "delivery_driver": {
        "type": "str",
        "required": True,
        "desc": "Name of delivery driver"
    },

    # ── Stage Durations (minutes) ──
    "dough_prep_time": {
        "type": "float",
        "required": True,
        "desc": "Minutes for dough preparation"
    },
    "styling_time": {
        "type": "float",
        "required": True,
        "desc": "Minutes for styling/topping"
    },
    "oven_time": {
        "type": "float",
        "required": True,
        "desc": "Minutes in oven"
    },
    "boxing_time": {
        "type": "float",
        "required": True,
        "desc": "Minutes to box"
    },

    # ── Oven Data ──
    "oven_temperature": {
        "type": "float",
        "required": False,
        "desc": "Oven temp in °C"
    },

    # ── Delivery Data ──
    "delivery_area": {
        "type": "category",
        "required": True,
        "desc": "Delivery zone: A, B, C, D, E",
        "valid_values": ["A", "B", "C", "D", "E"]
    },
    "delivery_duration": {
        "type": "float",
        "required": True,
        "desc": "Minutes from dispatch to arrival"
    },

    # ── Complaint Data ──
    "complaint": {
        "type": "bool",
        "required": True,
        "desc": "Whether a complaint was filed"
    },
    "complaint_reason": {
        "type": "str",
        "required": False,
        "desc": "Category or text of complaint"
    },

    # ── Optional Columns ──
    "pizza_size": {
        "type": "category",
        "required": False,
        "desc": "Size of pizza ordered"
    },
    "total_process_time": {
        "type": "float",
        "required": False,
        "desc": "Total order to delivery time (pre-computed)"
    },
    "order_receipt_time": {
        "type": "float",
        "required": False,
        "desc": "Time to receive/enter order"
    },
}

# ── Computed Columns (added by transformer) ──
COMPUTED_COLUMNS = [
    "total_prep_time",        # dough_prep + styling + oven + boxing
    "total_process_time",     # total_prep + delivery (if not already present)
    "delivery_target_met",    # total_process_time <= 30
    "hour_of_day",            # extracted from order_time
    "day_of_week",            # extracted from order_date
    "is_peak_hour",           # hour in peak lunch or dinner range
    "is_weekend",             # Saturday or Sunday
    "oven_temp_zone",         # cold/optimal/hot based on temperature
    "oven_temp_deviation",    # abs difference from optimal
    "delay_category",         # on_time/at_risk/late/critical
    "pct_dough_prep",         # stage proportion
    "pct_styling",            # stage proportion
    "pct_oven",               # stage proportion
    "pct_boxing",             # stage proportion
]


def normalize_column_name(col: str) -> str:
    """Normalize a column name: strip whitespace, lowercase, replace spaces."""
    return col.strip().lower().replace(" ", "_").replace(".", "")


def get_standardized_name(raw_col: str) -> str:
    """Get standardized column name from raw column name."""
    # First try exact match
    if raw_col in COLUMN_MAPPING:
        return COLUMN_MAPPING[raw_col]

    # Try with stripped whitespace
    stripped = raw_col.strip()
    if stripped in COLUMN_MAPPING:
        return COLUMN_MAPPING[stripped]

    # Try matching stripped version of mapping keys
    for key, value in COLUMN_MAPPING.items():
        if key.strip() == stripped:
            return value

    # Try case-insensitive matching
    raw_lower = raw_col.lower().strip()
    for key, value in COLUMN_MAPPING.items():
        if key.lower().strip() == raw_lower:
            return value

    # Return normalized version as fallback
    return normalize_column_name(raw_col)
