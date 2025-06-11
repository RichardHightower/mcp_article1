"""LiteLLM integration with MCP server."""

import asyncio

import litellm
from litellm import experimental_mcp_client
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from config import Config


async def setup_litellm_mcp():
    """Set up LiteLLM with MCP tools."""

    # Create MCP server connection
    server_params = StdioServerParameters(
        command="poetry", args=["run", "python", "src/main.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the MCP connection
            await session.initialize()

            # Load MCP tools in OpenAI format
            tools = await experimental_mcp_client.load_mcp_tools(
                session=session, format="openai"
            )

            print(f"Loaded {len(tools)} MCP tools")

            # Use tools with different models
            models_to_test = []

            if Config.LLM_PROVIDER == "openai":
                models_to_test.append(Config.OPENAI_MODEL)
            elif Config.LLM_PROVIDER == "anthropic":
                models_to_test.append(Config.ANTHROPIC_MODEL)
            else:
                models_to_test = [Config.OPENAI_MODEL, Config.ANTHROPIC_MODEL]

            for model in models_to_test:
                try:
                    print(f"\nTesting with {model}...")
                    response = await litellm.acompletion(
                        model=model,
                        messages=[
                            {
                                "role": "user",
                                "content": "Get customer 12345 information",
                            }
                        ],
                        tools=tools,
                    )
                    # Extract just the message content
                    content = response.choices[0].message.content
                    print(f"🤖 Response: {content}")
                except Exception as e:
                    print(f"Error with {model}: {e}")


async def main():
    """Main entry point."""
    Config.validate()
    await setup_litellm_mcp()


if __name__ == "__main__":
    asyncio.run(main())
