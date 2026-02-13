"""
PizzaOps AI Agent System
========================

A multi-agent AI system for autonomous business analytics automation.

Agent Architecture:
- OrchestratorAgent: Central coordinator for all agents
- DataIngestionAgent: Intelligent data loading and validation
- ProcessMiningAgent: Bottleneck detection and root cause analysis
- DeliveryIntelligenceAgent: Driver and route optimization
- QualityAssuranceAgent: Complaint prediction and prevention
- DemandForecastAgent: Demand prediction and staffing
- StaffOptimizationAgent: Workforce analytics and scheduling
- CommunicationAgent: Multi-channel notifications and reports

Usage:
    from agents import OrchestratorAgent, ClaudeProvider

    claude = ClaudeProvider()  # Uses API key from .env
    orchestrator = OrchestratorAgent(llm_client=claude)
    response = await orchestrator.process("What's our on-time rate today?")
"""

from .base import BaseAgent, AgentResponse, AgentTool
from .claude_provider import ClaudeProvider
from .orchestrator import OrchestratorAgent
from .data_agent import DataIngestionAgent
from .process_agent import ProcessMiningAgent
from .delivery_agent import DeliveryIntelligenceAgent
from .quality_agent import QualityAssuranceAgent
from .forecast_agent import DemandForecastAgent
from .staff_agent import StaffOptimizationAgent
from .communication_agent import CommunicationAgent

__all__ = [
    "BaseAgent",
    "AgentResponse",
    "AgentTool",
    "ClaudeProvider",
    "OrchestratorAgent",
    "DataIngestionAgent",
    "ProcessMiningAgent",
    "DeliveryIntelligenceAgent",
    "QualityAssuranceAgent",
    "DemandForecastAgent",
    "StaffOptimizationAgent",
    "CommunicationAgent",
]

__version__ = "1.0.0"
