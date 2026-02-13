"""
PizzaOps AI Module
==================

AI-powered analytics and automation for the PizzaOps Intelligence platform.

Includes two specialized AI agents:
1. Data Quality Agent - Analyzes and cleans datasets
2. Business Analyst Agent - Analyzes operations and provides recommendations
"""

from .service import AIService, get_ai_service
from .chat_handler import ChatHandler
from .insights_generator import InsightsGenerator
from .base_agent import BaseAgent, AgentResponse
from .data_quality_agent import DataQualityAgent, get_data_quality_agent
from .business_analyst import BusinessAnalystAgent, get_business_analyst_agent

__all__ = [
    # Core Service
    "AIService",
    "get_ai_service",
    "ChatHandler",
    "InsightsGenerator",
    # Agents
    "BaseAgent",
    "AgentResponse",
    "DataQualityAgent",
    "get_data_quality_agent",
    "BusinessAnalystAgent",
    "get_business_analyst_agent",
]
