"""
Intelligent Data Profiler
Automatically scans any dataset, identifies column types, detects issues,
and suggests appropriate cleaning actions.

Works with ANY dataset - fully adaptive, no hardcoded column names.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ColumnProfile:
    """Profile for a single column."""
    name: str
    dtype: str                    # Original pandas dtype
    inferred_type: str            # 'numeric', 'categorical', 'datetime', 'boolean', 'id', 'text'
    total_count: int
    unique_count: int
    missing_count: int
    missing_pct: float
    sample_values: List[Any]
    issues: List[Dict[str, Any]] = field(default_factory=list)
    suggested_actions: List[Dict[str, Any]] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)


class DataProfiler:
    """
    Intelligent data profiler that works with any dataset.
    Scans columns, infers types, detects issues, suggests cleaning actions.
    """

    def __init__(self):
        self.HIGH_CARDINALITY_THRESHOLD = 50  # If unique > 50, likely ID or high-cardinality
        self.CATEGORICAL_THRESHOLD = 20       # If unique <= 20, likely categorical
        self.MISSING_WARNING_PCT = 5          # Warn if missing > 5%
        self.MISSING_CRITICAL_PCT = 20        # Critical if missing > 20%

    def profile_dataset(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Profile entire dataset.

        Returns dict with:
        - total_rows: number of rows
        - total_columns: number of columns
        - columns: dict of ColumnProfile for each column
        - summary: overview statistics
        """
        profiles = {}
        for col in df.columns:
            profiles[col] = self.profile_column(df, col)

        return {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": profiles,
            "summary": self._generate_summary(profiles)
        }

    def profile_column(self, df: pd.DataFrame, col: str) -> ColumnProfile:
        """Profile a single column."""
        series = df[col]

        # Basic stats
        total = len(series)
        missing = series.isnull().sum()
        missing_pct = round(missing / total * 100, 1) if total > 0 else 0
        non_null = series.dropna()
        unique = non_null.nunique()

        # Infer type
        inferred_type = self._infer_type(series, unique, total)

        # Get type-specific stats
        stats = self._get_stats(series, inferred_type)

        # Detect issues
        issues = self._detect_issues(series, inferred_type, missing_pct, stats)

        # Suggest actions
        suggested_actions = self._suggest_actions(col, inferred_type, issues, stats)

        # Sample values (convert to native Python types for JSON serialization)
        sample_values = []
        if len(non_null) > 0:
            for v in non_null.head(5).tolist():
                if pd.isna(v):
                    sample_values.append(None)
                elif isinstance(v, (np.integer, np.floating)):
                    sample_values.append(float(v) if isinstance(v, np.floating) else int(v))
                else:
                    sample_values.append(v)

        return ColumnProfile(
            name=col,
            dtype=str(series.dtype),
            inferred_type=inferred_type,
            total_count=total,
            unique_count=unique,
            missing_count=int(missing),
            missing_pct=missing_pct,
            sample_values=sample_values,
            issues=issues,
            suggested_actions=suggested_actions,
            stats=stats
        )

    def _infer_type(self, series: pd.Series, unique: int, total: int) -> str:
        """Infer semantic type of column."""
        dtype = series.dtype
        name = str(series.name).lower() if series.name else ""

        # Check for ID columns by name pattern
        if 'id' in name or '_id' in name or name.endswith('id') or name == 'index':
            return 'id'

        # Check for datetime
        if pd.api.types.is_datetime64_any_dtype(series):
            return 'datetime'
        if 'date' in name or 'time' in name or 'timestamp' in name:
            # Try to parse as datetime
            try:
                non_null = series.dropna()
                if len(non_null) > 0:
                    pd.to_datetime(non_null.head(100))
                    return 'datetime'
            except:
                pass

        # Check for boolean
        if pd.api.types.is_bool_dtype(series):
            return 'boolean'
        non_null = series.dropna()
        if unique == 2 and len(non_null) > 0:
            vals = set(str(v).lower().strip() for v in non_null.unique())
            bool_patterns = {'yes', 'no', 'true', 'false', '1', '0', 'y', 'n', 'oui', 'non', 't', 'f'}
            if vals.issubset(bool_patterns):
                return 'boolean'

        # Check for numeric
        if pd.api.types.is_numeric_dtype(series):
            if total > 0 and (unique == total or unique > total * 0.9):
                return 'id'  # Likely an ID if all unique
            return 'numeric'

        # Check for categorical vs text
        if pd.api.types.is_object_dtype(series) or pd.api.types.is_categorical_dtype(series):
            if unique <= self.CATEGORICAL_THRESHOLD:
                return 'categorical'
            elif unique > self.HIGH_CARDINALITY_THRESHOLD:
                # Check if it's long text
                avg_len = non_null.astype(str).str.len().mean() if len(non_null) > 0 else 0
                if avg_len > 50:
                    return 'text'
                return 'categorical'  # High cardinality but short strings
            return 'categorical'

        return 'unknown'

    def _get_stats(self, series: pd.Series, inferred_type: str) -> Dict[str, Any]:
        """Get type-specific statistics."""
        non_null = series.dropna()
        stats = {}

        if inferred_type == 'numeric':
            if len(non_null) > 0:
                stats = {
                    "min": float(non_null.min()),
                    "max": float(non_null.max()),
                    "mean": round(float(non_null.mean()), 2),
                    "median": round(float(non_null.median()), 2),
                    "std": round(float(non_null.std()), 2) if len(non_null) > 1 else 0,
                }
                # Detect outliers using IQR
                q1, q3 = non_null.quantile([0.25, 0.75])
                iqr = q3 - q1
                lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
                outliers = ((non_null < lower) | (non_null > upper)).sum()
                stats["outliers_count"] = int(outliers)
                stats["outliers_pct"] = round(outliers / len(non_null) * 100, 1)
                stats["iqr_lower"] = round(float(lower), 2)
                stats["iqr_upper"] = round(float(upper), 2)

        elif inferred_type in ['categorical', 'boolean']:
            if len(non_null) > 0:
                value_counts = non_null.value_counts()
                # Convert to native Python types
                top_values = {}
                for k, v in value_counts.head(5).items():
                    top_values[str(k)] = int(v)
                stats = {
                    "top_values": top_values,
                    "cardinality": int(non_null.nunique()),
                }

        elif inferred_type == 'datetime':
            try:
                dates = pd.to_datetime(non_null)
                if len(dates) > 0:
                    stats = {
                        "min_date": str(dates.min()),
                        "max_date": str(dates.max()),
                        "date_range_days": int((dates.max() - dates.min()).days)
                    }
            except:
                stats = {}

        elif inferred_type == 'text':
            if len(non_null) > 0:
                lengths = non_null.astype(str).str.len()
                stats = {
                    "avg_length": round(float(lengths.mean()), 1),
                    "min_length": int(lengths.min()),
                    "max_length": int(lengths.max()),
                }

        return stats

    def _detect_issues(self, series: pd.Series, inferred_type: str,
                       missing_pct: float, stats: Dict) -> List[Dict]:
        """Detect data quality issues."""
        issues = []

        # Missing values
        if missing_pct > 0:
            severity = "critical" if missing_pct > self.MISSING_CRITICAL_PCT else (
                "warning" if missing_pct > self.MISSING_WARNING_PCT else "info"
            )
            issues.append({
                "type": "missing_values",
                "severity": severity,
                "description": f"{missing_pct}% missing values",
                "value": missing_pct
            })

        # Outliers for numeric
        if inferred_type == 'numeric' and stats.get("outliers_count", 0) > 0:
            outlier_pct = stats.get("outliers_pct", 0)
            severity = "warning" if outlier_pct > 5 else "info"
            issues.append({
                "type": "outliers",
                "severity": severity,
                "description": f"{stats['outliers_count']} outliers ({outlier_pct}%)",
                "value": stats['outliers_count']
            })

        # High cardinality for categorical
        if inferred_type == 'categorical' and stats.get("cardinality", 0) > self.CATEGORICAL_THRESHOLD:
            issues.append({
                "type": "high_cardinality",
                "severity": "info",
                "description": f"High cardinality: {stats['cardinality']} unique values",
                "value": stats['cardinality']
            })

        return issues

    def _suggest_actions(self, col: str, inferred_type: str,
                        issues: List[Dict], stats: Dict) -> List[Dict]:
        """Suggest cleaning actions based on column type and issues."""
        actions = []

        for issue in issues:
            if issue["type"] == "missing_values":
                if inferred_type == 'numeric':
                    actions.append({
                        "action": "fill_missing",
                        "method": "median",
                        "description": f"Fill missing with median ({stats.get('median', 'N/A')})",
                        "recommended": True
                    })
                    actions.append({
                        "action": "fill_missing",
                        "method": "mean",
                        "description": f"Fill missing with mean ({stats.get('mean', 'N/A')})",
                        "recommended": False
                    })
                elif inferred_type in ['categorical', 'text']:
                    top_values = stats.get('top_values', {})
                    top_val = list(top_values.keys())[0] if top_values else None
                    if top_val:
                        actions.append({
                            "action": "fill_missing",
                            "method": "mode",
                            "description": f"Fill with most common: '{top_val}'",
                            "recommended": True
                        })
                    actions.append({
                        "action": "fill_missing",
                        "method": "unknown",
                        "description": "Fill with 'Unknown'",
                        "recommended": False
                    })
                elif inferred_type == 'boolean':
                    actions.append({
                        "action": "fill_missing",
                        "method": "mode",
                        "description": "Fill with most common value",
                        "recommended": True
                    })

                # Always offer drop option
                actions.append({
                    "action": "drop_missing",
                    "method": "drop",
                    "description": "Drop rows with missing values",
                    "recommended": False
                })

            elif issue["type"] == "outliers":
                actions.append({
                    "action": "cap_outliers",
                    "method": "iqr",
                    "description": f"Cap outliers to IQR bounds ({stats.get('iqr_lower', 'N/A')} - {stats.get('iqr_upper', 'N/A')})",
                    "recommended": True
                })
                actions.append({
                    "action": "remove_outliers",
                    "method": "iqr",
                    "description": "Remove outlier rows",
                    "recommended": False
                })

        # Encoding suggestion for categorical columns (always available)
        if inferred_type == 'categorical':
            actions.append({
                "action": "encode",
                "method": "indicator",
                "description": "Create indicator variables (0/1) for analysis",
                "recommended": not any(i["type"] == "missing_values" for i in issues)
            })

        return actions

    def _generate_summary(self, profiles: Dict[str, ColumnProfile]) -> Dict[str, Any]:
        """Generate dataset-level summary."""
        total_issues = 0
        columns_with_issues = 0
        type_counts = {}

        for col_name, profile in profiles.items():
            # Count issues
            if profile.issues:
                columns_with_issues += 1
                total_issues += len(profile.issues)

            # Count types
            t = profile.inferred_type
            type_counts[t] = type_counts.get(t, 0) + 1

        return {
            "total_issues": total_issues,
            "columns_with_issues": columns_with_issues,
            "type_distribution": type_counts,
            "columns_clean": len(profiles) - columns_with_issues
        }

    def apply_action(self, df: pd.DataFrame, col: str, action: Dict) -> pd.DataFrame:
        """
        Apply a cleaning action to the dataframe.

        Args:
            df: DataFrame to clean
            col: Column name to apply action to
            action: Action dict with 'action' and 'method' keys

        Returns:
            Cleaned DataFrame (copy)
        """
        df = df.copy()
        action_type = action.get("action")
        method = action.get("method")

        if action_type == "fill_missing":
            if method == "median":
                df[col] = df[col].fillna(df[col].median())
            elif method == "mean":
                df[col] = df[col].fillna(df[col].mean())
            elif method == "mode":
                mode_val = df[col].mode()
                if len(mode_val) > 0:
                    df[col] = df[col].fillna(mode_val.iloc[0])
            elif method == "unknown":
                df[col] = df[col].fillna("Unknown")

        elif action_type == "drop_missing":
            df = df.dropna(subset=[col])

        elif action_type == "cap_outliers":
            if method == "iqr":
                q1, q3 = df[col].quantile([0.25, 0.75])
                iqr = q3 - q1
                lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
                df[col] = df[col].clip(lower=lower, upper=upper)

        elif action_type == "remove_outliers":
            if method == "iqr":
                q1, q3 = df[col].quantile([0.25, 0.75])
                iqr = q3 - q1
                lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
                df = df[(df[col] >= lower) & (df[col] <= upper)]

        elif action_type == "encode":
            if method == "indicator":
                # Create indicator columns for each unique value
                unique_vals = df[col].dropna().unique()
                for val in unique_vals:
                    clean_name = str(val).lower().replace(" ", "_").replace("-", "_")
                    new_col = f"is_{clean_name}"
                    df[new_col] = (df[col] == val).astype(int)

        return df


def get_data_profiler() -> DataProfiler:
    """Get DataProfiler instance."""
    return DataProfiler()
