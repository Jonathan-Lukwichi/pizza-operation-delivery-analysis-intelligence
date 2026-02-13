"""
Business Analyst Agent
======================

AI agent that acts as a Senior Business Analyst Consultant.
Analyzes operations, finds bottlenecks, and provides data-backed recommendations.
"""

import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import pandas as pd
import numpy as np

from .base_agent import BaseAgent, AgentResponse, Bottleneck, Recommendation


SYSTEM_PROMPT = """You are a Senior Business Analyst Consultant with 20 years of experience optimizing food delivery operations.
You have been hired to analyze this pizza delivery business and provide actionable recommendations.

Your analysis framework:

1. PERFORMANCE ASSESSMENT
   Compare key metrics against industry targets:
   - On-time delivery rate: Target 85%
   - Complaint rate: Target <5%
   - Average delivery time: Target 30 minutes

2. BOTTLENECK IDENTIFICATION
   Identify where operations are constrained:
   - By process stage (prep, styling, oven, boxing, delivery)
   - By delivery area (A, B, C, D, E)
   - By time of day (peak hours vs off-peak)
   - By staff member performance

3. ROOT CAUSE ANALYSIS
   Explain WHY problems exist, not just what they are:
   - Don't just say "Area D is slow" - explain why
   - Connect symptoms to underlying operational issues
   - Consider capacity, training, routing, and process factors

4. RECOMMENDATIONS
   Provide prioritized, actionable improvements:
   - PRIORITY 1 (HIGH): High impact, can implement today
   - PRIORITY 2 (MEDIUM): High impact, needs planning
   - PRIORITY 3 (QUICK WIN): Easy to implement, moderate impact

For every recommendation:
- Specify the exact action to take
- Quantify the expected impact
- Cite the data evidence supporting it
- Estimate the effort level (low/medium/high)

Be specific. Use actual numbers from the data.
Every insight must be backed by data evidence.

Return your analysis as structured JSON:
{
    "performance_summary": {
        "on_time_rate": {"value": 72.3, "target": 85, "status": "below"},
        "complaint_rate": {"value": 7.3, "target": 5, "status": "above"},
        "avg_delivery_time": {"value": 32.1, "target": 30, "status": "above"},
        "overall_assessment": "Brief 2-3 sentence assessment"
    },
    "bottlenecks": [
        {
            "rank": 1,
            "area": "oven_stage|delivery_area_D|peak_hours|etc",
            "severity": "critical|high|medium|low",
            "metric": "metric name",
            "current_value": 12.5,
            "benchmark_value": 10,
            "impact": "Causes X% of delays",
            "root_cause": "Specific explanation why this happens"
        }
    ],
    "recommendations": [
        {
            "priority": "high|medium|quick_win",
            "title": "Short title",
            "action": "Specific action to take",
            "expected_impact": "Quantified improvement",
            "effort": "low|medium|high",
            "evidence": "Data point supporting this",
            "timeline": "today|this_week|this_month"
        }
    ],
    "key_insights": [
        "Important observation 1",
        "Important observation 2"
    ]
}
"""


@dataclass
class PerformanceMetric:
    """A performance metric with target comparison."""
    name: str
    value: float
    target: float
    status: str  # below, above, on_target
    gap: float
    gap_pct: float


@dataclass
class OperationsReport:
    """Comprehensive operations analysis report."""
    performance_metrics: List[PerformanceMetric]
    bottlenecks: List[Bottleneck]
    recommendations: List[Recommendation]
    key_insights: List[str]
    overall_assessment: str


