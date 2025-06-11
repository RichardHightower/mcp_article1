"""LangChain integration with MCP server."""

import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from config import Config


async def setup_langchain_mcp_agent():
    """Set up a LangChain agent with MCP tools."""

    # Initialize the language model
    llm = ChatOpenAI(
        model=Config.OPENAI_MODEL, temperature=0.1, api_key=Config.OPENAI_API_KEY
    )

    # Connect to our MCP server using MultiServerMCPClient
    client = MultiServerMCPClient(
        {
            "customer-service": {
                "command": "poetry",
                "args": ["run", "python", "src/main.py"],
                "transport": "stdio",
            }
        }
    )

    # Get all available tools from MCP servers
    tools = await client.get_tools()

    # Create a ReAct agent with the tools
    agent = create_react_agent(llm, tools)

    return agent, client


async def run_customer_service_scenarios():
    """Demonstrate LangChain + MCP integration."""
    print("🔗 Setting up LangChain + MCP integration...")

    agent, client = await setup_langchain_mcp_agent()

    # Example customer service scenarios
    scenarios = [
        "Look up customer 12345 and summarize their account status",
        "Create a high-priority support ticket for customer 67890 about billing",
        "Calculate account value for customer with purchases: $150, $300, $89",
    ]

    for scenario in scenarios:
        print(f"\n📞 Scenario: {scenario}")
        try:
            response = await agent.ainvoke(
                {"messages": [{"role": "user", "content": scenario}]}
            )

            # Extract the final AI response
            final_message = response["messages"][-1]
            if hasattr(final_message, "content"):
                print(f"🤖 Response: {final_message.content}")
            else:
                print(f"🤖 Response: {final_message}")

        except Exception as e:
            print(f"❌ Error: {e}")

        print("-" * 60)


async def main():
    """Main entry point."""
    Config.validate()

    await run_customer_service_scenarios()


if __name__ == "__main__":
    asyncio.run(main())
