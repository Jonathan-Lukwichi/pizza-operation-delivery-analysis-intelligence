"""
Data Enricher - Adds computed columns for PizzaOps Intelligence.

Creates derived features from raw data for enhanced analytics.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class EnrichmentAction:
    """Records an enrichment action taken on the data."""
    column: str
    description: str
    formula: str


@dataclass
class EnrichmentReport:
    """Summary of all enrichment actions performed."""
    columns_added: int = 0
    actions: List[EnrichmentAction] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "columns_added": self.columns_added,
            "actions": [
                {
                    "column": a.column,
                    "description": a.description,
                    "formula": a.formula,
                }
                for a in self.actions
            ],
        }


class DataEnricher:
    """
    Adds computed columns to pizza operations data.

    Creates time-based features, aggregates, and business metrics.
    """

    # Peak hour definitions
    LUNCH_START = 11
    LUNCH_END = 14
    DINNER_START = 17
    DINNER_END = 21

    def __init__(self, df: pd.DataFrame, config: Optional[Dict] = None):
        """
        Initialize enricher with dataframe.

        Args:
            df: pandas DataFrame to enrich
            config: Optional business configuration dict
        """
        self.df = df.copy()
        self.config = config or {}
        self.report = EnrichmentReport()

        # Get delivery target from config (default 30 minutes)
        self.delivery_target = self.config.get("delivery_target_minutes", 30)

    def _log_action(self, column: str, description: str, formula: str):
        """Log an enrichment action."""
        self.report.actions.append(EnrichmentAction(
            column=column,
            description=description,
            formula=formula
        ))
        self.report.columns_added += 1

    def _has_column(self, col: str) -> bool:
        """Check if column exists."""
        return col in self.df.columns

    def add_hour_of_day(self) -> 'DataEnricher':
        """
        Extract hour from order_time or order_date.

        Returns:
            self for chaining
        """
        if self._has_column("hour_of_day"):
            return self  # Already exists

        # Try order_time first
        if self._has_column("order_time"):
            try:
                # Handle time strings like "12:05:07"
                times = pd.to_datetime(self.df["order_time"], format='%H:%M:%S', errors='coerce')
                if times.isna().all():
                    # Try other formats
                    times = pd.to_datetime(self.df["order_time"], errors='coerce')
                self.df["hour_of_day"] = times.dt.hour
                self._log_action(
                    "hour_of_day",
                    "Hour extracted from order time",
                    "order_time.hour"
                )
                return self
            except Exception:
                pass

        # Fall back to order_date if it has time component
        if self._has_column("order_date"):
            try:
                dates = pd.to_datetime(self.df["order_date"], errors='coerce')
                if dates.dt.hour.max() > 0:  # Has time component
                    self.df["hour_of_day"] = dates.dt.hour
                    self._log_action(
                        "hour_of_day",
                        "Hour extracted from order date",
                        "order_date.hour"
                    )
            except Exception:
                pass

        return self

    def add_day_of_week(self) -> 'DataEnricher':
        """
        Extract day of week from order_date.

        Returns:
            self for chaining
        """
        if self._has_column("day_of_week"):
            return self

        if self._has_column("order_date"):
            try:
                dates = pd.to_datetime(self.df["order_date"], errors='coerce')
                self.df["day_of_week"] = dates.dt.day_name()
                self.df["day_of_week_num"] = dates.dt.dayofweek  # 0=Monday, 6=Sunday

                self._log_action(
                    "day_of_week",
                    "Day name extracted from order date",
                    "order_date.day_name()"
                )
            except Exception:
                pass

        return self

    def add_is_weekend(self) -> 'DataEnricher':
        """
        Flag weekend orders (Saturday, Sunday).

        Returns:
            self for chaining
        """
        if self._has_column("is_weekend"):
            return self

        if self._has_column("order_date"):
            try:
                dates = pd.to_datetime(self.df["order_date"], errors='coerce')
                self.df["is_weekend"] = (dates.dt.dayofweek >= 5).astype(int)

                self._log_action(
                    "is_weekend",
                    "Weekend flag (Sat/Sun = 1)",
                    "dayofweek >= 5"
                )
            except Exception:
                pass

        return self

    def add_month_year(self) -> 'DataEnricher':
        """
        Extract month and year from order_date.

        Returns:
            self for chaining
        """
        if self._has_column("order_date"):
            try:
                dates = pd.to_datetime(self.df["order_date"], errors='coerce')

                if not self._has_column("month"):
                    self.df["month"] = dates.dt.month
                    self.df["month_name"] = dates.dt.month_name()
                    self._log_action("month", "Month number from order date", "order_date.month")

                if not self._has_column("year"):
                    self.df["year"] = dates.dt.year
                    self._log_action("year", "Year from order date", "order_date.year")

            except Exception:
                pass

        return self

    def add_is_peak_hour(self) -> 'DataEnricher':
        """
        Flag peak hour orders (lunch and dinner).

        Returns:
            self for chaining
        """
        if self._has_column("is_peak_hour"):
            return self

        # Ensure we have hour_of_day
        if not self._has_column("hour_of_day"):
            self.add_hour_of_day()

        if self._has_column("hour_of_day"):
            hour = self.df["hour_of_day"]
            is_lunch = (hour >= self.LUNCH_START) & (hour <= self.LUNCH_END)
            is_dinner = (hour >= self.DINNER_START) & (hour <= self.DINNER_END)

            self.df["is_peak_hour"] = (is_lunch | is_dinner).astype(int)

            self._log_action(
                "is_peak_hour",
                f"Peak hours: Lunch ({self.LUNCH_START}-{self.LUNCH_END}), Dinner ({self.DINNER_START}-{self.DINNER_END})",
                "hour in [11-14, 17-21]"
            )

            # Also add time period label
            if not self._has_column("time_period"):
                def get_period(h):
                    if pd.isna(h):
                        return "Unknown"
                    h = int(h)
                    if self.LUNCH_START <= h <= self.LUNCH_END:
                        return "Lunch"
                    elif self.DINNER_START <= h <= self.DINNER_END:
                        return "Dinner"
                    elif h < self.LUNCH_START:
                        return "Morning"
                    elif self.LUNCH_END < h < self.DINNER_START:
                        return "Afternoon"
                    else:
                        return "Late Night"

                self.df["time_period"] = self.df["hour_of_day"].apply(get_period)
                self._log_action("time_period", "Time period label", "Morning/Lunch/Afternoon/Dinner/Late Night")

        return self

    def add_total_prep_time(self) -> 'DataEnricher':
        """
        Calculate total preparation time (sum of all prep stages).

        Returns:
            self for chaining
        """
        if self._has_column("total_prep_time"):
            return self

        prep_cols = ["dough_prep_time", "styling_time", "oven_time", "boxing_time"]
        available_cols = [c for c in prep_cols if self._has_column(c)]

        if available_cols:
            self.df["total_prep_time"] = self.df[available_cols].sum(axis=1)

            self._log_action(
                "total_prep_time",
                f"Sum of {len(available_cols)} prep stages",
                " + ".join(available_cols)
            )

        return self

    def add_total_process_time(self) -> 'DataEnricher':
        """
        Calculate total process time (prep + delivery).

        Returns:
            self for chaining
        """
        # If already exists, skip
        if self._has_column("total_process_time"):
            return self

        # Ensure we have total_prep_time
        if not self._has_column("total_prep_time"):
            self.add_total_prep_time()

        if self._has_column("total_prep_time") and self._has_column("delivery_duration"):
            self.df["total_process_time"] = (
                self.df["total_prep_time"] + self.df["delivery_duration"]
            )

            self._log_action(
                "total_process_time",
                "Total time from order to delivery",
                "total_prep_time + delivery_duration"
            )

        return self

    def add_delivery_target_met(self) -> 'DataEnricher':
        """
        Flag whether delivery target was met.

        Returns:
            self for chaining
        """
        if self._has_column("delivery_target_met"):
            return self

        # Ensure we have total_process_time
        if not self._has_column("total_process_time"):
            self.add_total_process_time()

        if self._has_column("total_process_time"):
            self.df["delivery_target_met"] = (
                self.df["total_process_time"] <= self.delivery_target
            ).astype(int)

            self._log_action(
                "delivery_target_met",
                f"On-time delivery (within {self.delivery_target} mins)",
                f"total_process_time <= {self.delivery_target}"
            )

            # Also add delay amount
            if not self._has_column("delay_amount"):
                self.df["delay_amount"] = (
                    self.df["total_process_time"] - self.delivery_target
                ).clip(lower=0)

                self._log_action(
                    "delay_amount",
                    "Minutes over target (0 if on-time)",
                    f"max(0, total_process_time - {self.delivery_target})"
                )

        return self

    def add_complaint_binary(self) -> 'DataEnricher':
        """
        Ensure complaint column is binary (0/1).

        Returns:
            self for chaining
        """
        if self._has_column("complaint"):
            # Check if already binary
            unique_vals = self.df["complaint"].dropna().unique()
            if set(unique_vals) <= {0, 1, 0.0, 1.0}:
                return self

            # Convert yes/no to 0/1
            def to_binary(val):
                if pd.isna(val):
                    return 0
                str_val = str(val).lower().strip()
                return 1 if str_val in {'yes', 'true', '1', 'y'} else 0

            self.df["complaint"] = self.df["complaint"].apply(to_binary)

            self._log_action(
                "complaint",
                "Converted to binary (0=No, 1=Yes)",
                "yes/no → 1/0"
            )

        return self

    def add_oven_temp_range(self) -> 'DataEnricher':
        """
        Categorize oven temperature into ranges.

        Returns:
            self for chaining
        """
        if self._has_column("oven_temp_range"):
            return self

        if self._has_column("oven_temperature"):
            def categorize_temp(temp):
                if pd.isna(temp):
                    return "Unknown"
                if temp < 250:
                    return "Low"
                elif temp < 280:
                    return "Medium"
                else:
                    return "High"

            self.df["oven_temp_range"] = self.df["oven_temperature"].apply(categorize_temp)

            self._log_action(
                "oven_temp_range",
                "Temperature category (Low/Medium/High)",
                "<250=Low, 250-280=Medium, >280=High"
            )

        return self

    def auto_enrich(self) -> 'DataEnricher':
        """
        Automatically add all relevant computed columns.

        Returns:
            self for chaining
        """
        # Time-based features
        self.add_hour_of_day()
        self.add_day_of_week()
        self.add_is_weekend()
        self.add_month_year()
        self.add_is_peak_hour()

        # Process time features
        self.add_total_prep_time()
        self.add_total_process_time()
        self.add_delivery_target_met()

        # Quality features
        self.add_complaint_binary()
        self.add_oven_temp_range()

        return self

    def get_result(self) -> Tuple[pd.DataFrame, EnrichmentReport]:
        """
        Get enriched dataframe and report.

        Returns:
            Tuple of (enriched_df, report)
        """
        return self.df, self.report


def auto_enrich_dataframe(df: pd.DataFrame, config: Optional[Dict] = None) -> Tuple[pd.DataFrame, Dict]:
    """
    Convenience function to auto-enrich a dataframe.

    Args:
        df: pandas DataFrame
        config: Optional business configuration

    Returns:
        Tuple of (enriched_df, report_dict)
    """
    enricher = DataEnricher(df, config)
    enriched_df, report = enricher.auto_enrich().get_result()
    return enriched_df, report.to_dict()
