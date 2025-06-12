"""OpenAI Agents SDK integration with MCP server."""

import asyncio
from agents import Agent, Runner
from agents.mcp import MCPServerStdio

from config import Config


async def run_customer_service_scenarios():
    """Demonstrate OpenAI Agents + MCP integration."""
    print("🤖 Setting up OpenAI Agents + MCP integration...")

    # Create MCP server connection with proper async context manager
    mcp_server = MCPServerStdio(
        params={
            "command": "poetry",
            "args": ["run", "python", "src/main.py"]
        },
        cache_tools_list=True,
        name="Customer Service Server",
        client_session_timeout_seconds=30  # Increase timeout for startup
    )

    # Use the MCP server within an async context manager
    async with mcp_server as server:
        # Create agent with the connected MCP server
        agent = Agent(
            name="Customer Service Agent",
            instructions="""You are a helpful customer service assistant.
            Use the available tools to help customers with their requests.
            Always be professional and empathetic.
            
            Available tools:
            - get_recent_customers: Get a list of recent customers
            - create_support_ticket: Create support tickets for customers
            - calculate_account_value: Calculate customer account values
            
            When helping customers:
            1. Look up their information first when possible
            2. Create tickets for issues that need follow-up
            3. Calculate account values when discussing billing or purchases
            4. Always provide clear, helpful responses""",
            mcp_servers=[server]
        )

        # Example customer service scenarios
        scenarios = [
            "Get a list of recent customers and summarize their status",
            "Create a high-priority support ticket for customer 67890 about billing issues",
            "Calculate the account value for customer 12345 with purchases: $150, $300, $89"
        ]

        for i, scenario in enumerate(scenarios, 1):
            print(f"\n📞 Scenario {i}: {scenario}")
            try:
                # Run the agent with the scenario
                result = await Runner.run(agent, scenario)
                print(f"🤖 Agent Response: {result.final_output}")
            except Exception as e:
                print(f"❌ Error: {e}")

            print("-" * 60)


async def main():
    """Main entry point."""
    Config.validate()
    if Config.LLM_PROVIDER != "openai":
        print("OpenAI Agents example requires OpenAI. Set LLM_PROVIDER=openai in .env")
        return

    await run_customer_service_scenarios()


if __name__ == "__main__":
    asyncio.run(main())