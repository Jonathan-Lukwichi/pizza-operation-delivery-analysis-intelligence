"""
Data Pipeline - One-click data preparation for PizzaOps Intelligence.

Orchestrates schema mapping, cleaning, and enrichment in a single flow.
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
import time

from .schema_mapper import SchemaMapper, auto_map_columns
from .data_cleaner import DataCleaner, auto_clean_dataframe
from .data_enricher import DataEnricher, auto_enrich_dataframe


@dataclass
class PipelineStep:
    """Represents a step in the pipeline."""
    name: str
    status: str = "pending"  # pending, running, completed, failed
    message: str = ""
    duration_ms: int = 0
    details: Dict = field(default_factory=dict)


@dataclass
class PipelineResult:
    """Result of running the complete pipeline."""
    success: bool
    df: Optional[pd.DataFrame]
    steps: List[PipelineStep]
    quality_score: float = 0.0
    total_duration_ms: int = 0
    summary: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "quality_score": self.quality_score,
            "total_duration_ms": self.total_duration_ms,
            "steps": [
                {
                    "name": s.name,
                    "status": s.status,
                    "message": s.message,
                    "duration_ms": s.duration_ms,
                    "details": s.details,
                }
                for s in self.steps
            ],
            "summary": self.summary,
        }


class DataPipeline:
    """
    Complete data preparation pipeline for PizzaOps Intelligence.

    Stages:
    1. Schema Detection & Mapping
    2. Column Renaming
    3. Data Cleaning
    4. Data Enrichment
    5. Quality Validation
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize pipeline.

        Args:
            config: Business configuration dict with delivery_target_minutes, etc.
        """
        self.config = config or {}
        self.steps: List[PipelineStep] = []
        self.callbacks: List[Callable[[PipelineStep], None]] = []

    def add_callback(self, callback: Callable[[PipelineStep], None]):
        """Add a callback to be called after each step completes."""
        self.callbacks.append(callback)

    def _notify_callbacks(self, step: PipelineStep):
        """Notify all callbacks of step completion."""
        for callback in self.callbacks:
            try:
                callback(step)
            except Exception:
                pass  # Don't let callback errors break the pipeline

    def _run_step(self, name: str, func: Callable, *args, **kwargs) -> Tuple[any, PipelineStep]:
        """
        Run a pipeline step with timing and error handling.

        Args:
            name: Step name
            func: Function to run
            *args, **kwargs: Arguments for the function

        Returns:
            Tuple of (result, step)
        """
        step = PipelineStep(name=name, status="running")
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            step.status = "completed"
            step.duration_ms = int((time.time() - start_time) * 1000)
            return result, step
        except Exception as e:
            step.status = "failed"
            step.message = str(e)
            step.duration_ms = int((time.time() - start_time) * 1000)
            return None, step

    def run(self, df: pd.DataFrame, progress_callback: Optional[Callable] = None) -> PipelineResult:
        """
        Run the complete data preparation pipeline.

        Args:
            df: Raw input DataFrame
            progress_callback: Optional callback called with (step_num, total_steps, step_name)

        Returns:
            PipelineResult with cleaned/enriched DataFrame and reports
        """
        self.steps = []
        start_time = time.time()
        current_df = df.copy()
        total_steps = 5

        def update_progress(step_num: int, step_name: str):
            if progress_callback:
                progress_callback(step_num, total_steps, step_name)

        # =====================================================================
        # STEP 1: Schema Detection & Mapping
        # =====================================================================
        update_progress(1, "Detecting schema...")

        mapper = SchemaMapper()
        mapping_result, step1 = self._run_step(
            "Schema Detection",
            mapper.get_mapping_report,
            list(current_df.columns)
        )

        if step1.status == "completed" and mapping_result:
            step1.message = f"Mapped {mapping_result['mapped_columns']}/{mapping_result['total_columns']} columns"
            step1.details = {
                "mapped": mapping_result["mapped_columns"],
                "total": mapping_result["total_columns"],
                "rate": f"{mapping_result['mapping_rate']*100:.0f}%",
                "mappings": mapping_result["mappings"][:10],  # First 10 for display
            }
        self.steps.append(step1)
        self._notify_callbacks(step1)

        if step1.status == "failed":
            return PipelineResult(
                success=False,
                df=None,
                steps=self.steps,
                total_duration_ms=int((time.time() - start_time) * 1000),
            )

        # =====================================================================
        # STEP 2: Column Renaming
        # =====================================================================
        update_progress(2, "Standardizing columns...")

        rename_dict = mapper.get_rename_dict(list(current_df.columns))

        def do_rename(df, renames):
            return df.rename(columns=renames)

        current_df, step2 = self._run_step(
            "Column Standardization",
            do_rename,
            current_df,
            rename_dict
        )

        if step2.status == "completed":
            step2.message = f"Renamed {len(rename_dict)} columns to standard names"
            step2.details = {
                "renames": list(rename_dict.items())[:10],
            }
        self.steps.append(step2)
        self._notify_callbacks(step2)

        if step2.status == "failed" or current_df is None:
            return PipelineResult(
                success=False,
                df=None,
                steps=self.steps,
                total_duration_ms=int((time.time() - start_time) * 1000),
            )

        # =====================================================================
        # STEP 3: Data Cleaning
        # =====================================================================
        update_progress(3, "Cleaning data...")

        cleaner = DataCleaner(current_df)
        _, step3 = self._run_step(
            "Data Cleaning",
            cleaner.auto_clean
        )

        if step3.status == "completed":
            current_df, cleaning_report = cleaner.get_result()
            step3.message = f"Applied {cleaning_report.total_actions} cleaning actions"
            step3.details = {
                "actions": cleaning_report.total_actions,
                "rows_cleaned": cleaning_report.rows_cleaned,
                "action_list": [
                    {"col": a.column, "action": a.action_type, "desc": a.description}
                    for a in cleaning_report.actions[:10]
                ],
            }
        self.steps.append(step3)
        self._notify_callbacks(step3)

        if step3.status == "failed":
            return PipelineResult(
                success=False,
                df=None,
                steps=self.steps,
                total_duration_ms=int((time.time() - start_time) * 1000),
            )

        # =====================================================================
        # STEP 4: Data Enrichment
        # =====================================================================
        update_progress(4, "Enriching data...")

        enricher = DataEnricher(current_df, self.config)
        _, step4 = self._run_step(
            "Data Enrichment",
            enricher.auto_enrich
        )

        if step4.status == "completed":
            current_df, enrichment_report = enricher.get_result()
            step4.message = f"Added {enrichment_report.columns_added} computed columns"
            step4.details = {
                "columns_added": enrichment_report.columns_added,
                "new_columns": [a.column for a in enrichment_report.actions],
            }
        self.steps.append(step4)
        self._notify_callbacks(step4)

        if step4.status == "failed":
            return PipelineResult(
                success=False,
                df=None,
                steps=self.steps,
                total_duration_ms=int((time.time() - start_time) * 1000),
            )

        # =====================================================================
        # STEP 5: Quality Validation
        # =====================================================================
        update_progress(5, "Validating quality...")

        def validate_quality(df):
            """Calculate data quality score (0-100)."""
            scores = []

            # 1. Completeness (no missing values)
            missing_rate = df.isnull().sum().sum() / (df.shape[0] * df.shape[1])
            completeness = (1 - missing_rate) * 100
            scores.append(completeness)

            # 2. Required columns present
            required = ["order_id", "order_date"]
            present = sum(1 for c in required if c in df.columns)
            column_score = (present / len(required)) * 100 if required else 100
            scores.append(column_score)

            # 3. Has enough rows
            row_score = min(100, (len(df) / 100) * 100)  # 100 rows = 100%
            scores.append(row_score)

            # 4. Key analytics columns present
            analytics_cols = [
                "delivery_duration", "total_process_time", "delivery_target_met",
                "delivery_area", "complaint", "hour_of_day"
            ]
            analytics_present = sum(1 for c in analytics_cols if c in df.columns)
            analytics_score = (analytics_present / len(analytics_cols)) * 100
            scores.append(analytics_score)

            overall_score = sum(scores) / len(scores)

            return {
                "overall_score": round(overall_score, 1),
                "completeness": round(completeness, 1),
                "required_columns": round(column_score, 1),
                "row_count": len(df),
                "analytics_readiness": round(analytics_score, 1),
            }

        quality_result, step5 = self._run_step(
            "Quality Validation",
            validate_quality,
            current_df
        )

        if step5.status == "completed" and quality_result:
            step5.message = f"Quality score: {quality_result['overall_score']}%"
            step5.details = quality_result
        self.steps.append(step5)
        self._notify_callbacks(step5)

        # =====================================================================
        # Build Final Result
        # =====================================================================
        total_duration = int((time.time() - start_time) * 1000)

        # Build summary
        summary = {
            "original_rows": len(df),
            "original_columns": len(df.columns),
            "final_rows": len(current_df),
            "final_columns": len(current_df.columns),
            "columns_mapped": mapping_result.get("mapped_columns", 0) if mapping_result else 0,
            "cleaning_actions": cleaning_report.total_actions if 'cleaning_report' in dir() else 0,
            "columns_added": enrichment_report.columns_added if 'enrichment_report' in dir() else 0,
            "quality_score": quality_result.get("overall_score", 0) if quality_result else 0,
            "timestamp": datetime.now().isoformat(),
        }

        return PipelineResult(
            success=all(s.status == "completed" for s in self.steps),
            df=current_df,
            steps=self.steps,
            quality_score=quality_result.get("overall_score", 0) if quality_result else 0,
            total_duration_ms=total_duration,
            summary=summary,
        )


def prepare_data(df: pd.DataFrame, config: Optional[Dict] = None,
                 progress_callback: Optional[Callable] = None) -> PipelineResult:
    """
    One-click data preparation function.

    Args:
        df: Raw input DataFrame
        config: Optional business configuration
        progress_callback: Optional callback for progress updates

    Returns:
        PipelineResult with prepared DataFrame
    """
    pipeline = DataPipeline(config)
    return pipeline.run(df, progress_callback)


def quick_prepare(df: pd.DataFrame, config: Optional[Dict] = None) -> Tuple[pd.DataFrame, Dict]:
    """
    Quick data preparation without detailed reports.

    Args:
        df: Raw input DataFrame
        config: Optional business configuration

    Returns:
        Tuple of (prepared_df, summary_dict)
    """
    result = prepare_data(df, config)
    return result.df, result.summary
