"""
Data Cleaner - Automated data cleaning for PizzaOps Intelligence.

Handles missing values, outliers, type conversion, and value standardization.
All cleaning operations are logged for transparency.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field


@dataclass
class CleaningAction:
    """Records a cleaning action taken on the data."""
    column: str
    action_type: str  # 'fill_missing', 'cap_outlier', 'convert_type', 'standardize'
    description: str
    rows_affected: int
    before_value: Optional[Any] = None
    after_value: Optional[Any] = None


@dataclass
class CleaningReport:
    """Summary of all cleaning actions performed."""
    total_rows: int
    total_columns: int
    actions: List[CleaningAction] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def total_actions(self) -> int:
        return len(self.actions)

    @property
    def rows_cleaned(self) -> int:
        return sum(a.rows_affected for a in self.actions)

    def to_dict(self) -> Dict:
        return {
            "total_rows": self.total_rows,
            "total_columns": self.total_columns,
            "total_actions": self.total_actions,
            "rows_cleaned": self.rows_cleaned,
            "actions": [
                {
                    "column": a.column,
                    "action": a.action_type,
                    "description": a.description,
                    "rows_affected": a.rows_affected,
                }
                for a in self.actions
            ],
            "warnings": self.warnings,
        }


class DataCleaner:
    """
    Automated data cleaner for pizza operations data.

    Applies intelligent cleaning rules based on column types and data patterns.
    """

    # Standard boolean values mapping
    BOOL_TRUE = {'yes', 'true', '1', 'y', 't', 'on', 'active'}
    BOOL_FALSE = {'no', 'false', '0', 'n', 'f', 'off', 'inactive', 'none', ''}

    def __init__(self, df: pd.DataFrame):
        """
        Initialize cleaner with dataframe.

        Args:
            df: pandas DataFrame to clean
        """
        self.df = df.copy()
        self.report = CleaningReport(
            total_rows=len(df),
            total_columns=len(df.columns)
        )

    def _log_action(self, column: str, action_type: str, description: str,
                    rows_affected: int, before: Any = None, after: Any = None):
        """Log a cleaning action."""
        self.report.actions.append(CleaningAction(
            column=column,
            action_type=action_type,
            description=description,
            rows_affected=rows_affected,
            before_value=before,
            after_value=after
        ))

    def _is_numeric_column(self, col: str) -> bool:
        """Check if column is numeric."""
        return pd.api.types.is_numeric_dtype(self.df[col])

    def _is_datetime_column(self, col: str) -> bool:
        """Check if column is datetime."""
        return pd.api.types.is_datetime64_any_dtype(self.df[col])

    def _detect_column_type(self, col: str) -> str:
        """Detect the semantic type of a column."""
        if self._is_datetime_column(col):
            return "datetime"
        if self._is_numeric_column(col):
            return "numeric"

        # Check for boolean-like values
        unique_vals = set(str(v).lower().strip() for v in self.df[col].dropna().unique())
        if unique_vals <= (self.BOOL_TRUE | self.BOOL_FALSE):
            return "boolean"

        # Check cardinality for categorical
        nunique = self.df[col].nunique()
        if nunique <= 50 or nunique / len(self.df) < 0.05:
            return "categorical"

        return "text"

    def fill_missing_numeric(self, col: str, strategy: str = "median") -> 'DataCleaner':
        """
        Fill missing values in numeric column.

        Args:
            col: Column name
            strategy: 'median', 'mean', 'zero', or a specific value

        Returns:
            self for chaining
        """
        if col not in self.df.columns:
            return self

        missing_count = self.df[col].isna().sum()
        if missing_count == 0:
            return self

        if strategy == "median":
            fill_value = self.df[col].median()
        elif strategy == "mean":
            fill_value = self.df[col].mean()
        elif strategy == "zero":
            fill_value = 0
        else:
            fill_value = float(strategy)

        self.df[col] = self.df[col].fillna(fill_value)

        self._log_action(
            column=col,
            action_type="fill_missing",
            description=f"Filled {missing_count} missing values with {strategy} ({fill_value:.2f})",
            rows_affected=missing_count,
            before="NaN",
            after=fill_value
        )

        return self

    def fill_missing_categorical(self, col: str, strategy: str = "mode") -> 'DataCleaner':
        """
        Fill missing values in categorical column.

        Args:
            col: Column name
            strategy: 'mode', 'unknown', or a specific value

        Returns:
            self for chaining
        """
        if col not in self.df.columns:
            return self

        missing_count = self.df[col].isna().sum()
        if missing_count == 0:
            return self

        if strategy == "mode":
            mode_vals = self.df[col].mode()
            fill_value = mode_vals.iloc[0] if len(mode_vals) > 0 else "Unknown"
        elif strategy == "unknown":
            fill_value = "Unknown"
        else:
            fill_value = strategy

        self.df[col] = self.df[col].fillna(fill_value)

        self._log_action(
            column=col,
            action_type="fill_missing",
            description=f"Filled {missing_count} missing values with '{fill_value}'",
            rows_affected=missing_count,
            before="NaN",
            after=fill_value
        )

        return self

    def cap_outliers_iqr(self, col: str, multiplier: float = 1.5) -> 'DataCleaner':
        """
        Cap outliers using IQR method.

        Args:
            col: Column name
            multiplier: IQR multiplier (default 1.5)

        Returns:
            self for chaining
        """
        if col not in self.df.columns or not self._is_numeric_column(col):
            return self

        Q1 = self.df[col].quantile(0.25)
        Q3 = self.df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR

        # Count outliers
        outliers_low = (self.df[col] < lower_bound).sum()
        outliers_high = (self.df[col] > upper_bound).sum()
        total_outliers = outliers_low + outliers_high

        if total_outliers == 0:
            return self

        # Cap values
        self.df[col] = self.df[col].clip(lower=lower_bound, upper=upper_bound)

        self._log_action(
            column=col,
            action_type="cap_outlier",
            description=f"Capped {total_outliers} outliers to [{lower_bound:.2f}, {upper_bound:.2f}]",
            rows_affected=total_outliers,
            before=f"{outliers_low} low, {outliers_high} high",
            after=f"[{lower_bound:.2f}, {upper_bound:.2f}]"
        )

        return self

    def standardize_boolean(self, col: str, true_value: int = 1, false_value: int = 0) -> 'DataCleaner':
        """
        Standardize boolean column to numeric values.

        Args:
            col: Column name
            true_value: Value for True (default 1)
            false_value: Value for False (default 0)

        Returns:
            self for chaining
        """
        if col not in self.df.columns:
            return self

        def convert_bool(val):
            if pd.isna(val):
                return false_value
            str_val = str(val).lower().strip()
            if str_val in self.BOOL_TRUE:
                return true_value
            return false_value

        original_dtype = self.df[col].dtype
        rows_affected = len(self.df)

        self.df[col] = self.df[col].apply(convert_bool)

        self._log_action(
            column=col,
            action_type="standardize",
            description=f"Converted boolean values to {false_value}/{true_value}",
            rows_affected=rows_affected,
            before=str(original_dtype),
            after="int"
        )

        return self

    def convert_to_datetime(self, col: str, dayfirst: bool = False) -> 'DataCleaner':
        """
        Convert column to datetime.

        Args:
            col: Column name
            dayfirst: Whether day comes first in date format

        Returns:
            self for chaining
        """
        if col not in self.df.columns:
            return self

        if self._is_datetime_column(col):
            return self  # Already datetime

        try:
            original_dtype = self.df[col].dtype
            self.df[col] = pd.to_datetime(self.df[col], dayfirst=dayfirst, errors='coerce')
            converted = self.df[col].notna().sum()

            self._log_action(
                column=col,
                action_type="convert_type",
                description=f"Converted to datetime ({converted} valid dates)",
                rows_affected=converted,
                before=str(original_dtype),
                after="datetime64"
            )
        except Exception as e:
            self.report.warnings.append(f"Could not convert {col} to datetime: {str(e)}")

        return self

    def convert_to_numeric(self, col: str) -> 'DataCleaner':
        """
        Convert column to numeric.

        Args:
            col: Column name

        Returns:
            self for chaining
        """
        if col not in self.df.columns:
            return self

        if self._is_numeric_column(col):
            return self  # Already numeric

        try:
            original_dtype = self.df[col].dtype
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
            converted = self.df[col].notna().sum()

            self._log_action(
                column=col,
                action_type="convert_type",
                description=f"Converted to numeric ({converted} valid numbers)",
                rows_affected=converted,
                before=str(original_dtype),
                after="float64"
            )
        except Exception as e:
            self.report.warnings.append(f"Could not convert {col} to numeric: {str(e)}")

        return self

    def standardize_text(self, col: str, case: str = "title") -> 'DataCleaner':
        """
        Standardize text column (trim, case).

        Args:
            col: Column name
            case: 'title', 'upper', 'lower', or 'none'

        Returns:
            self for chaining
        """
        if col not in self.df.columns:
            return self

        if self._is_numeric_column(col) or self._is_datetime_column(col):
            return self

        def clean_text(val):
            if pd.isna(val):
                return val
            text = str(val).strip()
            if case == "title":
                return text.title()
            elif case == "upper":
                return text.upper()
            elif case == "lower":
                return text.lower()
            return text

        self.df[col] = self.df[col].apply(clean_text)

        self._log_action(
            column=col,
            action_type="standardize",
            description=f"Standardized text ({case} case, trimmed)",
            rows_affected=len(self.df),
        )

        return self

    def auto_clean(self) -> 'DataCleaner':
        """
        Automatically clean all columns based on detected types.

        Returns:
            self for chaining
        """
        for col in self.df.columns:
            col_type = self._detect_column_type(col)
            missing_count = self.df[col].isna().sum()

            if col_type == "numeric":
                # Fill missing with median
                if missing_count > 0:
                    self.fill_missing_numeric(col, "median")
                # Cap outliers
                self.cap_outliers_iqr(col)

            elif col_type == "categorical":
                # Fill missing with mode
                if missing_count > 0:
                    self.fill_missing_categorical(col, "mode")
                # Standardize text
                self.standardize_text(col, "title")

            elif col_type == "boolean":
                # Standardize to 0/1
                self.standardize_boolean(col)

            elif col_type == "datetime":
                # Nothing special needed
                pass

            elif col_type == "text":
                # Fill missing with "Unknown"
                if missing_count > 0:
                    self.fill_missing_categorical(col, "unknown")

        return self

    def get_result(self) -> Tuple[pd.DataFrame, CleaningReport]:
        """
        Get cleaned dataframe and report.

        Returns:
            Tuple of (cleaned_df, report)
        """
        return self.df, self.report


def auto_clean_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """
    Convenience function to auto-clean a dataframe.

    Args:
        df: pandas DataFrame

    Returns:
        Tuple of (cleaned_df, report_dict)
    """
    cleaner = DataCleaner(df)
    cleaned_df, report = cleaner.auto_clean().get_result()
    return cleaned_df, report.to_dict()
