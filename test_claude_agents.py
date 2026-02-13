"""
Test Claude-Powered AI Agents
==============================

This script tests the AI agent system with your Claude API key.

Usage:
    python test_claude_agents.py
"""

import asyncio
import os
import sys

# Fix Windows encoding for emojis
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add agents to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.claude_provider import ClaudeProvider


async def test_claude_connection():
    """Test basic Claude API connection."""
    print("\n" + "=" * 60)
    print("🔌 TEST 1: Claude API Connection")
    print("=" * 60)

    try:
        claude = ClaudeProvider()
        response = await claude.generate(
            "Say 'Hello! Claude is working!' in exactly those words.",
            max_tokens=50
        )
        print(f"✅ Response: {response.content}")
        print(f"📊 Tokens used: {response.tokens_used}")
        print(f"💰 Cost: ${response.cost:.6f}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_business_analysis():
    """Test Claude for business analysis."""
    print("\n" + "=" * 60)
    print("📊 TEST 2: Business Analysis")
    print("=" * 60)

    try:
        claude = ClaudeProvider()
        response = await claude.generate(
            prompt="""Analyze this pizza delivery data and give 3 specific recommendations:

            - Average delivery time: 32 minutes (target: 30 min)
            - On-time rate: 78% (target: 85%)
            - Top complaint: "Cold food" (45% of complaints)
            - Slowest area: Area D (avg 38 minutes)
            - Busiest hours: 12-2pm and 6-8pm
            """,
            system_prompt="You are an expert business analyst for a pizza delivery company. Be specific and actionable.",
            max_tokens=500
        )
        print(f"✅ Analysis:\n{response.content}")
        print(f"\n💰 Cost: ${response.cost:.6f}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_tool_calling():
    """Test Claude's tool calling capability."""
    print("\n" + "=" * 60)
    print("🔧 TEST 3: Tool Calling")
    print("=" * 60)

    try:
        claude = ClaudeProvider()

        tools = [
            {
                "name": "get_delivery_stats",
                "description": "Get delivery statistics for a specific time period",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "period": {
                            "type": "string",
                            "description": "Time period: today, week, month"
                        },
                        "area": {
                            "type": "string",
                            "description": "Delivery area: A, B, C, D, E, or all"
                        }
                    },
                    "required": ["period"]
                }
            },
            {
                "name": "get_driver_performance",
                "description": "Get performance metrics for a specific driver",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "driver_name": {
                            "type": "string",
                            "description": "Name of the driver"
                        }
                    },
                    "required": ["driver_name"]
                }
            }
        ]

        response = await claude.generate_with_tools(
            prompt="What are this week's delivery stats for Area D?",
            tools=tools,
            system_prompt="You are a delivery analytics assistant. Use tools when needed."
        )

        print(f"✅ Response: {response}")

        if response.get("tool_calls"):
            print(f"🔧 Tool calls made:")
            for tc in response["tool_calls"]:
                print(f"   - {tc['tool']}: {tc['parameters']}")
        else:
            print(f"📝 Text response: {response.get('content', '')[:200]}")

        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_agent_with_claude():
    """Test a full agent with Claude."""
    print("\n" + "=" * 60)
    print("🤖 TEST 4: Full Agent Integration")
    print("=" * 60)

    try:
        from agents.claude_provider import ClaudeProvider
        from agents.process_agent import ProcessMiningAgent

        claude = ClaudeProvider()
        agent = ProcessMiningAgent(llm_client=claude)

        print(f"✅ Agent initialized: {agent.name}")
        print(f"📌 Available tools: {list(agent.tools.keys())}")

        # Test agent processing
        response = await agent.process("What are the main bottlenecks?")
        print(f"\n📊 Agent response:")
        print(f"   Success: {response.success}")
        print(f"   Data: {response.data}")

        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_orchestrator():
    """Test the full orchestrator with Claude."""
    print("\n" + "=" * 60)
    print("🧠 TEST 5: Orchestrator (Multi-Agent)")
    print("=" * 60)

    try:
        from agents.claude_provider import ClaudeProvider
        from agents.orchestrator import OrchestratorAgent
        from agents.data_agent import DataIngestionAgent
        from agents.process_agent import ProcessMiningAgent
        from agents.quality_agent import QualityAssuranceAgent

        claude = ClaudeProvider()

        # Create orchestrator
        orchestrator = OrchestratorAgent(llm_client=claude)

        # Register agents
        orchestrator.register_agent(DataIngestionAgent(llm_client=claude))
        orchestrator.register_agent(ProcessMiningAgent(llm_client=claude))
        orchestrator.register_agent(QualityAssuranceAgent(llm_client=claude))

        print(f"✅ Orchestrator initialized")
        print(f"📌 Registered agents: {list(orchestrator._agents.keys())}")

        # Test a query
        response = await orchestrator.process(
            "Give me an overview of delivery performance and any quality issues"
        )

        print(f"\n📊 Orchestrator response:")
        print(f"   Success: {response.success}")
        print(f"   Agents used: {response.data.get('agents_used', [])}")
        print(f"   Content preview: {response.content[:300]}...")

        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("🚀 CLAUDE AI AGENT SYSTEM TEST")
    print("=" * 60)

    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ No ANTHROPIC_API_KEY found in .env file")
        return

    print(f"✅ API Key found: {api_key[:20]}...")

    results = {}

    # Run tests
    results["Claude Connection"] = await test_claude_connection()
    results["Business Analysis"] = await test_business_analysis()
    results["Tool Calling"] = await test_tool_calling()
    results["Agent Integration"] = await test_agent_with_claude()
    results["Orchestrator"] = await test_orchestrator()

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    passed = 0
    for name, result in results.items():
        status = "✅" if result else "❌"
        print(f"   {status} {name}")
        if result:
            passed += 1

    print(f"\n   Total: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("\n🎉 All tests passed! Your Claude-powered AI agents are ready!")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")


if __name__ == "__main__":
    # Install required packages if missing
    try:
        from dotenv import load_dotenv
    except ImportError:
        print("Installing python-dotenv...")
        os.system("pip install python-dotenv")
        from dotenv import load_dotenv

    try:
        import anthropic
    except ImportError:
        print("Installing anthropic...")
        os.system("pip install anthropic")

    asyncio.run(main())
