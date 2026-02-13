"""
Claude API Provider
====================

Official Anthropic Claude integration for the AI Agent system.
"""

import os
import json
import asyncio
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Standard response from LLM."""
    content: str
    model: str
    tokens_used: int = 0
    cost: float = 0.0


class ClaudeProvider:
    """
    Anthropic Claude API Provider.

    Models available:
    - claude-sonnet-4-20250514 (latest, best balance)
    - claude-3-5-sonnet-latest (alias for latest sonnet)
    - claude-3-haiku-20240307 (fastest, cheapest)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-20250514"
    ):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model

        if not self.api_key:
            raise ValueError("Claude API key required")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """Generate response using Claude."""
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.api_key)

            message = client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt or "You are a helpful AI assistant.",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
            )

            # Calculate approximate cost
            input_tokens = message.usage.input_tokens
            output_tokens = message.usage.output_tokens

            # Pricing for Sonnet (as of 2024)
            if "sonnet" in self.model:
                cost = (input_tokens * 0.003 + output_tokens * 0.015) / 1000
            elif "opus" in self.model:
                cost = (input_tokens * 0.015 + output_tokens * 0.075) / 1000
            else:  # haiku
                cost = (input_tokens * 0.00025 + output_tokens * 0.00125) / 1000

            return LLMResponse(
                content=message.content[0].text,
                model=self.model,
                tokens_used=input_tokens + output_tokens,
                cost=cost,
            )

        except ImportError:
            # Fallback to requests
            import requests

            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": self.model,
                    "max_tokens": max_tokens,
                    "system": system_prompt or "You are a helpful AI assistant.",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                }
            )

            result = response.json()

            if "error" in result:
                raise Exception(result["error"]["message"])

            return LLMResponse(
                content=result["content"][0]["text"],
                model=self.model,
                tokens_used=result.get("usage", {}).get("input_tokens", 0) +
                           result.get("usage", {}).get("output_tokens", 0),
            )

    async def generate_with_tools(
        self,
        prompt: str,
        tools: List[Dict],
        system_prompt: Optional[str] = None,
    ) -> Dict:
        """Generate with Claude's native tool use."""
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.api_key)

            # Convert tools to Claude format
            claude_tools = []
            for tool in tools:
                claude_tools.append({
                    "name": tool["name"],
                    "description": tool["description"],
                    "input_schema": tool.get("input_schema", {
                        "type": "object",
                        "properties": tool.get("parameters", {}),
                        "required": tool.get("required_params", []),
                    }),
                })

            message = client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=system_prompt or "You are a helpful AI assistant with access to tools.",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                tools=claude_tools if claude_tools else None,
            )

            # Parse response
            tool_calls = []
            text_content = ""

            for block in message.content:
                if block.type == "text":
                    text_content = block.text
                elif block.type == "tool_use":
                    tool_calls.append({
                        "tool": block.name,
                        "parameters": block.input,
                        "id": block.id,
                    })

            return {
                "content": text_content,
                "tool_calls": tool_calls,
            }

        except ImportError:
            # Fallback: use prompt-based tool calling
            tool_desc = "You have access to these tools:\n\n"
            for tool in tools:
                tool_desc += f"- {tool['name']}: {tool['description']}\n"

            tool_desc += """
To use a tool, respond with JSON:
{"tool": "tool_name", "parameters": {"param1": "value1"}}

Otherwise respond normally.
"""
            response = await self.generate(f"{tool_desc}\n\nUser: {prompt}", system_prompt)

            try:
                if "{" in response.content and "tool" in response.content:
                    tool_call = json.loads(response.content)
                    return {"content": "", "tool_calls": [tool_call]}
            except:
                pass

            return {"content": response.content, "tool_calls": []}


# Create a global instance for easy import
def get_claude_client(api_key: Optional[str] = None) -> ClaudeProvider:
    """Get a Claude client instance."""
    return ClaudeProvider(api_key=api_key)