class BusinessAnalystAgent(BaseAgent):
    """
    Business Analyst Consultant Agent.

    Analyzes operations to:
    - Assess performance against targets
    - Identify bottlenecks and root causes
    - Generate prioritized recommendations
    - Provide data-backed improvement plans
    """

    # Benchmarks for pizza delivery operations
    BENCHMARKS = {
        "on_time_rate": 85.0,  # percentage
        "complaint_rate": 5.0,  # percentage (target is below)
        "avg_delivery_time": 30.0,  # minutes
        "dough_prep_time": 5.0,  # minutes
        "styling_time": 3.0,  # minutes
        "oven_time": 10.0,  # minutes
        "boxing_time": 2.0,  # minutes
        "delivery_duration": 10.0,  # minutes
    }

    def __init__(self):
        super().__init__(
            name="Business Analyst Consultant",
            system_prompt=SYSTEM_PROMPT
        )

    def _compute_performance_metrics(self, df: pd.DataFrame) -> Dict[str, PerformanceMetric]:
        """Compute key performance metrics."""
        metrics = {}

        # On-time rate
        if "delivery_target_met" in df.columns:
            value = df["delivery_target_met"].mean() * 100
            target = self.BENCHMARKS["on_time_rate"]
            gap = target - value
            status = "below" if value < target else ("above" if value > target * 1.05 else "on_target")
            metrics["on_time_rate"] = PerformanceMetric(
                name="On-Time Delivery Rate",
                value=round(value, 1),
                target=target,
                status=status,
                gap=round(gap, 1),
                gap_pct=round((gap / target) * 100, 1)
            )

        # Complaint rate
        if "complaint" in df.columns:
            value = df["complaint"].mean() * 100
            target = self.BENCHMARKS["complaint_rate"]
            gap = value - target  # Positive means above target (bad)
            status = "above" if value > target else ("below" if value < target * 0.8 else "on_target")
            metrics["complaint_rate"] = PerformanceMetric(
                name="Complaint Rate",
                value=round(value, 1),
                target=target,
                status=status,
                gap=round(gap, 1),
                gap_pct=round((gap / target) * 100, 1) if target > 0 else 0
            )

        # Average delivery time
        if "total_process_time" in df.columns:
            value = df["total_process_time"].mean()
            target = self.BENCHMARKS["avg_delivery_time"]
            gap = value - target  # Positive means above target (bad)
            status = "above" if value > target else ("below" if value < target * 0.9 else "on_target")
            metrics["avg_delivery_time"] = PerformanceMetric(
                name="Average Delivery Time",
                value=round(value, 1),
                target=target,
                status=status,
                gap=round(gap, 1),
                gap_pct=round((gap / target) * 100, 1)
            )

        return metrics

    def _identify_bottlenecks(self, df: pd.DataFrame) -> List[Dict]:
        """Identify operational bottlenecks."""
        bottlenecks = []

        # Process stage bottlenecks
        stage_cols = ["dough_prep_time", "styling_time", "oven_time", "boxing_time", "delivery_duration"]
        for col in stage_cols:
            if col in df.columns:
                avg = df[col].mean()
                p95 = df[col].quantile(0.95)
                benchmark = self.BENCHMARKS.get(col, avg)

                if avg > benchmark * 1.1:  # More than 10% above benchmark
                    variance = df[col].std()
                    severity = "critical" if avg > benchmark * 1.5 else ("high" if avg > benchmark * 1.25 else "medium")

                    # Calculate impact
                    over_benchmark = df[df[col] > benchmark]
                    impact_pct = (len(over_benchmark) / len(df)) * 100

                    bottlenecks.append({
                        "area": col.replace("_", " ").title(),
                        "severity": severity,
                        "metric": f"Average {col.replace('_', ' ')}",
                        "current_value": round(avg, 1),
                        "benchmark_value": benchmark,
                        "p95_value": round(p95, 1),
                        "variance": round(variance, 2),
                        "impact": f"Affects {impact_pct:.0f}% of orders",
                        "root_cause": "Pending AI analysis"
                    })

        # Area-based bottlenecks
        if "delivery_area" in df.columns and "total_process_time" in df.columns:
            overall_avg = df["total_process_time"].mean()
            area_stats = df.groupby("delivery_area")["total_process_time"].agg(["mean", "count", "std"])

            for area in area_stats.index:
                area_avg = area_stats.loc[area, "mean"]
                area_count = area_stats.loc[area, "count"]

                if area_avg > overall_avg * 1.15:  # More than 15% above average
                    severity = "high" if area_avg > overall_avg * 1.3 else "medium"

                    # Additional area analysis
                    area_data = df[df["delivery_area"] == area]
                    area_on_time = area_data["delivery_target_met"].mean() * 100 if "delivery_target_met" in df.columns else 0
                    area_complaints = area_data["complaint"].mean() * 100 if "complaint" in df.columns else 0

                    bottlenecks.append({
                        "area": f"Delivery Area {area}",
                        "severity": severity,
                        "metric": "Average delivery time",
                        "current_value": round(area_avg, 1),
                        "benchmark_value": round(overall_avg, 1),
                        "order_count": int(area_count),
                        "on_time_rate": round(area_on_time, 1),
                        "complaint_rate": round(area_complaints, 1),
                        "impact": f"{area_count} orders affected ({(area_count/len(df))*100:.0f}% of total)",
                        "root_cause": "Pending AI analysis"
                    })

        # Peak hour bottlenecks
        if "order_hour" in df.columns and "total_process_time" in df.columns:
            hour_stats = df.groupby("order_hour")["total_process_time"].agg(["mean", "count"])
            overall_avg = df["total_process_time"].mean()

            peak_hours = hour_stats[hour_stats["mean"] > overall_avg * 1.2].index.tolist()
            if peak_hours:
                for hour in peak_hours:
                    hour_data = df[df["order_hour"] == hour]
                    hour_avg = hour_data["total_process_time"].mean()
                    hour_count = len(hour_data)

                    bottlenecks.append({
                        "area": f"Peak Hour {hour}:00",
                        "severity": "high" if hour_avg > overall_avg * 1.4 else "medium",
                        "metric": "Average process time",
                        "current_value": round(hour_avg, 1),
                        "benchmark_value": round(overall_avg, 1),
                        "order_count": int(hour_count),
                        "impact": f"Peak volume: {hour_count} orders",
                        "root_cause": "Pending AI analysis"
                    })

        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        bottlenecks.sort(key=lambda x: severity_order.get(x["severity"], 4))

        return bottlenecks[:10]  # Top 10 bottlenecks

    def _generate_local_recommendations(self, metrics: Dict, bottlenecks: List[Dict]) -> List[Dict]:
        """Generate basic recommendations based on local analysis."""
        recommendations = []

        # Based on metrics
        for metric_key, metric in metrics.items():
            if metric.status in ["above", "below"] and abs(metric.gap_pct) > 10:
                if metric_key == "on_time_rate":
                    recommendations.append({
                        "priority": "high",
                        "title": "Improve On-Time Delivery",
                        "action": f"Focus on reducing delivery time by {metric.gap:.1f}%",
                        "expected_impact": f"Could improve on-time rate from {metric.value}% to {metric.target}%",
                        "effort": "medium",
                        "evidence": f"Currently {metric.gap:.1f}% below target",
                        "timeline": "this_week"
                    })
                elif metric_key == "complaint_rate":
                    recommendations.append({
                        "priority": "high",
                        "title": "Reduce Customer Complaints",
                        "action": "Identify and address top complaint reasons",
                        "expected_impact": f"Reduce complaints from {metric.value}% to below {metric.target}%",
                        "effort": "medium",
                        "evidence": f"Currently {metric.gap:.1f}% above target",
                        "timeline": "this_week"
                    })

        # Based on bottlenecks
        for bottleneck in bottlenecks[:3]:  # Top 3
            recommendations.append({
                "priority": "high" if bottleneck["severity"] in ["critical", "high"] else "medium",
                "title": f"Address {bottleneck['area']} Bottleneck",
                "action": f"Reduce {bottleneck['metric'].lower()} from {bottleneck['current_value']} to {bottleneck['benchmark_value']}",
                "expected_impact": bottleneck["impact"],
                "effort": "medium",
                "evidence": f"Currently {bottleneck['current_value'] - bottleneck['benchmark_value']:.1f} above benchmark",
                "timeline": "this_week"
            })

        return recommendations

    def analyze(self, df: pd.DataFrame) -> AgentResponse:
        """
        Analyze operations and provide expert recommendations.

        Args:
            df: The dataframe to analyze

        Returns:
            AgentResponse with operations analysis results
        """
        if not self.is_available():
            return self._analyze_locally(df)

        try:
            # Compute local metrics first
            metrics = self._compute_performance_metrics(df)
            bottlenecks = self._identify_bottlenecks(df)
            local_recommendations = self._generate_local_recommendations(metrics, bottlenecks)

            # Build context for Claude
            data_summary = self._build_data_summary(df)
            performance_context = self._build_performance_context(df)

            # Prepare metrics for prompt
            metrics_dict = {
                k: {
                    "value": m.value,
                    "target": m.target,
                    "status": m.status,
                    "gap": m.gap,
                    "gap_pct": m.gap_pct
                }
                for k, m in metrics.items()
            }

            prompt = f"""Analyze this pizza delivery operations data as a Senior Business Analyst Consultant.

{data_summary}

{performance_context}

Pre-computed Performance Metrics:
{json.dumps(metrics_dict, indent=2)}

Pre-identified Bottlenecks:
{json.dumps(bottlenecks, indent=2)}

Your task:
1. Provide an overall performance assessment
2. Identify the root causes for each bottleneck
3. Generate 5-7 prioritized, data-backed recommendations
4. Include specific actions, expected impacts, and evidence

IMPORTANT: Return your analysis as valid JSON matching the expected format.
Focus on actionable insights that can be implemented immediately.
Every recommendation must cite specific data evidence.
"""

            # Call Claude for expert analysis
            response_text, cost = self._call_claude(prompt, max_tokens=3000)

            # Try to parse JSON response
            parsed = self._parse_json_from_response(response_text)

            if parsed:
                # Use AI-enhanced analysis
                perf_summary = parsed.get("performance_summary", {})
                ai_bottlenecks = parsed.get("bottlenecks", bottlenecks)
                ai_recommendations = parsed.get("recommendations", local_recommendations)
                key_insights = parsed.get("key_insights", [])

                overall = perf_summary.get("overall_assessment", "Analysis complete.")

                return AgentResponse(
                    success=True,
                    content=overall,
                    data={
                        "performance_summary": perf_summary,
                        "metrics": metrics_dict,
                        "bottleneck_count": len(ai_bottlenecks),
                        "recommendation_count": len(ai_recommendations),
                        "raw_response": response_text
                    },
                    issues=[{
                        "type": "bottleneck",
                        "column": b.get("area", "unknown"),
                        "severity": b.get("severity", "medium"),
                        "count": b.get("order_count", 0),
                        "description": f"{b.get('metric', '')}: {b.get('current_value', 0)} vs benchmark {b.get('benchmark_value', 0)}",
                        "suggested_fix": b.get("root_cause", ""),
                        "auto_fixable": False
                    } for b in ai_bottlenecks],
                    recommendations=[{
                        "priority": r.get("priority", "medium"),
                        "title": r.get("title", ""),
                        "action": r.get("action", ""),
                        "expected_impact": r.get("expected_impact", ""),
                        "effort": r.get("effort", "medium"),
                        "evidence": r.get("evidence", ""),
                        "timeline": r.get("timeline", "this_week")
                    } for r in ai_recommendations],
                    score=None,
                    cost=cost
                )
            else:
                # AI response wasn't JSON, return free-form with local data
                return AgentResponse(
                    success=True,
                    content=response_text,
                    data={
                        "metrics": metrics_dict,
                        "bottleneck_count": len(bottlenecks),
                        "recommendation_count": len(local_recommendations)
                    },
                    issues=[{
                        "type": "bottleneck",
                        "column": b.get("area", "unknown"),
                        "severity": b.get("severity", "medium"),
                        "count": b.get("order_count", 0),
                        "description": f"{b.get('metric', '')}: {b.get('current_value', 0)} vs benchmark {b.get('benchmark_value', 0)}",
                        "suggested_fix": b.get("root_cause", ""),
                        "auto_fixable": False
                    } for b in bottlenecks],
                    recommendations=[{
                        "priority": r.get("priority", "medium"),
                        "title": r.get("title", ""),
                        "action": r.get("action", "")
                    } for r in local_recommendations],
                    score=None,
                    cost=cost
                )

        except Exception as e:
            return self._analyze_locally(df, error=str(e))

    def _analyze_locally(self, df: pd.DataFrame, error: str = None) -> AgentResponse:
        """Perform local analysis without AI (fallback)."""
        metrics = self._compute_performance_metrics(df)
        bottlenecks = self._identify_bottlenecks(df)
        recommendations = self._generate_local_recommendations(metrics, bottlenecks)

        # Build summary
        summary_parts = ["Operations Analysis Summary:"]

        for metric_key, metric in metrics.items():
            status_icon = "OK" if metric.status == "on_target" else "ISSUE"
            summary_parts.append(f"- {metric.name}: {metric.value} (Target: {metric.target}) [{status_icon}]")

        if bottlenecks:
            summary_parts.append(f"\nIdentified {len(bottlenecks)} bottlenecks.")
            summary_parts.append(f"Top bottleneck: {bottlenecks[0]['area']} - {bottlenecks[0]['severity']} severity")

        summary_parts.append(f"\nGenerated {len(recommendations)} recommendations.")

        if error:
            summary_parts.append(f"\n(AI enhancement unavailable: {error})")

        metrics_dict = {
            k: {
                "value": m.value,
                "target": m.target,
                "status": m.status,
                "gap": m.gap
            }
            for k, m in metrics.items()
        }

        return AgentResponse(
            success=True,
            content="\n".join(summary_parts),
            data={
                "metrics": metrics_dict,
                "bottleneck_count": len(bottlenecks),
                "recommendation_count": len(recommendations),
                "ai_enhanced": False
            },
            issues=[{
                "type": "bottleneck",
                "column": b.get("area", "unknown"),
                "severity": b.get("severity", "medium"),
                "count": b.get("order_count", 0),
                "description": f"{b.get('metric', '')}: {b.get('current_value', 0)} vs benchmark {b.get('benchmark_value', 0)}",
                "suggested_fix": b.get("root_cause", ""),
                "auto_fixable": False
            } for b in bottlenecks],
            recommendations=[{
                "priority": r.get("priority", "medium"),
                "title": r.get("title", ""),
                "action": r.get("action", "")
            } for r in recommendations],
            score=None,
            cost=0.0
        )


# Singleton instance
_business_analyst_agent: Optional[BusinessAnalystAgent] = None


def get_business_analyst_agent() -> BusinessAnalystAgent:
    """
    Get the Business Analyst Agent instance.

    Creates a new instance if:
    - No instance exists
    - API key status has changed (user added/removed key via Settings)
    """
    global _business_analyst_agent

    # Import here to get current API key
    from .base_agent import get_api_key

    # Check if we need to create or refresh the instance
    if _business_analyst_agent is None:
        _business_analyst_agent = BusinessAnalystAgent()
    else:
        # Check if API key status changed (user may have added one)
        current_key = get_api_key()
        if current_key != _business_analyst_agent.api_key:
            # API key changed - create fresh instance
            _business_analyst_agent = BusinessAnalystAgent()

    return _business_analyst_agent
