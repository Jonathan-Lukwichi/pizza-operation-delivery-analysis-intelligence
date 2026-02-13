"""
Test Script for AI Agents
=========================

Tests the Data Quality Agent and Business Analyst Agent.
"""

import sys
import os

# Windows encoding fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from dotenv import load_dotenv
load_dotenv()


def create_sample_data():
    """Create sample pizza delivery data for testing."""
    np.random.seed(42)
    n = 100

    # Generate dates
    base_date = datetime(2024, 1, 1)
    dates = [base_date + timedelta(days=np.random.randint(0, 30)) for _ in range(n)]

    # Generate process times
    data = {
        "order_id": range(1, n + 1),
        "order_date": dates,
        "order_hour": [d.hour for d in [datetime(2024, 1, 1, np.random.randint(10, 22)) for _ in range(n)]],
        "dough_prep_time": np.random.normal(5, 1.5, n).clip(2, 10),
        "styling_time": np.random.normal(3, 0.8, n).clip(1, 6),
        "oven_time": np.random.normal(10, 2, n).clip(6, 18),
        "boxing_time": np.random.normal(2, 0.5, n).clip(1, 4),
        "delivery_duration": np.random.normal(12, 4, n).clip(5, 30),
        "delivery_area": np.random.choice(["A", "B", "C", "D", "E"], n, p=[0.25, 0.25, 0.2, 0.15, 0.15]),
        "chef_name": np.random.choice(["Alice", "Bob", "Charlie", "Diana"], n),
        "driver_name": np.random.choice(["Mike", "Sarah", "John", "Emily"], n),
        "oven_temperature": np.random.normal(220, 10, n).clip(180, 260),
    }

    df = pd.DataFrame(data)

    # Calculate total process time
    df["total_process_time"] = (
        df["dough_prep_time"] +
        df["styling_time"] +
        df["oven_time"] +
        df["boxing_time"] +
        df["delivery_duration"]
    )

    # Delivery target (30 minutes)
    df["delivery_target_met"] = (df["total_process_time"] <= 30).astype(int)

    # Generate complaints (correlated with long delivery times)
    complaint_prob = np.where(df["total_process_time"] > 35, 0.3, 0.05)
    df["complaint"] = (np.random.random(n) < complaint_prob).astype(int)
    df["complaint_reason"] = np.where(
        df["complaint"] == 1,
        np.random.choice(["Cold food", "Late delivery", "Wrong order", "Damaged packaging"], n),
        None
    )

    # Add some missing values for testing
    df.loc[np.random.choice(n, 5, replace=False), "oven_temperature"] = np.nan

    # Add some duplicates
    df = pd.concat([df, df.iloc[:3]], ignore_index=True)

    # Add some outliers
    df.loc[n, "delivery_duration"] = 120  # Extreme outlier

    return df


def test_data_quality_agent():
    """Test the Data Quality Agent."""
    print("\n" + "=" * 60)
    print("Testing Data Quality Agent")
    print("=" * 60)

    from ai.data_quality_agent import get_data_quality_agent

    # Create sample data
    df = create_sample_data()
    print(f"\nSample data created: {len(df)} rows, {len(df.columns)} columns")

    # Get agent
    agent = get_data_quality_agent()
    print(f"Agent available: {agent.is_available()}")

    if not agent.is_available():
        print("SKIPPING: API key not configured")
        return False

    # Run analysis
    print("\nRunning data quality analysis...")
    result = agent.analyze(df)

    print(f"\nSuccess: {result.success}")
    print(f"Quality Score: {result.score}")
    print(f"Cost: ${result.cost:.4f}")
    print(f"\nSummary: {result.content[:200]}...")

    if result.issues:
        print(f"\nIssues found: {len(result.issues)}")
        for issue in result.issues[:3]:
            print(f"  - {issue.get('type', 'unknown')}: {issue.get('column', 'unknown')} ({issue.get('severity', 'medium')})")

    if result.recommendations:
        print(f"\nRecommendations: {len(result.recommendations)}")
        for rec in result.recommendations[:2]:
            print(f"  - {rec.get('action', 'Unknown action')}")

    # Test applying fixes
    if result.issues:
        print("\nTesting fix application...")
        auto_fixes = [i for i in result.issues if i.get("auto_fixable", False)]
        if auto_fixes:
            df_cleaned, actions = agent.apply_fixes(df, auto_fixes[:2])
            print(f"Fixes applied: {len(actions)}")
            for action in actions:
                print(f"  - {action}")
            print(f"Rows after cleaning: {len(df_cleaned)}")

    print("\nData Quality Agent test PASSED")
    return True


def test_business_analyst_agent():
    """Test the Business Analyst Agent."""
    print("\n" + "=" * 60)
    print("Testing Business Analyst Agent")
    print("=" * 60)

    from ai.business_analyst import get_business_analyst_agent

    # Create sample data (already cleaned)
    df = create_sample_data()
    df = df.drop_duplicates()  # Pre-clean
    print(f"\nSample data: {len(df)} rows")

    # Get agent
    agent = get_business_analyst_agent()
    print(f"Agent available: {agent.is_available()}")

    if not agent.is_available():
        print("SKIPPING: API key not configured")
        return False

    # Run analysis
    print("\nRunning operations analysis...")
    result = agent.analyze(df)

    print(f"\nSuccess: {result.success}")
    print(f"Cost: ${result.cost:.4f}")
    print(f"\nAssessment: {result.content[:300]}...")

    if result.issues:
        print(f"\nBottlenecks identified: {len(result.issues)}")
        for bottleneck in result.issues[:3]:
            print(f"  - {bottleneck.get('column', 'unknown')}: {bottleneck.get('severity', 'medium')} severity")

    if result.recommendations:
        print(f"\nRecommendations: {len(result.recommendations)}")
        for rec in result.recommendations[:3]:
            print(f"  - [{rec.get('priority', 'medium').upper()}] {rec.get('title', 'Unknown')}")
            print(f"    Action: {rec.get('action', 'N/A')[:80]}...")

    print("\nBusiness Analyst Agent test PASSED")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("AI AGENTS TEST SUITE")
    print("=" * 60)

    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        print(f"API Key found: {api_key[:20]}...")
    else:
        print("WARNING: No API key found. Tests will run in fallback mode.")

    results = []

    # Test Data Quality Agent
    try:
        results.append(("Data Quality Agent", test_data_quality_agent()))
    except Exception as e:
        print(f"\nData Quality Agent test FAILED: {e}")
        results.append(("Data Quality Agent", False))

    # Test Business Analyst Agent
    try:
        results.append(("Business Analyst Agent", test_business_analyst_agent()))
    except Exception as e:
        print(f"\nBusiness Analyst Agent test FAILED: {e}")
        results.append(("Business Analyst Agent", False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")

    passed_count = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed_count}/{len(results)} tests passed")

    return all(p for _, p in results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
