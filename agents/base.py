"""
Base Agent Classes
==================

Foundation classes for all AI agents in the system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union
import asyncio
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent execution status."""
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    WAITING = "waiting"
    ERROR = "error"
    COMPLETED = "completed"


class MessageRole(Enum):
    """Message roles in agent conversation."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class AgentMessage:
    """A message in the agent's conversation history."""
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tool_calls: List[Dict] = field(default_factory=list)
    tool_results: List[Dict] = field(default_factory=list)


@dataclass
class AgentResponse:
    """Response from an agent."""
    content: str
    success: bool = True
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    agent_name: str = ""
    thinking: Optional[str] = None
    tool_calls_made: List[str] = field(default_factory=list)
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "agent_name": self.agent_name,
            "confidence": self.confidence,
        }


@dataclass
class AgentTool:
    """
    A tool that an agent can use.

    Tools are functions that agents can call to perform actions
    or retrieve information from external systems.
    """
    name: str
    description: str
    function: Callable
    parameters: Dict[str, Any] = field(default_factory=dict)
    required_params: List[str] = field(default_factory=list)
    returns: str = "string"
    is_async: bool = True
    timeout: int = 30  # seconds

    def to_schema(self) -> Dict[str, Any]:
        """Convert to LLM tool schema format."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": self.parameters,
                "required": self.required_params,
            },
        }

    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters."""
        try:
            if self.is_async:
                return await asyncio.wait_for(
                    self.function(**kwargs),
                    timeout=self.timeout
                )
            else:
                return await asyncio.wait_for(
                    asyncio.to_thread(self.function, **kwargs),
                    timeout=self.timeout
                )
        except asyncio.TimeoutError:
            raise TimeoutError(f"Tool {self.name} timed out after {self.timeout}s")
        except Exception as e:
            logger.error(f"Tool {self.name} failed: {e}")
            raise


class AgentMemory:
    """
    Memory system for agents.

    Stores conversation history, context, and learned patterns.
    """

    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.messages: List[AgentMessage] = []
        self.context: Dict[str, Any] = {}
        self.learned_patterns: List[Dict] = []
        self.session_id: str = datetime.now().strftime("%Y%m%d_%H%M%S")

    def add_message(self, message: AgentMessage) -> None:
        """Add a message to history."""
        self.messages.append(message)
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]

    def get_recent_messages(self, n: int = 10) -> List[AgentMessage]:
        """Get n most recent messages."""
        return self.messages[-n:]

    def set_context(self, key: str, value: Any) -> None:
        """Set a context value."""
        self.context[key] = value

    def get_context(self, key: str, default: Any = None) -> Any:
        """Get a context value."""
        return self.context.get(key, default)

    def clear_context(self) -> None:
        """Clear all context."""
        self.context = {}

    def add_learned_pattern(self, pattern: Dict) -> None:
        """Store a learned pattern for future reference."""
        self.learned_patterns.append({
            **pattern,
            "learned_at": datetime.now().isoformat(),
        })

    def get_conversation_summary(self) -> str:
        """Generate a summary of the conversation."""
        if not self.messages:
            return "No conversation history."

        summary_parts = []
        for msg in self.messages[-5:]:
            role = msg.role.value
            content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
            summary_parts.append(f"{role}: {content}")

        return "\n".join(summary_parts)


