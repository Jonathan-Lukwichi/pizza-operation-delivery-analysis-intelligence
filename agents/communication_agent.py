"""
Communication Agent
===================

Automated notifications, reports, and stakeholder communication.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

from .base import BaseAgent, AgentResponse, AgentTool, AgentStatus

logger = logging.getLogger(__name__)


class CommunicationAgent(BaseAgent):
    """
    Intelligent multi-channel communication and reporting.

    Features:
    - Personalized message generation
    - Multi-channel delivery (email, SMS, WhatsApp, Slack)
    - Scheduled report automation
    - Alert escalation management
    - Response tracking and follow-up
    """

    # Channel configurations
    CHANNELS = {
        "email": {"enabled": True, "provider": "sendgrid"},
        "sms": {"enabled": True, "provider": "twilio"},
        "whatsapp": {"enabled": True, "provider": "twilio"},
        "slack": {"enabled": True, "provider": "slack_api"},
    }

    def __init__(self, llm_client: Any = None):
        super().__init__(
            name="communication",
            description="automated notifications, reports, and stakeholder communication",
            llm_client=llm_client,
        )

    def _register_default_tools(self) -> None:
        """Register communication tools."""

        self.register_tool(AgentTool(
            name="send_alert",
            description="Send an alert notification",
            function=self.send_alert,
            parameters={
                "alert": {"type": "object", "description": "Alert details"},
                "channels": {"type": "array", "description": "Channels to use"},
                "recipients": {"type": "array", "description": "Recipients"},
            },
        ))

        self.register_tool(AgentTool(
            name="generate_report",
            description="Generate and send a report",
            function=self.generate_report,
            parameters={
                "report_type": {"type": "string", "description": "Type of report"},
                "date_range": {"type": "object", "description": "Date range"},
            },
        ))

        self.register_tool(AgentTool(
            name="send_briefing",
            description="Send a daily/weekly briefing",
            function=self.send_briefing,
            parameters={
                "briefing_type": {"type": "string", "description": "morning or weekly"},
            },
        ))

        self.register_tool(AgentTool(
            name="schedule_message",
            description="Schedule a message for later delivery",
            function=self.schedule_message,
            parameters={
                "message": {"type": "object", "description": "Message details"},
                "schedule_time": {"type": "string", "description": "When to send"},
            },
        ))

        self.register_tool(AgentTool(
            name="get_delivery_status",
            description="Get status of sent communications",
            function=self.get_delivery_status,
            parameters={},
        ))

    async def send_alert(
        self,
        alert: Dict = None,
        channels: List[str] = None,
        recipients: List[str] = None
    ) -> Dict[str, Any]:
        """Send an alert notification."""
        alert = alert or {
            "level": "warning",
            "title": "On-Time Rate Below Target",
            "message": "On-time delivery rate dropped to 78% in the last hour.",
        }
        channels = channels or ["slack", "sms"]
        recipients = recipients or ["manager", "shift_lead"]

        # TODO: Implement actual sending via APIs
        return {
            "success": True,
            "alert_id": "ALT-2024-001",
            "sent_to": recipients,
            "channels_used": channels,
            "timestamp": datetime.now().isoformat(),
            "message_preview": alert.get("message", "")[:100],
        }

    async def generate_report(
        self,
        report_type: str = "daily",
        date_range: Dict = None
    ) -> Dict[str, Any]:
        """Generate and send a report."""
        return {
            "report_id": "RPT-2024-001",
            "type": report_type,
            "date_range": date_range or {"start": "2024-02-01", "end": "2024-02-07"},
            "generated_at": datetime.now().isoformat(),
            "sections": [
                "Executive Summary",
                "KPI Dashboard",
                "Bottleneck Analysis",
                "Staff Performance",
                "Recommendations",
            ],
            "format": "PDF",
            "file_size": "2.4 MB",
            "download_url": "/reports/RPT-2024-001.pdf",
            "sent_to": ["manager@pizzaops.com"],
        }

    async def send_briefing(self, briefing_type: str = "morning") -> Dict[str, Any]:
        """Send a daily/weekly briefing."""
        if briefing_type == "morning":
            content = """
🌅 **Good Morning! PizzaOps Daily Briefing**

📊 **Yesterday's Performance**
• Total Orders: 147 (+5% vs avg)
• On-Time Rate: 89.2% ✅
• Complaint Rate: 3.4%

