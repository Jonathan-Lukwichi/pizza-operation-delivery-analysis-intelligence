"""
Example Usage of the AI Agent System
=====================================

This file demonstrates how to use the PizzaOps AI Agent system
for autonomous business analytics.
"""

import asyncio
from datetime import datetime, timedelta

# Import agents
from agents import (
    OrchestratorAgent,
    DataIngestionAgent,
    ProcessMiningAgent,
    DeliveryIntelligenceAgent,
    QualityAssuranceAgent,
    DemandForecastAgent,
    StaffOptimizationAgent,
    CommunicationAgent,
)


async def setup_agent_system():
    """Initialize and configure the agent system."""

    # Create orchestrator (central coordinator)
    orchestrator = OrchestratorAgent(llm_client=None)  # Add LLM client in production

    # Create specialist agents
    agents = {
        "data": DataIngestionAgent(),
        "process": ProcessMiningAgent(),
        "delivery": DeliveryIntelligenceAgent(),
        "quality": QualityAssuranceAgent(),
        "forecast": DemandForecastAgent(),
        "staff": StaffOptimizationAgent(),
        "communication": CommunicationAgent(),
    }

    # Register agents with orchestrator
    for agent in agents.values():
        orchestrator.register_agent(agent)

    return orchestrator, agents


async def example_1_simple_query():
    """Example 1: Simple data query."""
    print("\n" + "="*60)
    print("Example 1: Simple Data Query")
    print("="*60)

    orchestrator, _ = await setup_agent_system()

    # Ask a simple question
    response = await orchestrator.process("What's our on-time delivery rate?")

    print(f"Question: What's our on-time delivery rate?")
    print(f"Response: {response.content}")
    print(f"Success: {response.success}")
    print(f"Agents used: {response.data.get('agents_used', [])}")


async def example_2_insight_request():
    """Example 2: Request for insights."""
    print("\n" + "="*60)
    print("Example 2: Insight Request")
    print("="*60)

    orchestrator, _ = await setup_agent_system()

    # Ask for insights
    response = await orchestrator.process(
        "Why are complaints increasing in Area D?"
    )

    print(f"Question: Why are complaints increasing in Area D?")
    print(f"Response: {response.content}")
    print(f"Agents used: {response.data.get('agents_used', [])}")


async def example_3_forecast_request():
    """Example 3: Demand forecasting."""
    print("\n" + "="*60)
    print("Example 3: Demand Forecasting")
    print("="*60)

    orchestrator, agents = await setup_agent_system()

    # Get forecast directly from forecast agent
    forecast_agent = agents["forecast"]
    forecast = await forecast_agent.generate_forecast(horizon=7)

    print("7-Day Demand Forecast:")
    for day in forecast["forecast"][:7]:
        print(f"  {day['date']}: {day['predicted_orders']} orders "
              f"({day['lower_bound']}-{day['upper_bound']})")


async def example_4_staffing_recommendation():
    """Example 4: Get staffing recommendations."""
    print("\n" + "="*60)
    print("Example 4: Staffing Recommendation")
    print("="*60)

    orchestrator, agents = await setup_agent_system()

    # Get staffing recommendation
    forecast_agent = agents["forecast"]
    recommendation = await forecast_agent.get_staffing_recommendation(
        date=datetime.now().strftime("%Y-%m-%d")
    )

    print(f"Staffing for {recommendation['date']}:")
    print(f"  Predicted orders: {recommendation['predicted_orders']}")
    print(f"  Staff needed:")
    for role, count in recommendation['staffing'].items():
        print(f"    - {role}: {count}")


async def example_5_bottleneck_detection():
    """Example 5: Detect bottlenecks."""
    print("\n" + "="*60)
    print("Example 5: Bottleneck Detection")
    print("="*60)

    orchestrator, agents = await setup_agent_system()

    # Detect bottlenecks
    process_agent = agents["process"]
    bottlenecks = await process_agent.detect_bottlenecks()

    print("Detected Bottlenecks:")
    for bn in bottlenecks:
        print(f"  - {bn['location']}: {bn['severity']} severity")
        print(f"    Issue: {bn['metric']} = {bn['current_value']} (threshold: {bn['threshold']})")
        print(f"    Recommendation: {bn['recommendation']}")