class BaseAgent(ABC):
    """
    Base class for all AI agents.

    Provides common functionality for:
    - Tool management
    - Memory/context handling
    - LLM interaction
    - Error handling
    - Logging
    """

    def __init__(
        self,
        name: str,
        description: str,
        llm_client: Any = None,
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ):
        self.name = name
        self.description = description
        self.llm_client = llm_client
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        self.tools: Dict[str, AgentTool] = {}
        self.memory = AgentMemory()
        self.status = AgentStatus.IDLE
        self.logger = logging.getLogger(f"agent.{name}")

        # Register default tools
        self._register_default_tools()

    @abstractmethod
    def _register_default_tools(self) -> None:
        """Register default tools for this agent. Must be implemented by subclasses."""
        pass

    @abstractmethod
    async def process(self, request: str, context: Optional[Dict] = None) -> AgentResponse:
        """
        Process a request. Must be implemented by subclasses.

        Args:
            request: The user's request
            context: Optional context from orchestrator

        Returns:
            AgentResponse with the result
        """
        pass

    def register_tool(self, tool: AgentTool) -> None:
        """Register a tool for this agent."""
        self.tools[tool.name] = tool
        self.logger.info(f"Registered tool: {tool.name}")

    def get_tool_schemas(self) -> List[Dict]:
        """Get schemas for all registered tools."""
        return [tool.to_schema() for tool in self.tools.values()]

    async def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a registered tool."""
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")

        tool = self.tools[tool_name]
        self.logger.info(f"Executing tool: {tool_name}")

        try:
            result = await tool.execute(**kwargs)
            self.logger.info(f"Tool {tool_name} completed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Tool {tool_name} failed: {e}")
            raise

    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent.
        Override in subclasses for custom prompts.
        """
        tools_description = "\n".join([
            f"- {tool.name}: {tool.description}"
            for tool in self.tools.values()
        ])

        return f"""You are {self.name}, an AI agent specialized in {self.description}.

Your capabilities include:
{tools_description}

Guidelines:
1. Use tools when you need to retrieve data or perform actions
2. Be concise but thorough in your analysis
3. Always explain your reasoning
4. If uncertain, state your confidence level
5. Provide actionable recommendations when appropriate

Current context:
{json.dumps(self.memory.context, indent=2, default=str)}
"""

    async def think(self, request: str) -> str:
        """
        Internal reasoning process before responding.
        Can be overridden for custom reasoning logic.
        """
        return f"Processing request: {request}"

    async def call_llm(
        self,
        messages: List[Dict],
        tools: Optional[List[Dict]] = None,
    ) -> Dict:
        """
        Call the LLM with messages and optional tools.

        This is a placeholder - implement actual LLM call based on your provider.
        """
        if self.llm_client is None:
            # Return mock response for testing
            return {
                "content": f"[Mock response from {self.name}]",
                "tool_calls": [],
            }

        # TODO: Implement actual LLM call
        # Example for Anthropic:
        # response = await self.llm_client.messages.create(
        #     model=self.model,
        #     max_tokens=self.max_tokens,
        #     temperature=self.temperature,
        #     system=self.get_system_prompt(),
        #     messages=messages,
        #     tools=tools,
        # )
        # return response

        raise NotImplementedError("LLM client not configured")

    def update_status(self, status: AgentStatus) -> None:
        """Update agent status."""
        self.status = status
        self.logger.debug(f"Status updated to: {status.value}")

    def log_interaction(self, request: str, response: AgentResponse) -> None:
        """Log an interaction for analytics."""
        self.memory.add_message(AgentMessage(
            role=MessageRole.USER,
            content=request,
        ))
        self.memory.add_message(AgentMessage(
            role=MessageRole.ASSISTANT,
            content=response.content,
            metadata=response.metadata,
        ))

    def get_status_report(self) -> Dict[str, Any]:
        """Get current agent status report."""
        return {
            "name": self.name,
            "status": self.status.value,
            "tools_count": len(self.tools),
            "messages_count": len(self.memory.messages),
            "context_keys": list(self.memory.context.keys()),
            "session_id": self.memory.session_id,
        }


class AgentRegistry:
    """
    Registry for managing multiple agents.

    Provides discovery and routing capabilities.
    """

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        """Register an agent."""
        self.agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name}")

    def get(self, name: str) -> Optional[BaseAgent]:
        """Get an agent by name."""
        return self.agents.get(name)

    def list_agents(self) -> List[str]:
        """List all registered agent names."""
        return list(self.agents.keys())

    def get_agent_capabilities(self) -> Dict[str, List[str]]:
        """Get capabilities (tools) for all agents."""
        return {
            name: list(agent.tools.keys())
            for name, agent in self.agents.items()
        }


# Global registry instance
agent_registry = AgentRegistry()
