"""
Free LLM Providers for AI Agent System
=======================================

This module provides FREE alternatives to paid LLM APIs.
Choose the one that works best for your situation.

Options:
1. Ollama (Local) - Best quality, runs on your PC
2. Groq (Cloud) - Very fast, generous free tier
3. Google Gemini (Cloud) - Good quality, free tier
4. Hugging Face (Cloud/Local) - Open source models
"""

import os
import json
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Standard response from any LLM provider."""
    content: str
    model: str
    tokens_used: int = 0
    cost: float = 0.0  # Always 0 for free providers!


class BaseLLMProvider(ABC):
    """Base class for LLM providers."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """Generate a response from the LLM."""
        pass

    @abstractmethod
    async def generate_with_tools(
        self,
        prompt: str,
        tools: List[Dict],
        system_prompt: Optional[str] = None,
    ) -> Dict:
        """Generate a response with tool calling capability."""
        pass


# =============================================================================
# OPTION 1: OLLAMA (Local, Free, Best Quality)
# =============================================================================

class OllamaProvider(BaseLLMProvider):
    """
    Ollama - Run LLMs locally on your PC for FREE.

    Setup:
    1. Download Ollama: https://ollama.ai/download
    2. Run: ollama pull llama3.1
    3. That's it! Ollama runs at http://localhost:11434

    Models (all free):
    - llama3.1:8b (best balance of speed/quality)
    - llama3.1:70b (best quality, needs good GPU)
    - mistral:7b (fast, good for simple tasks)
    - phi3:mini (very fast, lightweight)
    - codellama (best for code tasks)
    """

    def __init__(
        self,
        model: str = "llama3.1:8b",
        base_url: str = "http://localhost:11434"
    ):
        self.model = model
        self.base_url = base_url

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """Generate response using Ollama."""
        try:
            import aiohttp
        except ImportError:
            # Fallback to requests
            import requests

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    }
                },
                timeout=120
            )

            result = response.json()
            return LLMResponse(
                content=result["message"]["content"],
                model=self.model,
                tokens_used=result.get("eval_count", 0),
                cost=0.0  # FREE!
            )

        # Async version with aiohttp
        async with aiohttp.ClientSession() as session:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            async with session.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    }
                }
            ) as response:
                result = await response.json()
                return LLMResponse(
                    content=result["message"]["content"],
                    model=self.model,
                    tokens_used=result.get("eval_count", 0),
                    cost=0.0
                )

    async def generate_with_tools(
        self,
        prompt: str,
        tools: List[Dict],
        system_prompt: Optional[str] = None,
    ) -> Dict:
        """Generate with tool calling (Ollama supports this in newer versions)."""
        # Build tool descriptions into prompt
        tool_desc = "You have access to these tools:\n\n"
        for tool in tools:
            tool_desc += f"- {tool['name']}: {tool['description']}\n"
            tool_desc += f"  Parameters: {json.dumps(tool.get('input_schema', {}))}\n\n"

        tool_desc += """
To use a tool, respond with JSON in this format:
{"tool": "tool_name", "parameters": {"param1": "value1"}}