async def example_6_complaint_risk():
    """Example 6: Predict complaint risk."""
    print("\n" + "="*60)
    print("Example 6: Complaint Risk Prediction")
    print("="*60)

    orchestrator, agents = await setup_agent_system()

    # Get high-risk orders
    quality_agent = agents["quality"]
    high_risk = await quality_agent.get_high_risk_orders()

    print("High-Risk Orders:")
    for order in high_risk:
        print(f"  Order {order['order_id']}:")
        print(f"    Risk Score: {order['risk_score']}")
        print(f"    Predicted Issue: {order['predicted_issue']}")
        print(f"    Intervention: {order['intervention']}")


async def example_7_morning_briefing():
    """Example 7: Generate morning briefing."""
    print("\n" + "="*60)
    print("Example 7: Morning Briefing")
    print("="*60)

    orchestrator, agents = await setup_agent_system()

    # Get morning briefing
    comm_agent = agents["communication"]
    briefing = await comm_agent.send_briefing("morning")

    print("Morning Briefing Content:")
    print(briefing["content"])


async def example_8_multi_agent_workflow():
    """Example 8: Complex multi-agent workflow."""
    print("\n" + "="*60)
    print("Example 8: Multi-Agent Workflow")
    print("="*60)

    orchestrator, agents = await setup_agent_system()

    # Complex query that requires multiple agents
    response = await orchestrator.process(
        "Give me a complete operations overview: "
        "current performance, any bottlenecks, "
        "high-risk orders, and staffing for tomorrow."
    )

    print("Multi-Agent Response:")
    print(f"Content: {response.content[:500]}...")
    print(f"\nAgents used: {response.data.get('agents_used', [])}")
    print(f"Execution time: {response.metadata.get('execution_time', 0):.2f}s")


async def example_9_scenario_analysis():
    """Example 9: What-if scenario analysis."""
    print("\n" + "="*60)
    print("Example 9: Scenario Analysis")
    print("="*60)

    orchestrator, agents = await setup_agent_system()

    # Run scenario
    forecast_agent = agents["forecast"]
    scenario = await forecast_agent.run_scenario({
        "promotion": True,
        "discount_pct": 20,
        "advertising": "social_media",
    })

    print("Scenario: 20% Discount Promotion")
    print(f"  Baseline demand: {scenario['baseline_demand']}")
    print(f"  Scenario demand: {scenario['scenario_demand']} (+{scenario['change_pct']}%)")
    print(f"  Additional staff needed:")
    for role, count in scenario['staffing_impact'].items():
        print(f"    - {role}: +{count}")
    print(f"  Net financial impact: ${scenario['cost_impact']['net_impact']}")
    print(f"  Recommendation: {scenario['recommendation']}")


async def example_10_automated_alerts():
    """Example 10: Set up automated alerts."""
    print("\n" + "="*60)
    print("Example 10: Automated Alerts")
    print("="*60)

    orchestrator, agents = await setup_agent_system()

    # Send an alert
    comm_agent = agents["communication"]
    alert_result = await comm_agent.send_alert(
        alert={
            "level": "warning",
            "title": "Delivery Time Increasing",
            "message": "Average delivery time has increased to 32 minutes in the last hour.",
        },
        channels=["slack", "sms"],
        recipients=["manager", "shift_lead"],
    )

    print("Alert Sent:")
    print(f"  Alert ID: {alert_result['alert_id']}")
    print(f"  Sent to: {alert_result['sent_to']}")
    print(f"  Channels: {alert_result['channels_used']}")
    print(f"  Time: {alert_result['timestamp']}")


async def main():
    """Run all examples."""
    print("="*60)
    print("PizzaOps AI Agent System - Example Usage")
    print("="*60)

    # Run examples
    await example_1_simple_query()
    await example_2_insight_request()
    await example_3_forecast_request()
    await example_4_staffing_recommendation()
    await example_5_bottleneck_detection()
    await example_6_complaint_risk()
    await example_7_morning_briefing()
    await example_8_multi_agent_workflow()
    await example_9_scenario_analysis()
    await example_10_automated_alerts()

    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
