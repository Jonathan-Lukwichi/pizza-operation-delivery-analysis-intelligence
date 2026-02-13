"""
Data Quality Agent
==================

AI agent that acts as a Data Quality Analyst.
Examines datasets, identifies quality issues, and suggests cleaning actions.
"""

import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import pandas as pd
import numpy as np

from .base_agent import BaseAgent, AgentResponse, QualityIssue


SYSTEM_PROMPT = """You are a Senior Data Quality Analyst with 15 years of experience in business analytics.
You are examining a pizza delivery operations dataset to ensure data quality before analysis.

Your expertise includes:
- Identifying missing values and their impact
- Detecting duplicate records
- Finding outliers using statistical methods (IQR, z-score)
- Validating data types and ranges
- Assessing data completeness and consistency

Your task:
1. Analyze the data quality thoroughly
2. Identify ALL issues (missing values, duplicates, outliers, type errors)
3. Score the data quality from 0-100
4. Recommend specific cleaning actions
5. Explain the impact of each issue on analysis

Be specific with numbers. Reference actual column names.
Format your response as structured JSON for programmatic parsing.

Expected JSON format:
{
    "quality_score": 85,
    "summary": "Brief 1-2 sentence assessment",
    "issues": [
        {
            "type": "missing|duplicate|outlier|type_error|invalid",
            "column": "column_name",
            "severity": "low|medium|high|critical",
            "count": 123,
            "percentage": 5.2,
            "description": "What the issue is",
            "impact": "How it affects analysis",
            "suggested_fix": "Recommended action",
            "auto_fixable": true
        }
    ],
    "recommendations": [
        {
            "priority": 1,
            "action": "What to do",
            "reason": "Why"
        }
    ],
    "ready_for_analysis": true
}
"""


@dataclass
class QualityReport:
    """Comprehensive data quality report."""
    quality_score: float
    summary: str
    issues: List[QualityIssue]
    recommendations: List[Dict[str, str]]
    ready_for_analysis: bool
    stats: Dict[str, any] = field(default_factory=dict)