If you don't need a tool, just respond normally.
"""

        full_prompt = f"{tool_desc}\n\nUser request: {prompt}"

        response = await self.generate(full_prompt, system_prompt)

        # Try to parse tool call from response
        try:
            content = response.content.strip()
            if content.startswith("{") and "tool" in content:
                tool_call = json.loads(content)
                return {
                    "content": "",
                    "tool_calls": [tool_call],
                }
        except json.JSONDecodeError:
            pass

        return {"content": response.content, "tool_calls": []}


# =============================================================================
# OPTION 2: GROQ (Cloud, Free Tier, VERY Fast)
# =============================================================================

class GroqProvider(BaseLLMProvider):
    """
    Groq - Extremely fast inference, generous free tier.

    Setup:
    1. Go to https://console.groq.com/
    2. Sign up (free)
    3. Get API key
    4. Set environment variable: GROQ_API_KEY=your_key

    Free Tier Limits:
    - 14,400 requests/day
    - 30 requests/minute
    - That's ~10 requests per minute = plenty for most uses!

    Models (all free):
    - llama-3.1-70b-versatile (best quality)
    - llama-3.1-8b-instant (faster)
    - mixtral-8x7b-32768 (good for long context)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "llama-3.1-8b-instant"
    ):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1"

        if not self.api_key:
            raise ValueError(
                "Groq API key required. Get free key at https://console.groq.com/"
            )

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """Generate response using Groq."""
        try:
            from groq import Groq

            client = Groq(api_key=self.api_key)

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            return LLMResponse(
                content=response.choices[0].message.content,
                model=self.model,
                tokens_used=response.usage.total_tokens,
                cost=0.0  # FREE!
            )

        except ImportError:
            # Fallback to requests
            import requests

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
            )

            result = response.json()
            return LLMResponse(
                content=result["choices"][0]["message"]["content"],
                model=self.model,
                tokens_used=result.get("usage", {}).get("total_tokens", 0),
                cost=0.0
            )

    async def generate_with_tools(
        self,
        prompt: str,
        tools: List[Dict],
        system_prompt: Optional[str] = None,
    ) -> Dict:
        """Groq supports native tool calling."""
        try:
            from groq import Groq

            client = Groq(api_key=self.api_key)

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            # Convert tools to OpenAI format
            openai_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameters": tool.get("input_schema", {}),
                    }
                }
                for tool in tools
            ]

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=openai_tools if openai_tools else None,
            )

            message = response.choices[0].message

            tool_calls = []
            if message.tool_calls:
                for tc in message.tool_calls:
                    tool_calls.append({
                        "tool": tc.function.name,
                        "parameters": json.loads(tc.function.arguments),
                    })

            return {
                "content": message.content or "",
                "tool_calls": tool_calls,
            }

        except ImportError:
            # Fallback to prompt-based tool calling
            return await OllamaProvider.generate_with_tools(self, prompt, tools, system_prompt)


# =============================================================================
# OPTION 3: GOOGLE GEMINI (Cloud, Free Tier)
# =============================================================================

class GeminiProvider(BaseLLMProvider):
    """
    Google Gemini - Good quality, free tier available.

    Setup:
    1. Go to https://aistudio.google.com/
    2. Get API key (free)
    3. Set environment variable: GOOGLE_API_KEY=your_key

    Free Tier Limits:
    - 60 requests/minute
    - 1,500 requests/day

    Models:
    - gemini-1.5-flash (fast, free)
    - gemini-1.5-pro (better quality, free tier available)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-1.5-flash"
    ):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = model

        if not self.api_key:
            raise ValueError(
                "Google API key required. Get free key at https://aistudio.google.com/"
            )

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """Generate response using Gemini."""
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model)

            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            response = model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                }
            )

            return LLMResponse(
                content=response.text,
                model=self.model,
                cost=0.0  # FREE!
            )

        except ImportError:
            # Fallback to REST API
            import requests

            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1/models/{self.model}:generateContent",
                params={"key": self.api_key},
                json={
                    "contents": [{"parts": [{"text": full_prompt}]}],
                    "generationConfig": {
                        "temperature": temperature,
                        "maxOutputTokens": max_tokens,
                    }
                }
            )

            result = response.json()
            content = result["candidates"][0]["content"]["parts"][0]["text"]

            return LLMResponse(
                content=content,
                model=self.model,
                cost=0.0
            )

    async def generate_with_tools(
        self,
        prompt: str,
        tools: List[Dict],
        system_prompt: Optional[str] = None,
    ) -> Dict:
        """Gemini supports function calling."""
        # For simplicity, using prompt-based approach
        # Full implementation would use Gemini's native function calling
        tool_desc = "You have access to these tools:\n\n"
        for tool in tools:
            tool_desc += f"- {tool['name']}: {tool['description']}\n"

        tool_desc += "\nTo use a tool, respond with: TOOL: tool_name(param1=value1)\n"
        tool_desc += "Otherwise, respond normally.\n\n"

        full_prompt = f"{tool_desc}User: {prompt}"

        response = await self.generate(full_prompt, system_prompt)

        return {"content": response.content, "tool_calls": []}


# =============================================================================
# OPTION 4: HUGGING FACE (Free Inference API)
# =============================================================================

class HuggingFaceProvider(BaseLLMProvider):
    """
    Hugging Face - Free inference API for many models.

    Setup:
    1. Go to https://huggingface.co/
    2. Sign up (free)
    3. Get token from https://huggingface.co/settings/tokens
    4. Set environment variable: HF_TOKEN=your_token

    Free Tier:
    - Rate limited but free
    - Many open source models available

    Models:
    - microsoft/Phi-3-mini-4k-instruct (fast, good quality)
    - mistralai/Mistral-7B-Instruct-v0.2 (good balance)
    - meta-llama/Meta-Llama-3-8B-Instruct (requires approval)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "microsoft/Phi-3-mini-4k-instruct"
    ):
        self.api_key = api_key or os.getenv("HF_TOKEN")
        self.model = model
        self.base_url = "https://api-inference.huggingface.co/models"

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """Generate response using Hugging Face Inference API."""
        import requests

        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:"

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        response = requests.post(
            f"{self.base_url}/{self.model}",
            headers=headers,
            json={
                "inputs": full_prompt,
                "parameters": {
                    "temperature": temperature,
                    "max_new_tokens": max_tokens,
                    "return_full_text": False,
                }
            }
        )

        result = response.json()

        if isinstance(result, list):
            content = result[0].get("generated_text", "")
        else:
            content = result.get("generated_text", str(result))

        return LLMResponse(
            content=content,
            model=self.model,
            cost=0.0  # FREE!
        )

    async def generate_with_tools(
        self,
        prompt: str,
        tools: List[Dict],
        system_prompt: Optional[str] = None,
    ) -> Dict:
        """Use prompt-based tool calling for HF models."""
        tool_desc = "Available tools:\n"
        for tool in tools:
            tool_desc += f"- {tool['name']}: {tool['description']}\n"

        full_prompt = f"{tool_desc}\n\n{prompt}"
        response = await self.generate(full_prompt, system_prompt)

        return {"content": response.content, "tool_calls": []}


