"""
Orchestrator Agent
==================

Central coordinator that manages all specialist agents.
Uses a state machine approach for complex multi-step workflows.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import json
import logging

from .base import (
    BaseAgent,
    AgentResponse,
    AgentTool,
    AgentStatus,
    AgentMessage,
    MessageRole,
    agent_registry,
)

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """Types of user intents."""
    DATA_QUERY = "data_query"           # "What's our on-time rate?"
    INSIGHT_REQUEST = "insight_request"  # "Why are complaints up?"
    ACTION_REQUEST = "action_request"    # "Generate a report"
    FORECAST_REQUEST = "forecast_request"  # "Predict next week's demand"
    ALERT_CHECK = "alert_check"          # "Any issues I should know about?"
    CONFIGURATION = "configuration"       # "Change the delivery target"
    GENERAL = "general"                   # Catch-all


class WorkflowState(Enum):
    """States in the agent workflow."""
    INIT = "init"
    CLASSIFYING = "classifying"
    PLANNING = "planning"
    EXECUTING = "executing"
    SYNTHESIZING = "synthesizing"
    RESPONDING = "responding"
    ERROR = "error"
    COMPLETE = "complete"


@dataclass
class ExecutionPlan:
    """Plan for executing a request."""
    intent: IntentType
    agents_needed: List[str]
    steps: List[Dict[str, Any]]
    parallel_execution: bool = True
    estimated_time: float = 0.0


@dataclass
class AgentResult:
    """Result from a specialist agent."""
    agent_name: str
    success: bool
    data: Any
    error: Optional[str] = None
    execution_time: float = 0.0


class OrchestratorAgent(BaseAgent):
    """
    Central orchestrator that coordinates all specialist agents.

    Responsibilities:
    - Classify user intents
    - Route requests to appropriate agents
    - Coordinate multi-agent workflows
    - Synthesize responses from multiple agents
    - Handle errors and fallbacks
    """

    def __init__(self, llm_client: Any = None):
        super().__init__(
            name="orchestrator",
            description="central coordination of all specialist agents",
            llm_client=llm_client,
            model="claude-3-5-sonnet-20241022",
        )

        # Specialist agents (lazy loaded)
        self._agents: Dict[str, BaseAgent] = {}

        # Agent routing map
        self.intent_to_agents: Dict[IntentType, List[str]] = {
            IntentType.DATA_QUERY: ["data", "process"],
            IntentType.INSIGHT_REQUEST: ["process", "quality", "delivery"],
            IntentType.ACTION_REQUEST: ["communication"],
            IntentType.FORECAST_REQUEST: ["forecast", "staff"],
            IntentType.ALERT_CHECK: ["process", "quality", "delivery"],
            IntentType.CONFIGURATION: ["data"],
            IntentType.GENERAL: ["data"],
        }

        # Workflow state
        self.current_state = WorkflowState.INIT

    def _register_default_tools(self) -> None:
        """Register orchestrator-specific tools."""

        # Tool: Route to specialist agent
        self.register_tool(AgentTool(
            name="route_to_agent",
            description="Route a request to a specialist agent",
            function=self._route_to_agent,
            parameters={
                "agent_name": {
                    "type": "string",
                    "description": "Name of the specialist agent",
                    "enum": ["data", "process", "delivery", "quality", "forecast", "staff", "communication"],
                },
                "request": {
                    "type": "string",
                    "description": "The request to send to the agent",
                },
            },
            required_params=["agent_name", "request"],
        ))

        # Tool: Synthesize multiple responses
        self.register_tool(AgentTool(
            name="synthesize_responses",
            description="Combine responses from multiple agents into a unified answer",
            function=self._synthesize_responses,
            parameters={
                "responses": {
                    "type": "array",
                    "description": "List of agent responses to synthesize",
                },
                "original_request": {
                    "type": "string",
                    "description": "The original user request",
                },
            },
            required_params=["responses", "original_request"],
        ))

        # Tool: Generate execution plan
        self.register_tool(AgentTool(
            name="create_plan",
            description="Create an execution plan for a complex request",
            function=self._create_plan,
            parameters={
                "intent": {
                    "type": "string",
                    "description": "The classified intent",
                },
                "context": {
                    "type": "object",
                    "description": "Additional context for planning",
                },
            },
            required_params=["intent"],
        ))

    async def _route_to_agent(self, agent_name: str, request: str) -> AgentResult:
        """Route a request to a specialist agent."""
        agent = self._get_agent(agent_name)
        if agent is None:
            return AgentResult(
                agent_name=agent_name,
                success=False,
                data=None,
                error=f"Agent {agent_name} not found",
            )

        start_time = datetime.now()
        try:
            response = await agent.process(request, self.memory.context)
            execution_time = (datetime.now() - start_time).total_seconds()

            return AgentResult(
                agent_name=agent_name,
                success=response.success,
                data=response.data,
                error=response.error,
                execution_time=execution_time,
            )
        except Exception as e:
            logger.error(f"Error routing to {agent_name}: {e}")
            return AgentResult(
                agent_name=agent_name,
                success=False,
                data=None,
                error=str(e),
            )

    async def _synthesize_responses(
        self,
        responses: List[AgentResult],
        original_request: str
    ) -> str:
        """Synthesize multiple agent responses into a unified answer."""

        # Build context from responses
        context_parts = []
        for resp in responses:
            if resp.success and resp.data:
                context_parts.append(f"[{resp.agent_name}]: {json.dumps(resp.data, default=str)}")
            elif resp.error:
                context_parts.append(f"[{resp.agent_name}]: Error - {resp.error}")

        context = "\n".join(context_parts)

        # Use LLM to synthesize if available
        if self.llm_client:
            synthesis_prompt = f"""
            Original request: {original_request}

            Agent responses:
            {context}

            Synthesize these responses into a clear, unified answer.
            Focus on:
            1. Directly answering the user's question
            2. Highlighting key insights
            3. Noting any conflicts or uncertainties
            4. Providing actionable recommendations
            """

            # Call LLM for synthesis
            # response = await self.call_llm([{"role": "user", "content": synthesis_prompt}])
            # return response["content"]

        # Fallback: Simple concatenation
        return f"Based on analysis from {len(responses)} agents:\n\n{context}"

    async def _create_plan(self, intent: str, context: Optional[Dict] = None) -> ExecutionPlan:
        """Create an execution plan for a request."""
        intent_type = IntentType(intent) if intent in [e.value for e in IntentType] else IntentType.GENERAL

        agents_needed = self.intent_to_agents.get(intent_type, ["data"])

        steps = [
            {"agent": agent, "action": "process", "order": i}
            for i, agent in enumerate(agents_needed)
        ]

        return ExecutionPlan(
            intent=intent_type,
            agents_needed=agents_needed,
            steps=steps,
            parallel_execution=len(agents_needed) > 1,
            estimated_time=len(steps) * 2.0,  # ~2 seconds per agent
        )

    def _get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get a specialist agent by name (lazy loading)."""
        if name not in self._agents:
            agent = agent_registry.get(name)
            if agent:
                self._agents[name] = agent
        return self._agents.get(name)

    def register_agent(self, agent: BaseAgent) -> None:
        """Register a specialist agent."""
        self._agents[agent.name] = agent
        agent_registry.register(agent)
        self.logger.info(f"Registered specialist agent: {agent.name}")

    async def classify_intent(self, request: str) -> IntentType:
        """
        Classify the user's intent.

        Uses pattern matching and optionally LLM for complex cases.
        """
        request_lower = request.lower()

        # Pattern-based classification
        if any(word in request_lower for word in ["rate", "percentage", "count", "total", "average", "what"]):
            return IntentType.DATA_QUERY

        if any(word in request_lower for word in ["why", "reason", "cause", "explain", "insight"]):
            return IntentType.INSIGHT_REQUEST

        if any(word in request_lower for word in ["predict", "forecast", "next", "future", "expect"]):
            return IntentType.FORECAST_REQUEST

        if any(word in request_lower for word in ["generate", "create", "send", "report", "email"]):
            return IntentType.ACTION_REQUEST

        if any(word in request_lower for word in ["alert", "issue", "problem", "warning", "check"]):
            return IntentType.ALERT_CHECK

        if any(word in request_lower for word in ["set", "change", "configure", "update"]):
            return IntentType.CONFIGURATION

        # Use LLM for ambiguous cases
        if self.llm_client:
            classification_prompt = f"""
            Classify this request into one of these categories:
            - data_query: Questions about metrics, KPIs, numbers
            - insight_request: Questions about reasons, causes, patterns
            - action_request: Requests to do something (generate, send, create)
            - forecast_request: Questions about future predictions
            - alert_check: Questions about issues or warnings
            - configuration: Requests to change settings
            - general: Everything else

            Request: "{request}"

            Return only the category name.
            """
            # response = await self.call_llm([{"role": "user", "content": classification_prompt}])
            # return IntentType(response["content"].strip())

        return IntentType.GENERAL

    async def process(self, request: str, context: Optional[Dict] = None) -> AgentResponse:
        """
        Process a request through the agent workflow.

        Workflow:
        1. Classify intent
        2. Create execution plan
        3. Execute with specialist agents (parallel when possible)
        4. Synthesize responses
        5. Return unified response
        """
        self.update_status(AgentStatus.THINKING)
        start_time = datetime.now()

        # Update context
        if context:
            for key, value in context.items():
                self.memory.set_context(key, value)

        try:
            # Step 1: Classify intent
            self.current_state = WorkflowState.CLASSIFYING
            intent = await self.classify_intent(request)
            self.logger.info(f"Classified intent: {intent.value}")

            # Step 2: Create execution plan
            self.current_state = WorkflowState.PLANNING
            plan = await self._create_plan(intent.value, context)
            self.logger.info(f"Created plan with {len(plan.agents_needed)} agents")

            # Step 3: Execute with specialist agents
            self.current_state = WorkflowState.EXECUTING
            self.update_status(AgentStatus.EXECUTING)

            if plan.parallel_execution:
                # Execute agents in parallel
                tasks = [
                    self._route_to_agent(agent_name, request)
                    for agent_name in plan.agents_needed
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Handle exceptions
                agent_results = []
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        agent_results.append(AgentResult(
                            agent_name=plan.agents_needed[i],
                            success=False,
                            data=None,
                            error=str(result),
                        ))
                    else:
                        agent_results.append(result)
            else:
                # Execute agents sequentially
                agent_results = []
                for agent_name in plan.agents_needed:
                    result = await self._route_to_agent(agent_name, request)
                    agent_results.append(result)

            # Step 4: Synthesize responses
            self.current_state = WorkflowState.SYNTHESIZING
            synthesized = await self._synthesize_responses(agent_results, request)

            # Step 5: Build response
            self.current_state = WorkflowState.RESPONDING
            execution_time = (datetime.now() - start_time).total_seconds()

            response = AgentResponse(
                content=synthesized,
                success=True,
                data={
                    "intent": intent.value,
                    "agents_used": plan.agents_needed,
                    "results": [
                        {
                            "agent": r.agent_name,
                            "success": r.success,
                            "time": r.execution_time,
                        }
                        for r in agent_results
                    ],
                },
                metadata={
                    "execution_time": execution_time,
                    "parallel_execution": plan.parallel_execution,
                },
                agent_name=self.name,
            )

            self.current_state = WorkflowState.COMPLETE
            self.update_status(AgentStatus.COMPLETED)

            # Log interaction
            self.log_interaction(request, response)

            return response

        except Exception as e:
            self.current_state = WorkflowState.ERROR
            self.update_status(AgentStatus.ERROR)
            logger.error(f"Orchestrator error: {e}")

            return AgentResponse(
                content=f"I encountered an error processing your request: {str(e)}",
                success=False,
                error=str(e),
                agent_name=self.name,
            )

    async def gather_report_data(self, date_range: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """Gather data from all agents for report generation."""
        self.memory.set_context("date_range", {
            "start": date_range[0].isoformat(),
            "end": date_range[1].isoformat(),
        })

        # Gather from all relevant agents
        tasks = [
            self._route_to_agent("data", "Get data summary"),
            self._route_to_agent("process", "Get bottleneck summary"),
            self._route_to_agent("quality", "Get complaint summary"),
            self._route_to_agent("delivery", "Get delivery summary"),
            self._route_to_agent("forecast", "Get forecast summary"),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            "date_range": date_range,
            "data_summary": results[0].data if not isinstance(results[0], Exception) else None,
            "process_summary": results[1].data if not isinstance(results[1], Exception) else None,
            "quality_summary": results[2].data if not isinstance(results[2], Exception) else None,
            "delivery_summary": results[3].data if not isinstance(results[3], Exception) else None,
            "forecast_summary": results[4].data if not isinstance(results[4], Exception) else None,
        }

    async def morning_briefing(self) -> AgentResponse:
        """Generate automated morning briefing."""
        request = """
        Generate a morning briefing including:
        1. Overnight performance summary
        2. Today's forecast and staffing needs
        3. Any issues requiring attention
        4. Priority actions for today
        """

        return await self.process(request)

    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status."""
        return {
            "current_state": self.current_state.value,
            "agent_status": self.status.value,
            "registered_agents": list(self._agents.keys()),
            "context": self.memory.context,
        }
