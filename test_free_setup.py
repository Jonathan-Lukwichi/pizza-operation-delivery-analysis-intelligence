"""
Test Free AI Setup
==================

Run this script to test if your free LLM setup is working.

Usage:
    python test_free_setup.py
"""

import asyncio
import sys
import os

# Add agents to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_ollama():
    """Check if Ollama is running."""
    print("\n1️⃣  Checking Ollama (local LLM)...")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            models = response.json().get("models", [])
            if models:
                print(f"   ✅ Ollama is running with {len(models)} model(s):")
                for m in models[:3]:
                    print(f"      - {m['name']}")
                return True
            else:
                print("   ⚠️  Ollama is running but no models installed")
                print("      Run: ollama pull llama3.1:8b")
                return False
        return False
    except Exception as e:
        print(f"   ❌ Ollama not running: {e}")
        print("      Install from: https://ollama.ai/download")
        return False


def check_groq():
    """Check if Groq API key is available."""
    print("\n2️⃣  Checking Groq (cloud LLM)...")
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        print(f"   ✅ Groq API key found: {api_key[:10]}...")
        return True
    else:
        print("   ❌ No GROQ_API_KEY environment variable")
        print("      Get free key at: https://console.groq.com/")
        return False


def check_gemini():
    """Check if Google API key is available."""
    print("\n3️⃣  Checking Google Gemini (cloud LLM)...")
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        print(f"   ✅ Google API key found: {api_key[:10]}...")
        return True
    else:
        print("   ❌ No GOOGLE_API_KEY environment variable")
        print("      Get free key at: https://aistudio.google.com/")
        return False


async def test_ollama():
    """Test Ollama with a simple prompt."""
    print("\n🧪 Testing Ollama...")
    try:
        from agents.free_llm_providers import OllamaProvider

        llm = OllamaProvider(model="llama3.1:8b")
        response = await llm.generate(
            "In one sentence, what is business analytics?",
            max_tokens=100
        )
        print(f"   ✅ Response: {response.content[:150]}...")
        print(f"   💰 Cost: ${response.cost}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


async def test_groq():
    """Test Groq with a simple prompt."""
    print("\n🧪 Testing Groq...")
    try:
        from agents.free_llm_providers import GroqProvider

        llm = GroqProvider()
        response = await llm.generate(
            "In one sentence, what is AI automation?",
            max_tokens=100
        )
        print(f"   ✅ Response: {response.content[:150]}...")
        print(f"   💰 Cost: ${response.cost}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


async def test_smart_provider():
    """Test the smart auto-detection."""
    print("\n🧪 Testing Smart Provider (auto-detect)...")
    try:
        from agents.free_llm_providers import SmartFreeProvider

        llm = SmartFreeProvider()
        print(f"   📌 Selected provider: {llm.provider.__class__.__name__}")

        response = await llm.generate(
            "What are 2 ways to improve pizza delivery efficiency?",
            system_prompt="You are a business analyst. Be concise.",
            max_tokens=150
        )
        print(f"   ✅ Response:\n      {response.content[:200]}...")
        print(f"   💰 Cost: ${response.cost} (FREE!)")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_agent_integration():
    """Test basic agent with free LLM."""
    print("\n🧪 Testing Agent Integration...")
    try:
        from agents.free_llm_providers import SmartFreeProvider
        from agents.data_agent import DataIngestionAgent

        llm = SmartFreeProvider()
        agent = DataIngestionAgent(llm_client=llm)

        # Just test that the agent initializes correctly
        print(f"   ✅ Data Agent initialized")
        print(f"   📌 Tools available: {list(agent.tools.keys())}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def print_summary(results):
    """Print test summary."""
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for name, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {name}")

    print(f"\n   Total: {passed}/{total} checks passed")

    if passed == 0:
        print("\n⚠️  No LLM provider available!")
        print("   Please either:")
        print("   1. Install Ollama: https://ollama.ai/download")
        print("   2. Get Groq key: https://console.groq.com/")
        print("   3. Get Gemini key: https://aistudio.google.com/")
    elif passed > 0:
        print("\n✅ You're ready to use the AI Agent system for FREE!")


async def main():
    """Run all checks and tests."""
    print("=" * 60)
    print("🔍 FREE AI SETUP CHECKER")
    print("=" * 60)
    print("\nChecking available free LLM providers...\n")

    results = {}

    # Check what's available
    ollama_available = check_ollama()
    groq_available = check_groq()
    gemini_available = check_gemini()

    results["Ollama Available"] = ollama_available
    results["Groq Available"] = groq_available
    results["Gemini Available"] = gemini_available

    # Run actual tests if providers are available
    print("\n" + "-" * 60)
    print("Running LLM tests...")
    print("-" * 60)

    if ollama_available:
        results["Ollama Test"] = await test_ollama()

    if groq_available:
        results["Groq Test"] = await test_groq()

    # Always test smart provider
    results["Smart Provider"] = await test_smart_provider()

    # Test agent integration
    results["Agent Integration"] = await test_agent_integration()

    # Print summary
    print_summary(results)


if __name__ == "__main__":
    asyncio.run(main())