# =============================================================================
# SMART PROVIDER - Auto-selects best free option
# =============================================================================

class SmartFreeProvider(BaseLLMProvider):
    """
    Automatically selects the best available free LLM provider.

    Priority:
    1. Ollama (if running locally)
    2. Groq (if API key available)
    3. Gemini (if API key available)
    4. Hugging Face (always available)
    """

    def __init__(self):
        self.provider = self._detect_best_provider()
        logger.info(f"Using free LLM provider: {self.provider.__class__.__name__}")

    def _detect_best_provider(self) -> BaseLLMProvider:
        """Detect and return the best available provider."""

        # Try Ollama first (check if running)
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                logger.info("Ollama detected - using local LLM")
                return OllamaProvider()
        except:
            pass

        # Try Groq
        if os.getenv("GROQ_API_KEY"):
            logger.info("Groq API key found - using Groq")
            return GroqProvider()

        # Try Gemini
        if os.getenv("GOOGLE_API_KEY"):
            logger.info("Google API key found - using Gemini")
            return GeminiProvider()

        # Fallback to Hugging Face
        logger.info("Using Hugging Face free inference")
        return HuggingFaceProvider()

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """Generate using detected provider."""
        return await self.provider.generate(prompt, system_prompt, temperature, max_tokens)

    async def generate_with_tools(
        self,
        prompt: str,
        tools: List[Dict],
        system_prompt: Optional[str] = None,
    ) -> Dict:
        """Generate with tools using detected provider."""
        return await self.provider.generate_with_tools(prompt, tools, system_prompt)


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

async def example_usage():
    """Example of using free LLM providers."""

    print("=" * 60)
    print("Free LLM Provider Examples")
    print("=" * 60)

    # Option 1: Auto-detect best provider
    print("\n1. Smart Auto-Detection:")
    provider = SmartFreeProvider()
    response = await provider.generate(
        "What are 3 ways to improve pizza delivery speed?",
        system_prompt="You are a helpful business analyst."
    )
    print(f"Response: {response.content[:200]}...")
    print(f"Cost: ${response.cost} (FREE!)")

    # Option 2: Explicit Ollama
    print("\n2. Using Ollama (local):")
    try:
        ollama = OllamaProvider(model="llama3.1:8b")
        response = await ollama.generate("Explain bottleneck analysis in 2 sentences.")
        print(f"Response: {response.content}")
    except Exception as e:
        print(f"Ollama not available: {e}")

    # Option 3: With tool calling
    print("\n3. Tool Calling Example:")
    tools = [
        {
            "name": "get_delivery_stats",
            "description": "Get delivery statistics for a time period",
            "input_schema": {
                "type": "object",
                "properties": {
                    "period": {"type": "string", "description": "today, week, month"}
                }
            }
        }
    ]

    response = await provider.generate_with_tools(
        "What are today's delivery stats?",
        tools=tools
    )
    print(f"Response: {response}")


if __name__ == "__main__":
    asyncio.run(example_usage())
