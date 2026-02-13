"""
Data Ingestion Agent
====================

Intelligent data loading, validation, and anomaly detection.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import json
import logging

import pandas as pd
import numpy as np

from .base import BaseAgent, AgentResponse, AgentTool, AgentStatus

logger = logging.getLogger(__name__)


@dataclass
class DataQualityReport:
    """Report on data quality."""
    total_rows: int
    valid_rows: int
    missing_values: Dict[str, int]
    duplicates: int
    anomalies: List[Dict]
    quality_score: float  # 0-100
    recommendations: List[str]


@dataclass
class ColumnMapping:
    """Mapping from raw to standardized column names."""
    raw_name: str
    standard_name: str
    confidence: float
    method: str  # "exact", "fuzzy", "llm"


class DataIngestionAgent(BaseAgent):
    """
    Autonomous data ingestion with intelligent validation.

    Features:
    - Auto-detect file formats and schemas
    - Intelligent column mapping (pattern + LLM-powered)
    - Real-time anomaly detection
    - Data quality scoring
    - Self-healing (auto-fix common data issues)
    """

    # Standard schema expected
    STANDARD_SCHEMA = {
        "order_id": {"type": "string", "required": True},
        "order_date": {"type": "datetime", "required": True},
        "order_time": {"type": "time", "required": False},
        "order_mode": {"type": "category", "values": ["app", "phone", "email", "walk-in"]},
        "delivery_area": {"type": "category", "values": ["A", "B", "C", "D", "E"]},
        "dough_prep_time": {"type": "float", "unit": "minutes"},
        "styling_time": {"type": "float", "unit": "minutes"},
        "oven_time": {"type": "float", "unit": "minutes"},
        "boxing_time": {"type": "float", "unit": "minutes"},
        "delivery_duration": {"type": "float", "unit": "minutes"},
        "oven_temperature": {"type": "float", "unit": "celsius"},
        "complaint": {"type": "boolean"},
        "complaint_reason": {"type": "string"},
        "delivery_driver": {"type": "string"},
        "stylist": {"type": "string"},
    }

    # Column name variations for fuzzy matching
    COLUMN_VARIATIONS = {
        "order_id": ["orderid", "order_number", "order #", "id"],
        "order_date": ["date", "orderdate", "order_dt", "transaction_date"],
        "delivery_area": ["area", "zone", "delivery_zone", "sector"],
        "dough_prep_time": ["dough_time", "prep_time", "dough_preparation"],
        "styling_time": ["style_time", "topping_time", "decoration_time"],
        "oven_time": ["baking_time", "cook_time", "bake_time"],
        "boxing_time": ["box_time", "packaging_time", "pack_time"],
        "delivery_duration": ["delivery_time", "transit_time", "delivery_mins"],
        "oven_temperature": ["oven_temp", "temperature", "temp"],
        "complaint": ["complained", "has_complaint", "is_complaint"],
        "delivery_driver": ["driver", "driver_name", "courier"],
    }

    def __init__(self, llm_client: Any = None):
        super().__init__(
            name="data",
            description="intelligent data ingestion, validation, and anomaly detection",
            llm_client=llm_client,
        )

        self._dataframe: Optional[pd.DataFrame] = None
        self._quality_report: Optional[DataQualityReport] = None

    def _register_default_tools(self) -> None:
        """Register data agent tools."""

        self.register_tool(AgentTool(
            name="load_data",
            description="Load data from a file (CSV or Excel)",
            function=self.load_data,
            parameters={
                "file_path": {"type": "string", "description": "Path to the data file"},
            },
            required_params=["file_path"],
        ))

        self.register_tool(AgentTool(
            name="validate_schema",
            description="Validate data against expected schema",
            function=self.validate_schema,
            parameters={},
        ))

        self.register_tool(AgentTool(
            name="detect_anomalies",
            description="Detect anomalies in the data",
            function=self.detect_anomalies,
            parameters={
                "sensitivity": {"type": "number", "description": "Anomaly sensitivity (0-1)"},
            },
        ))

        self.register_tool(AgentTool(
            name="get_summary",
            description="Get summary statistics of the data",
            function=self.get_summary,
            parameters={},
        ))

        self.register_tool(AgentTool(
            name="fix_data_issues",
            description="Automatically fix common data issues",
            function=self.fix_data_issues,
            parameters={
                "issues": {"type": "array", "description": "List of issues to fix"},
            },
        ))

        self.register_tool(AgentTool(
            name="map_columns",
            description="Map raw column names to standard schema",
            function=self.map_columns,
            parameters={
                "raw_columns": {"type": "array", "description": "List of raw column names"},
            },
            required_params=["raw_columns"],
        ))

    async def load_data(self, file_path: str) -> Dict[str, Any]:
        """Load data from file with intelligent format detection."""
        try:
            # Detect file type
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                # Try CSV as default
                df = pd.read_csv(file_path)

            self._dataframe = df

            # Auto-map columns
            mappings = await self.map_columns(list(df.columns))

            # Apply mappings
            column_map = {m.raw_name: m.standard_name for m in mappings if m.confidence > 0.7}
            df = df.rename(columns=column_map)
            self._dataframe = df

            # Initial quality check
            self._quality_report = await self._calculate_quality_report()

            return {
                "success": True,
                "rows": len(df),
                "columns": list(df.columns),
                "mapped_columns": len(column_map),
                "quality_score": self._quality_report.quality_score,
            }

        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return {"success": False, "error": str(e)}

    async def map_columns(self, raw_columns: List[str]) -> List[ColumnMapping]:
        """Intelligently map raw column names to standard schema."""
        mappings = []

        for raw_col in raw_columns:
            raw_lower = raw_col.lower().strip().replace(" ", "_")

            # Try exact match
            if raw_lower in self.STANDARD_SCHEMA:
                mappings.append(ColumnMapping(
                    raw_name=raw_col,
                    standard_name=raw_lower,
                    confidence=1.0,
                    method="exact",
                ))
                continue

            # Try fuzzy match
            matched = False
            for standard_name, variations in self.COLUMN_VARIATIONS.items():
                if raw_lower in [v.lower().replace(" ", "_") for v in variations]:
                    mappings.append(ColumnMapping(
                        raw_name=raw_col,
                        standard_name=standard_name,
                        confidence=0.9,
                        method="fuzzy",
                    ))
                    matched = True
                    break

            # If no match, try LLM
            if not matched and self.llm_client:
                llm_mapping = await self._llm_map_column(raw_col)
                if llm_mapping:
                    mappings.append(llm_mapping)
                else:
                    mappings.append(ColumnMapping(
                        raw_name=raw_col,
                        standard_name=raw_col,  # Keep original
                        confidence=0.0,
                        method="none",
                    ))
            elif not matched:
                mappings.append(ColumnMapping(
                    raw_name=raw_col,
                    standard_name=raw_col,
                    confidence=0.0,
                    method="none",
                ))

        return mappings

    async def _llm_map_column(self, raw_column: str) -> Optional[ColumnMapping]:
        """Use LLM to map ambiguous column names."""
        if not self.llm_client:
            return None

        prompt = f"""
        Map this column name to our standard schema.

        Raw column: "{raw_column}"

        Standard schema columns:
        {json.dumps(list(self.STANDARD_SCHEMA.keys()), indent=2)}

        If it matches one of the standard columns, return that name.
        If it doesn't match any, return "unknown".

        Return only the standard column name, nothing else.
        """

        # response = await self.call_llm([{"role": "user", "content": prompt}])
        # standard_name = response["content"].strip()
        #
        # if standard_name in self.STANDARD_SCHEMA:
        #     return ColumnMapping(
        #         raw_name=raw_column,
        #         standard_name=standard_name,
        #         confidence=0.8,
        #         method="llm",
        #     )

        return None

    async def validate_schema(self) -> Dict[str, Any]:
        """Validate data against expected schema."""
        if self._dataframe is None:
            return {"success": False, "error": "No data loaded"}

        df = self._dataframe
        issues = []

        # Check required columns
        for col, spec in self.STANDARD_SCHEMA.items():
            if spec.get("required", False) and col not in df.columns:
                issues.append({
                    "type": "missing_column",
                    "column": col,
                    "severity": "high",
                })

        # Check data types
        for col in df.columns:
            if col in self.STANDARD_SCHEMA:
                expected_type = self.STANDARD_SCHEMA[col]["type"]

                if expected_type == "datetime":
                    try:
                        pd.to_datetime(df[col])
                    except:
                        issues.append({
                            "type": "type_mismatch",
                            "column": col,
                            "expected": "datetime",
                            "severity": "medium",
                        })

                elif expected_type == "float":
                    if not pd.api.types.is_numeric_dtype(df[col]):
                        issues.append({
                            "type": "type_mismatch",
                            "column": col,
                            "expected": "numeric",
                            "severity": "medium",
                        })

                elif expected_type == "category":
                    expected_values = self.STANDARD_SCHEMA[col].get("values", [])
                    if expected_values:
                        invalid = set(df[col].dropna().unique()) - set(expected_values)
                        if invalid:
                            issues.append({
                                "type": "invalid_values",
                                "column": col,
                                "invalid": list(invalid),
                                "severity": "low",
                            })

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "columns_validated": len(df.columns),
        }

    async def detect_anomalies(self, sensitivity: float = 0.95) -> List[Dict]:
        """Detect anomalies in numerical columns."""
        if self._dataframe is None:
            return []

        df = self._dataframe
        anomalies = []

        # Numeric columns for anomaly detection
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            data = df[col].dropna()
            if len(data) < 10:
                continue

            # Statistical anomaly detection (IQR method)
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]

            if len(outliers) > 0:
                anomalies.append({
                    "column": col,
                    "type": "outlier",
                    "count": len(outliers),
                    "lower_bound": float(lower_bound),
                    "upper_bound": float(upper_bound),
                    "severity": "high" if len(outliers) > len(df) * 0.05 else "medium",
                    "sample_values": outliers[col].head(5).tolist(),
                })

            # Detect sudden spikes (if datetime indexed)
            if "order_date" in df.columns:
                daily = df.groupby("order_date")[col].mean()
                daily_pct_change = daily.pct_change().abs()
                spikes = daily_pct_change[daily_pct_change > 0.5]

                if len(spikes) > 0:
                    anomalies.append({
                        "column": col,
                        "type": "spike",
                        "dates": spikes.index.tolist()[:5],
                        "changes": spikes.values.tolist()[:5],
                        "severity": "medium",
                    })

        return anomalies

    async def _calculate_quality_report(self) -> DataQualityReport:
        """Calculate comprehensive data quality report."""
        df = self._dataframe

        # Missing values
        missing = df.isnull().sum().to_dict()
        missing = {k: int(v) for k, v in missing.items() if v > 0}

        # Duplicates
        duplicates = int(df.duplicated().sum())

        # Anomalies
        anomalies = await self.detect_anomalies()

        # Quality score calculation
        total_cells = df.shape[0] * df.shape[1]
        missing_cells = sum(missing.values())
        missing_pct = missing_cells / total_cells if total_cells > 0 else 0
        duplicate_pct = duplicates / len(df) if len(df) > 0 else 0
        anomaly_pct = len(anomalies) / len(df.columns) if len(df.columns) > 0 else 0

        quality_score = max(0, 100 - (missing_pct * 30) - (duplicate_pct * 20) - (anomaly_pct * 20))

        # Recommendations
        recommendations = []
        if missing_pct > 0.05:
            recommendations.append(f"High missing value rate ({missing_pct:.1%}). Consider imputation.")
        if duplicate_pct > 0.01:
            recommendations.append(f"Found {duplicates} duplicate rows. Consider deduplication.")
        if len(anomalies) > 0:
            recommendations.append(f"Detected {len(anomalies)} anomaly types. Review outliers.")

        return DataQualityReport(
            total_rows=len(df),
            valid_rows=len(df) - duplicates,
            missing_values=missing,
            duplicates=duplicates,
            anomalies=anomalies,
            quality_score=quality_score,
            recommendations=recommendations,
        )

    async def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive data summary."""
        if self._dataframe is None:
            return {"error": "No data loaded"}

        df = self._dataframe

        summary = {
            "shape": {"rows": len(df), "columns": len(df.columns)},
            "columns": list(df.columns),
            "dtypes": df.dtypes.astype(str).to_dict(),
        }

        # Date range
        if "order_date" in df.columns:
            dates = pd.to_datetime(df["order_date"], errors="coerce")
            summary["date_range"] = {
                "min": str(dates.min()),
                "max": str(dates.max()),
                "days": (dates.max() - dates.min()).days if not pd.isna(dates.min()) else 0,
            }

        # Categorical summaries
        if "delivery_area" in df.columns:
            summary["areas"] = df["delivery_area"].value_counts().to_dict()

        if "order_mode" in df.columns:
            summary["order_modes"] = df["order_mode"].value_counts().to_dict()

        # Numeric summaries
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        summary["numeric_stats"] = df[numeric_cols].describe().to_dict()

        # Quality
        if self._quality_report:
            summary["quality"] = {
                "score": self._quality_report.quality_score,
                "missing_columns": list(self._quality_report.missing_values.keys()),
                "duplicates": self._quality_report.duplicates,
                "recommendations": self._quality_report.recommendations,
            }

        return summary

    async def fix_data_issues(self, issues: Optional[List[str]] = None) -> Dict[str, Any]:
        """Automatically fix common data issues."""
        if self._dataframe is None:
            return {"error": "No data loaded"}

        df = self._dataframe.copy()
        fixes_applied = []

        # Fix 1: Remove duplicates
        if issues is None or "duplicates" in issues:
            before = len(df)
            df = df.drop_duplicates()
            removed = before - len(df)
            if removed > 0:
                fixes_applied.append(f"Removed {removed} duplicate rows")

        # Fix 2: Convert date columns
        if issues is None or "dates" in issues:
            if "order_date" in df.columns:
                df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
                fixes_applied.append("Converted order_date to datetime")

        # Fix 3: Standardize categorical values
        if issues is None or "categories" in issues:
            if "delivery_area" in df.columns:
                df["delivery_area"] = df["delivery_area"].str.upper().str.strip()
                fixes_applied.append("Standardized delivery_area values")

            if "complaint" in df.columns:
                df["complaint"] = df["complaint"].apply(
                    lambda x: True if str(x).lower() in ["yes", "true", "1", "y"] else False
                )
                fixes_applied.append("Standardized complaint to boolean")

        # Fix 4: Handle missing values in numeric columns
        if issues is None or "missing" in issues:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                missing_count = df[col].isna().sum()
                if 0 < missing_count < len(df) * 0.1:  # Less than 10% missing
                    median_val = df[col].median()
                    df[col] = df[col].fillna(median_val)
                    fixes_applied.append(f"Filled {missing_count} missing values in {col} with median")

        self._dataframe = df
        self._quality_report = await self._calculate_quality_report()

        return {
            "fixes_applied": fixes_applied,
            "new_quality_score": self._quality_report.quality_score,
        }

    async def process(self, request: str, context: Optional[Dict] = None) -> AgentResponse:
        """Process a data-related request."""
        self.update_status(AgentStatus.THINKING)

        request_lower = request.lower()

        try:
            # Route to appropriate tool based on request
            if "load" in request_lower or "file" in request_lower:
                # Need file path from context
                file_path = context.get("file_path") if context else None
                if file_path:
                    result = await self.load_data(file_path)
                else:
                    result = {"error": "No file path provided"}

            elif "summary" in request_lower or "overview" in request_lower:
                result = await self.get_summary()

            elif "quality" in request_lower or "validate" in request_lower:
                result = await self.validate_schema()

            elif "anomal" in request_lower or "outlier" in request_lower:
                result = await self.detect_anomalies()

            elif "fix" in request_lower or "clean" in request_lower:
                result = await self.fix_data_issues()

            else:
                # Default: return summary
                result = await self.get_summary()

            self.update_status(AgentStatus.COMPLETED)

            return AgentResponse(
                content=json.dumps(result, indent=2, default=str),
                success=True,
                data=result,
                agent_name=self.name,
            )

        except Exception as e:
            self.update_status(AgentStatus.ERROR)
            logger.error(f"Data agent error: {e}")

            return AgentResponse(
                content=f"Error processing request: {str(e)}",
                success=False,
                error=str(e),
                agent_name=self.name,
            )

    @property
    def dataframe(self) -> Optional[pd.DataFrame]:
        """Get the current dataframe."""
        return self._dataframe

    @dataframe.setter
    def dataframe(self, df: pd.DataFrame) -> None:
        """Set the dataframe directly."""
        self._dataframe = df
