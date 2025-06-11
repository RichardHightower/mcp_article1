"""DSPy integration with MCP server."""

import asyncio

import dspy
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from config import Config


# Define a DSPy signature for our customer service tasks
class CustomerServiceSignature(dspy.Signature):
    """Handle customer service requests using available tools."""

    request: str = dspy.InputField(desc="Customer service request")
    response: str = dspy.OutputField(desc="Helpful customer service response")


async def setup_dspy_mcp_integration():
    """Set up DSPy with MCP tools."""

    # Configure DSPy with your preferred language model
    if Config.LLM_PROVIDER == "openai":
        llm = dspy.LM(f"openai/{Config.OPENAI_MODEL}", api_key=Config.OPENAI_API_KEY)
    elif Config.LLM_PROVIDER == "anthropic":
        llm = dspy.LM(
            f"anthropic/{Config.ANTHROPIC_MODEL}", api_key=Config.ANTHROPIC_API_KEY
        )
    else:
        print("DSPy requires OpenAI or Anthropic provider")
        return None

    dspy.configure(lm=llm)

    # Create MCP client connection
    server_params = StdioServerParameters(
        command="poetry", args=["run", "python", "src/main.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the MCP connection
            await session.initialize()

            # List available tools
            tools = await session.list_tools()

            # Convert MCP tools to DSPy tools
            dspy_tools = []
            for tool in tools.tools:
                dspy_tools.append(dspy.Tool.from_mcp_tool(session, tool))

            # Create a ReAct agent with the tools
            react = dspy.ReAct(CustomerServiceSignature, tools=dspy_tools)

            # Test the integration
            result = await react.acall(
                request="Look up customer 12345 and create a support ticket as the bbq grill that she bought is defective."
            )

            print(f"DSPy Result: {result}")


async def main():
    """Main entry point."""
    Config.validate()
    await setup_dspy_mcp_integration()


if __name__ == "__main__":
    asyncio.run(main())