class DataQualityAgent(BaseAgent):
    """
    Data Quality Analyst Agent.

    Examines datasets after upload to:
    - Check data quality (missing, duplicates, outliers)
    - Generate a quality score (0-100)
    - Suggest and apply cleaning actions
    - Validate data readiness for analysis
    """

    def __init__(self):
        super().__init__(
            name="Data Quality Analyst",
            system_prompt=SYSTEM_PROMPT
        )

    def _compute_basic_stats(self, df: pd.DataFrame) -> Dict:
        """Compute basic statistics for quality assessment."""
        stats = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
        }

        # Missing values
        missing = df.isnull().sum()
        stats["missing_by_column"] = {col: int(count) for col, count in missing.items() if count > 0}
        stats["total_missing"] = int(missing.sum())
        stats["missing_pct"] = (missing.sum() / (len(df) * len(df.columns))) * 100

        # Duplicates
        stats["duplicate_rows"] = int(df.duplicated().sum())
        stats["duplicate_pct"] = (stats["duplicate_rows"] / len(df)) * 100 if len(df) > 0 else 0

        # Numeric columns for outlier detection
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        stats["numeric_columns"] = numeric_cols

        # Outliers (IQR method)
        outliers = {}
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            outlier_count = int(((df[col] < lower) | (df[col] > upper)).sum())
            if outlier_count > 0:
                outliers[col] = {
                    "count": outlier_count,
                    "percentage": (outlier_count / len(df)) * 100,
                    "lower_bound": float(lower),
                    "upper_bound": float(upper),
                    "min": float(df[col].min()),
                    "max": float(df[col].max())
                }
        stats["outliers"] = outliers

        # Data types
        stats["column_types"] = {col: str(dtype) for col, dtype in df.dtypes.items()}

        return stats

    def _compute_quality_score(self, stats: Dict) -> float:
        """Compute a quality score from 0-100."""
        score = 100.0

        # Penalize for missing values (up to -30 points)
        missing_pct = stats.get("missing_pct", 0)
        if missing_pct > 0:
            score -= min(30, missing_pct * 2)

        # Penalize for duplicates (up to -20 points)
        dup_pct = stats.get("duplicate_pct", 0)
        if dup_pct > 0:
            score -= min(20, dup_pct * 4)

        # Penalize for outliers (up to -15 points)
        outlier_cols = len(stats.get("outliers", {}))
        if outlier_cols > 0:
            score -= min(15, outlier_cols * 3)

        return max(0, min(100, score))

    def _identify_issues_locally(self, df: pd.DataFrame, stats: Dict) -> List[QualityIssue]:
        """Identify quality issues without AI (fast local analysis)."""
        issues = []

        # Missing values
        for col, count in stats.get("missing_by_column", {}).items():
            pct = (count / len(df)) * 100
            severity = "low" if pct < 5 else ("medium" if pct < 15 else ("high" if pct < 30 else "critical"))

            # Determine if auto-fixable based on column type
            dtype = str(df[col].dtype)
            if "float" in dtype or "int" in dtype:
                suggested_fix = f"Fill with median value ({df[col].median():.2f})"
                auto_fixable = True
            elif col == "complaint_reason":
                suggested_fix = "Keep as-is (null = no complaint)"
                auto_fixable = False
            else:
                suggested_fix = f"Fill with mode value or 'Unknown'"
                auto_fixable = True

            issues.append(QualityIssue(
                type="missing",
                column=col,
                severity=severity,
                count=count,
                description=f"{count} missing values ({pct:.1f}%)",
                suggested_fix=suggested_fix,
                auto_fixable=auto_fixable
            ))

        # Duplicates
        dup_count = stats.get("duplicate_rows", 0)
        if dup_count > 0:
            pct = (dup_count / len(df)) * 100
            severity = "low" if pct < 1 else ("medium" if pct < 5 else "high")
            issues.append(QualityIssue(
                type="duplicate",
                column="[all]",
                severity=severity,
                count=dup_count,
                description=f"{dup_count} duplicate rows ({pct:.1f}%)",
                suggested_fix="Remove duplicate rows, keeping first occurrence",
                auto_fixable=True
            ))

        # Outliers
        for col, outlier_info in stats.get("outliers", {}).items():
            count = outlier_info["count"]
            pct = outlier_info["percentage"]
            severity = "low" if pct < 2 else ("medium" if pct < 5 else "high")

            # Time columns have different handling
            if "time" in col.lower() or "duration" in col.lower():
                upper = outlier_info["upper_bound"]
                suggested_fix = f"Cap at {upper:.0f} minutes (P95 threshold)"
            else:
                suggested_fix = f"Review and cap at bounds ({outlier_info['lower_bound']:.2f} - {outlier_info['upper_bound']:.2f})"

            issues.append(QualityIssue(
                type="outlier",
                column=col,
                severity=severity,
                count=count,
                description=f"{count} outliers ({pct:.1f}%) - values outside [{outlier_info['lower_bound']:.1f}, {outlier_info['upper_bound']:.1f}]",
                suggested_fix=suggested_fix,
                auto_fixable=True
            ))

        return issues

    def analyze(self, df: pd.DataFrame) -> AgentResponse:
        """
        Analyze data quality and return a comprehensive report.

        Args:
            df: The dataframe to analyze

        Returns:
            AgentResponse with quality analysis results
        """
        if not self.is_available():
            # Fallback to local analysis only
            return self._analyze_locally(df)

        try:
            # Compute local stats first
            stats = self._compute_basic_stats(df)
            local_score = self._compute_quality_score(stats)
            local_issues = self._identify_issues_locally(df, stats)

            # Build prompt for Claude
            data_summary = self._build_data_summary(df)

            prompt = f"""Analyze this pizza delivery dataset for data quality issues.

{data_summary}

Pre-computed Statistics:
{json.dumps(stats, indent=2, default=str)}

Local Analysis Found:
- Quality Score (computed): {local_score:.0f}/100
- Issues identified: {len(local_issues)}

Please provide your expert assessment as a Data Quality Analyst.
Review my preliminary findings, add any issues I missed, and provide recommendations.

IMPORTANT: Return your response as valid JSON matching the expected format.
"""

            # Call Claude for expert analysis
            response_text, cost = self._call_claude(prompt, max_tokens=2000)

            # Try to parse JSON response
            parsed = self._parse_json_from_response(response_text)

            if parsed:
                # Use AI-enhanced analysis
                ai_score = parsed.get("quality_score", local_score)
                ai_summary = parsed.get("summary", f"Data quality score: {ai_score}/100")
                ai_ready = parsed.get("ready_for_analysis", ai_score >= 70)

                # Merge AI issues with local issues
                ai_issues = parsed.get("issues", [])
                ai_recommendations = parsed.get("recommendations", [])

                return AgentResponse(
                    success=True,
                    content=ai_summary,
                    data={
                        "quality_score": ai_score,
                        "stats": stats,
                        "raw_response": response_text,
                        "ready_for_analysis": ai_ready
                    },
                    issues=[{
                        "type": issue.get("type", "unknown"),
                        "column": issue.get("column", "unknown"),
                        "severity": issue.get("severity", "medium"),
                        "count": issue.get("count", 0),
                        "description": issue.get("description", ""),
                        "suggested_fix": issue.get("suggested_fix", ""),
                        "auto_fixable": issue.get("auto_fixable", False)
                    } for issue in ai_issues] if ai_issues else [
                        {
                            "type": issue.type,
                            "column": issue.column,
                            "severity": issue.severity,
                            "count": issue.count,
                            "description": issue.description,
                            "suggested_fix": issue.suggested_fix,
                            "auto_fixable": issue.auto_fixable
                        } for issue in local_issues
                    ],
                    recommendations=[{
                        "priority": str(rec.get("priority", "medium")),
                        "action": rec.get("action", ""),
                        "reason": rec.get("reason", "")
                    } for rec in ai_recommendations],
                    score=ai_score,
                    cost=cost
                )
            else:
                # AI response wasn't JSON, use local analysis with AI commentary
                return AgentResponse(
                    success=True,
                    content=response_text,  # Use AI's free-form response
                    data={
                        "quality_score": local_score,
                        "stats": stats,
                        "ready_for_analysis": local_score >= 70
                    },
                    issues=[{
                        "type": issue.type,
                        "column": issue.column,
                        "severity": issue.severity,
                        "count": issue.count,
                        "description": issue.description,
                        "suggested_fix": issue.suggested_fix,
                        "auto_fixable": issue.auto_fixable
                    } for issue in local_issues],
                    score=local_score,
                    cost=cost
                )

        except Exception as e:
            # Fallback to local-only analysis
            return self._analyze_locally(df, error=str(e))

    def _analyze_locally(self, df: pd.DataFrame, error: str = None) -> AgentResponse:
        """Perform local analysis without AI (fallback)."""
        stats = self._compute_basic_stats(df)
        score = self._compute_quality_score(stats)
        issues = self._identify_issues_locally(df, stats)

        summary = f"Data quality score: {score:.0f}/100. "
        if issues:
            summary += f"Found {len(issues)} issues requiring attention."
        else:
            summary += "No major issues detected."

        if error:
            summary += f" (AI enhancement unavailable: {error})"

        return AgentResponse(
            success=True,
            content=summary,
            data={
                "quality_score": score,
                "stats": stats,
                "ready_for_analysis": score >= 70,
                "ai_enhanced": False
            },
            issues=[{
                "type": issue.type,
                "column": issue.column,
                "severity": issue.severity,
                "count": issue.count,
                "description": issue.description,
                "suggested_fix": issue.suggested_fix,
                "auto_fixable": issue.auto_fixable
            } for issue in issues],
            score=score,
            cost=0.0
        )

    def apply_fixes(self, df: pd.DataFrame, fixes: List[Dict]) -> Tuple[pd.DataFrame, List[str]]:
        """
        Apply selected fixes to the dataframe.

        Args:
            df: Original dataframe
            fixes: List of fixes to apply (from issues with auto_fixable=True)

        Returns:
            Tuple of (cleaned_dataframe, list_of_actions_taken)
        """
        df_clean = df.copy()
        actions = []

        for fix in fixes:
            fix_type = fix.get("type")
            column = fix.get("column")

            try:
                if fix_type == "duplicate":
                    original_len = len(df_clean)
                    df_clean = df_clean.drop_duplicates(keep='first')
                    removed = original_len - len(df_clean)
                    actions.append(f"Removed {removed} duplicate rows")

                elif fix_type == "missing" and column and column != "[all]":
                    if column in df_clean.columns:
                        dtype = str(df_clean[column].dtype)
                        if "float" in dtype or "int" in dtype:
                            median_val = df_clean[column].median()
                            count = df_clean[column].isnull().sum()
                            df_clean[column] = df_clean[column].fillna(median_val)
                            actions.append(f"Filled {count} missing values in '{column}' with median ({median_val:.2f})")
                        else:
                            mode_val = df_clean[column].mode()[0] if len(df_clean[column].mode()) > 0 else "Unknown"
                            count = df_clean[column].isnull().sum()
                            df_clean[column] = df_clean[column].fillna(mode_val)
                            actions.append(f"Filled {count} missing values in '{column}' with mode ('{mode_val}')")

                elif fix_type == "outlier" and column:
                    if column in df_clean.columns:
                        Q1 = df_clean[column].quantile(0.25)
                        Q3 = df_clean[column].quantile(0.75)
                        IQR = Q3 - Q1
                        lower = Q1 - 1.5 * IQR
                        upper = Q3 + 1.5 * IQR

                        count_low = (df_clean[column] < lower).sum()
                        count_high = (df_clean[column] > upper).sum()

                        df_clean[column] = df_clean[column].clip(lower=lower, upper=upper)
                        actions.append(f"Capped {count_low + count_high} outliers in '{column}' to [{lower:.1f}, {upper:.1f}]")

            except Exception as e:
                actions.append(f"Failed to apply fix for {column}: {str(e)}")

        return df_clean, actions


# Singleton instance
_data_quality_agent: Optional[DataQualityAgent] = None


def get_data_quality_agent() -> DataQualityAgent:
    """Get the singleton Data Quality Agent instance."""
    global _data_quality_agent
    if _data_quality_agent is None:
        _data_quality_agent = DataQualityAgent()
    return _data_quality_agent
