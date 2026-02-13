"""
Business Configuration System
==============================

Central configuration for generic pizza business analytics.
Replaces hardcoded values with configurable settings.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json
import streamlit as st


@dataclass
class StageConfig:
    """Configuration for a production stage."""
    id: str                    # e.g., "dough_prep"
    name: str                  # Display name e.g., "Dough Preparation"
    column_name: str           # Column in data e.g., "dough_prep_time"
    target_minutes: float      # Target time
    p95_max_minutes: float     # P95 threshold
    color: str = "#8B5CF6"     # Hex color for charts


@dataclass
class BusinessConfig:
    """
    Central business configuration.

    Provides sensible pizza defaults but allows customization.
    """
    # Branding
    business_name: str = "Pizza Business"
    business_icon: str = "pizza"
    tagline: str = "Operations Analytics"

    # Delivery Targets
    delivery_target_minutes: int = 30
    delivery_warning_minutes: int = 25
    delivery_critical_minutes: int = 40

    # KPI Thresholds
    on_time_target_pct: float = 85.0
    complaint_target_pct: float = 5.0
    avg_delivery_target_min: float = 25.0

    # Peak Hours
    peak_lunch_start: int = 11
    peak_lunch_end: int = 14
    peak_dinner_start: int = 17
    peak_dinner_end: int = 21

    # AI Budget (ZAR)
    daily_budget_zar: float = 50.0

    # Pipeline Stages (default pizza stages)
    stages: List[StageConfig] = field(default_factory=lambda: [
        StageConfig("dough_prep", "Dough Prep", "dough_prep_time", 5.0, 8.0, "#8B5CF6"),
        StageConfig("styling", "Styling", "styling_time", 3.0, 6.0, "#06B6D4"),
        StageConfig("oven", "Oven", "oven_time", 10.0, 14.0, "#F59E0B"),
        StageConfig("boxing", "Boxing", "boxing_time", 2.0, 4.0, "#10B981"),
        StageConfig("delivery", "Delivery", "delivery_duration", 10.0, 15.0, "#EC4899"),
    ])

    # Delivery Areas (None = auto-detect from data)
    delivery_areas: Optional[List[str]] = None

    # Staff Roles (None = auto-detect from data)
    staff_roles: Optional[List[str]] = None

    def get_stage_benchmarks(self) -> Dict[str, float]:
        """Get stage benchmarks as dict."""
        return {s.column_name: s.target_minutes for s in self.stages}

    def get_stage_by_column(self, column_name: str) -> Optional[StageConfig]:
        """Get stage config by column name."""
        for stage in self.stages:
            if stage.column_name == column_name:
                return stage
        return None

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "business_name": self.business_name,
            "business_icon": self.business_icon,
            "tagline": self.tagline,
            "delivery_target_minutes": self.delivery_target_minutes,
            "delivery_warning_minutes": self.delivery_warning_minutes,
            "delivery_critical_minutes": self.delivery_critical_minutes,
            "on_time_target_pct": self.on_time_target_pct,
            "complaint_target_pct": self.complaint_target_pct,
            "avg_delivery_target_min": self.avg_delivery_target_min,
            "peak_lunch_start": self.peak_lunch_start,
            "peak_lunch_end": self.peak_lunch_end,
            "peak_dinner_start": self.peak_dinner_start,
            "peak_dinner_end": self.peak_dinner_end,
            "daily_budget_zar": self.daily_budget_zar,
            "stages": [
                {
                    "id": s.id,
                    "name": s.name,
                    "column_name": s.column_name,
                    "target_minutes": s.target_minutes,
                    "p95_max_minutes": s.p95_max_minutes,
                    "color": s.color
                }
                for s in self.stages
            ],
            "delivery_areas": self.delivery_areas,
            "staff_roles": self.staff_roles,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BusinessConfig":
        """Create from dictionary."""
        stages = [
            StageConfig(
                id=s["id"],
                name=s["name"],
                column_name=s["column_name"],
                target_minutes=s["target_minutes"],
                p95_max_minutes=s["p95_max_minutes"],
                color=s.get("color", "#8B5CF6")
            )
            for s in data.get("stages", [])
        ]

        return cls(
            business_name=data.get("business_name", "Pizza Business"),
            business_icon=data.get("business_icon", "pizza"),
            tagline=data.get("tagline", "Operations Analytics"),
            delivery_target_minutes=data.get("delivery_target_minutes", 30),
            delivery_warning_minutes=data.get("delivery_warning_minutes", 25),
            delivery_critical_minutes=data.get("delivery_critical_minutes", 40),
            on_time_target_pct=data.get("on_time_target_pct", 85.0),
            complaint_target_pct=data.get("complaint_target_pct", 5.0),
            avg_delivery_target_min=data.get("avg_delivery_target_min", 25.0),
            peak_lunch_start=data.get("peak_lunch_start", 11),
            peak_lunch_end=data.get("peak_lunch_end", 14),
            peak_dinner_start=data.get("peak_dinner_start", 17),
            peak_dinner_end=data.get("peak_dinner_end", 21),
            daily_budget_zar=data.get("daily_budget_zar", 50.0),
            stages=stages if stages else None,
            delivery_areas=data.get("delivery_areas"),
            staff_roles=data.get("staff_roles"),
        )


def get_config() -> BusinessConfig:
    """
    Get the current business configuration.

    Loads from session state or creates default.
    """
    if "business_config" not in st.session_state:
        st.session_state.business_config = BusinessConfig()
    return st.session_state.business_config


def save_config(config: BusinessConfig):
    """Save configuration to session state."""
    st.session_state.business_config = config


def export_config_json(config: BusinessConfig) -> str:
    """Export configuration as JSON string."""
    return json.dumps(config.to_dict(), indent=2)


def import_config_json(json_str: str) -> BusinessConfig:
    """Import configuration from JSON string."""
    data = json.loads(json_str)
    return BusinessConfig.from_dict(data)


# Mode helpers
def is_pro_mode() -> bool:
    """Check if app is in Pro mode (AI enabled)."""
    return st.session_state.get("app_mode", "lite") == "pro"


def is_lite_mode() -> bool:
    """Check if app is in Lite mode (offline only)."""
    return not is_pro_mode()


def set_mode(mode: str):
    """Set app mode ('lite' or 'pro')."""
    st.session_state.app_mode = mode


def get_mode() -> str:
    """Get current app mode."""
    return st.session_state.get("app_mode", "lite")