🔮 **Today's Forecast**
• Expected Orders: 152
• Peak Hours: 12-2pm, 6-8pm
• Recommended Staff: 12

⚠️ **Attention Needed**
• Driver John out sick - backup needed
• Area D showing higher times

📋 **Priority Actions**
1. Assign backup driver for Area D
2. Extra prep for lunch rush
3. Check oven temp calibration

Have a great day! 🍕
            """
        else:
            content = """
📈 **Weekly Performance Summary**

**Week of Feb 5-11, 2024**

📊 **Key Metrics**
• Total Orders: 987 (+8% vs last week)
• Revenue: $24,675
• On-Time Rate: 87.5% (target: 85%) ✅
• Complaint Rate: 4.1% (target: 5%) ✅

🏆 **Top Performers**
1. John - 156 deliveries, 94% on-time
2. Alice - Fastest prep time
3. Bob - Zero complaints

📉 **Areas for Improvement**
• Area E delivery times (+15% vs avg)
• Saturday evening staffing gap

📋 **Next Week Focus**
1. Valentine's Day prep (Feb 14)
2. New driver onboarding
3. Oven maintenance scheduled

Great work team! 🎉
            """

        return {
            "type": briefing_type,
            "content": content,
            "sent_at": datetime.now().isoformat(),
            "channels": ["slack", "email"],
            "recipients": ["all_managers"],
            "read_receipts": 0,
        }

    async def schedule_message(
        self,
        message: Dict = None,
        schedule_time: str = None
    ) -> Dict[str, Any]:
        """Schedule a message for later delivery."""
        message = message or {
            "type": "reminder",
            "content": "Weekly team meeting in 1 hour",
        }

        return {
            "scheduled_id": "SCH-2024-001",
            "message": message,
            "scheduled_for": schedule_time or "2024-02-10T09:00:00",
            "status": "scheduled",
            "channels": ["slack"],
            "can_cancel": True,
        }

    async def get_delivery_status(self) -> Dict[str, Any]:
        """Get status of sent communications."""
        return {
            "summary": {
                "total_sent_today": 47,
                "delivered": 45,
                "pending": 2,
                "failed": 0,
            },
            "by_channel": {
                "email": {"sent": 12, "opened": 8, "clicked": 3},
                "sms": {"sent": 15, "delivered": 15},
                "slack": {"sent": 18, "read": 16},
                "whatsapp": {"sent": 2, "delivered": 2},
            },
            "recent_alerts": [
                {
                    "id": "ALT-001",
                    "title": "Low stock alert",
                    "sent_at": "2024-02-10T14:30:00",
                    "status": "acknowledged",
                },
                {
                    "id": "ALT-002",
                    "title": "On-time rate warning",
                    "sent_at": "2024-02-10T13:15:00",
                    "status": "resolved",
                },
            ],
            "scheduled_upcoming": [
                {
                    "id": "SCH-001",
                    "type": "Daily briefing",
                    "scheduled_for": "2024-02-11T06:00:00",
                },
            ],
        }

    async def generate_personalized_message(
        self,
        template: str,
        recipient: Dict,
        context: Dict
    ) -> str:
        """Generate a personalized message using LLM."""
        if self.llm_client:
            prompt = f"""
            Generate a personalized message based on:
            Template: {template}
            Recipient: {recipient}
            Context: {context}

            Guidelines:
            - Be professional but warm
            - Keep it concise (max 200 words for email, 160 chars for SMS)
            - Include relevant data points
            - End with clear next steps if applicable
            """
            # response = await self.call_llm([{"role": "user", "content": prompt}])
            # return response["content"]

        # Fallback: Simple template substitution
        message = template
        for key, value in context.items():
            message = message.replace(f"{{{key}}}", str(value))
        return message

    async def process(self, request: str, context: Optional[Dict] = None) -> AgentResponse:
        """Process a communication-related request."""
        self.update_status(AgentStatus.EXECUTING)

        try:
            request_lower = request.lower()

            if "alert" in request_lower or "notify" in request_lower:
                result = await self.send_alert()
            elif "report" in request_lower:
                result = await self.generate_report()
            elif "briefing" in request_lower or "morning" in request_lower:
                result = await self.send_briefing("morning")
            elif "weekly" in request_lower:
                result = await self.send_briefing("weekly")
            elif "schedule" in request_lower:
                result = await self.schedule_message()
            elif "status" in request_lower or "delivery" in request_lower:
                result = await self.get_delivery_status()
            else:
                result = await self.get_delivery_status()

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
