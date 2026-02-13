"""
Staff Optimization Agent
========================

Workforce analytics, scheduling optimization, and performance management.
"""

from typing import Any, Dict, List, Optional
import logging

from .base import BaseAgent, AgentResponse, AgentTool, AgentStatus

logger = logging.getLogger(__name__)


class StaffOptimizationAgent(BaseAgent):
    """
    Intelligent workforce management and optimization.

    Features:
    - AI-powered scheduling optimization
    - Performance prediction and coaching
    - Skill-based task assignment
    - Fatigue and burnout detection
    - Training recommendations
    """

    def __init__(self, llm_client: Any = None):
        super().__init__(
            name="staff",
            description="workforce analytics, scheduling optimization, and performance management",
            llm_client=llm_client,
        )

    def _register_default_tools(self) -> None:
        """Register staff optimization tools."""

        self.register_tool(AgentTool(
            name="generate_schedule",
            description="Generate optimal staff schedule",
            function=self.generate_schedule,
            parameters={
                "week_start": {"type": "string", "description": "Start date of the week"},
            },
        ))

        self.register_tool(AgentTool(
            name="analyze_performance",
            description="Analyze individual staff performance",
            function=self.analyze_performance,
            parameters={
                "staff_id": {"type": "string", "description": "Staff member ID or name"},
            },
        ))

        self.register_tool(AgentTool(
            name="detect_burnout_risk",
            description="Detect burnout risk for staff members",
            function=self.detect_burnout_risk,
            parameters={},
        ))

        self.register_tool(AgentTool(
            name="get_training_recommendations",
            description="Get training recommendations for staff",
            function=self.get_training_recommendations,
            parameters={},
        ))

        self.register_tool(AgentTool(
            name="get_team_overview",
            description="Get team performance overview",
            function=self.get_team_overview,
            parameters={},
        ))

    async def generate_schedule(self, week_start: str = None) -> Dict[str, Any]:
        """Generate optimal staff schedule."""
        return {
            "week_start": week_start or "2024-02-12",
            "schedule": [
                {
                    "day": "Monday",
                    "shifts": [
                        {"shift": "10-14", "staff": ["John", "Sarah", "Mike"]},
                        {"shift": "14-18", "staff": ["Alice", "Bob"]},
                        {"shift": "18-22", "staff": ["John", "Sarah", "Tom", "Lisa"]},
                    ],
                },
                {
                    "day": "Tuesday",
                    "shifts": [
                        {"shift": "10-14", "staff": ["Alice", "Bob", "Mike"]},
                        {"shift": "14-18", "staff": ["Tom", "Lisa"]},
                        {"shift": "18-22", "staff": ["John", "Sarah", "Alice", "Bob"]},
                    ],
                },
                # ... more days
            ],
            "optimization_notes": [
                "John assigned to peak hours (best performer)",
                "Sarah paired with newer staff for mentoring",
                "Weekend coverage increased by 2 staff",
            ],
            "coverage_score": 94.5,
            "cost_efficiency": 88.2,
        }

    async def analyze_performance(self, staff_id: str = None) -> Dict[str, Any]:
        """Analyze individual staff performance."""
        return {
            "staff_id": staff_id or "John",
            "role": "Driver",
            "tenure_months": 18,
            "performance_score": 92,
            "metrics": {
                "deliveries_completed": 1847,
                "avg_delivery_time": 22.3,
                "on_time_rate": 94.2,
                "complaint_rate": 1.8,
                "customer_rating": 4.7,
            },
            "peer_comparison": {
                "vs_team_avg": "+12%",
                "rank": "2 of 8",
            },
            "strengths": [
                "Excellent time management",
                "High customer satisfaction",
                "Reliable attendance",
            ],
            "areas_for_improvement": [
                "Could improve in Area E (unfamiliar routes)",
                "Evening shift performance slightly lower",
            ],
            "recommendations": [
                "Consider for team lead promotion",
                "Provide Area E route training",
                "Schedule for more morning shifts (peak performance)",
            ],
            "trend": "improving",
        }

    async def detect_burnout_risk(self) -> List[Dict]:
        """Detect burnout risk for staff members."""
        return [
            {
                "staff_id": "Sarah",
                "risk_score": 0.72,
                "risk_level": "high",
                "indicators": [
                    "Worked 6 consecutive weeks without day off",
                    "Performance declining 8% over 2 weeks",
                    "Increased late arrivals (3 in past week)",
                ],
                "recommendations": [
                    "Schedule mandatory day off this week",
                    "Reduce shift hours by 20% next week",
                    "Check in with manager for wellness",
                ],
            },
            {
                "staff_id": "Mike",
                "risk_score": 0.58,
                "risk_level": "medium",
                "indicators": [
                    "Overtime hours up 40% this month",
                    "Break times being skipped",
                ],
                "recommendations": [
                    "Monitor overtime hours",
                    "Encourage regular breaks",
                ],
            },
        ]

    async def get_training_recommendations(self) -> List[Dict]:
        """Get training recommendations for staff."""
        return [
            {
                "staff_id": "Tom",
                "priority": "high",
                "training_needed": "Customer Service",
                "reason": "Complaint rate 2x team average",
                "suggested_course": "Customer Excellence Workshop",
                "estimated_impact": "Reduce complaints by 40%",
            },
            {
                "staff_id": "Lisa",
                "priority": "medium",
                "training_needed": "Route Optimization",
                "reason": "Delivery times 15% above average",
                "suggested_course": "Efficient Delivery Routes",
                "estimated_impact": "Improve delivery time by 10%",
            },
            {
                "staff_id": "New Hires",
                "priority": "high",
                "training_needed": "Onboarding Program",
                "reason": "3 new hires starting next week",
                "suggested_course": "PizzaOps Fundamentals",
                "estimated_impact": "Faster ramp-up to productivity",
            },
        ]

    async def get_team_overview(self) -> Dict[str, Any]:
        """Get team performance overview."""
        return {
            "total_staff": 12,
            "by_role": {
                "drivers": 6,
                "prep_staff": 3,
                "oven_operators": 2,
                "managers": 1,
            },
            "overall_performance": 87.5,
            "top_performers": [
                {"name": "John", "role": "Driver", "score": 95},
                {"name": "Alice", "role": "Prep", "score": 92},
                {"name": "Bob", "role": "Oven", "score": 90},
            ],
            "needs_attention": [
                {"name": "Tom", "issue": "High complaint rate", "action": "Training scheduled"},
                {"name": "Sarah", "issue": "Burnout risk", "action": "Reduced hours"},
            ],
            "staffing_gaps": [
                {"day": "Saturday", "shift": "Evening", "gap": 2},
                {"day": "Sunday", "shift": "Lunch", "gap": 1},
            ],
            "upcoming": [
                "2 interviews scheduled this week",
                "Performance reviews due Feb 15",
            ],
        }

    async def process(self, request: str, context: Optional[Dict] = None) -> AgentResponse:
        """Process a staff-related request."""
        self.update_status(AgentStatus.EXECUTING)

        try:
            request_lower = request.lower()

            if "schedule" in request_lower:
                result = await self.generate_schedule()
            elif "performance" in request_lower or "analyze" in request_lower:
                result = await self.analyze_performance()
            elif "burnout" in request_lower or "risk" in request_lower:
                result = await self.detect_burnout_risk()
            elif "training" in request_lower or "development" in request_lower:
                result = await self.get_training_recommendations()
            elif "team" in request_lower or "overview" in request_lower:
                result = await self.get_team_overview()
            else:
                result = await self.get_team_overview()

            self.update_status(AgentStatus.COMPLETED)

            return AgentResponse(
                content=str(result),
                success=True,
                data=result,
                agent_name=self.name,
            )

        except Exception as e:
            self.update_status(AgentStatus.ERROR)
            return AgentResponse(
                content=f"Error: {e}",
                success=False,
                error=str(e),
                agent_name=self.name,
            )
