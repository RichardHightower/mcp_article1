"""LiteLLM integration with MCP server."""

import asyncio
import json

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

                    # Initial conversation
                    messages = [
                        {
                            "role": "user",
                            "content": "Customer 67890 recently purchases were $150, $300, $13 and $89. "
                            "Calculate their total account value.",
                        }
                    ]

                    # First call to get tool requests
                    response = await litellm.acompletion(
                        model=model,
                        messages=messages,
                        tools=tools,
                    )

                    # Extract the response
                    message = response.choices[0].message

                    # Check if the model made tool calls
                    if hasattr(message, "tool_calls") and message.tool_calls:
                        print(f"🔧 Tool calls made: {len(message.tool_calls)}")

                        # Add assistant's message with tool calls to conversation
                        messages.append(
                            {
                                "role": "assistant",
                                "content": message.content,
                                "tool_calls": message.tool_calls,
                            }
                        )

                        # Execute each tool call
                        for call in message.tool_calls:
                            print(f"   - Executing {call.function.name}")

                            # Execute the tool through MCP
                            arguments = json.loads(call.function.arguments)
                            result = await session.call_tool(
                                call.function.name, arguments
                            )

                            # Add tool result to conversation
                            messages.append(
                                {
                                    "role": "tool",
                                    "content": str(result.content),
                                    "tool_call_id": call.id,
                                }
                            )

                        # Get final response from model with tool results
                        final_response = await litellm.acompletion(
                            model=model,
                            messages=messages,
                            tools=tools,
                        )

                        final_content = final_response.choices[0].message.content
                        print(f"🤖 Final Response: {final_content}")

                    else:
                        # Display content if available (no tools called)
                        if message.content:
                            print(f"🤖 Response: {message.content}")
                        else:
                            print("🤖 Response: (No response)")

                except Exception as e:
                    print(f"Error with {model}: {e}")


async def main():
    """Main entry point."""
    Config.validate()
    await setup_litellm_mcp()


if __name__ == "__main__":
    asyncio.run(main())
