"""OpenAI integration with MCP server."""

import asyncio
import json
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import AsyncOpenAI

from config import Config


class OpenAIMCPChatBot:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.sessions = []
        self.exit_stack = AsyncExitStack()
        self.available_tools = []
        self.tool_to_session = {}

    async def connect_to_server(self, server_name: str, server_config: dict) -> None:
        """Connect to a single MCP server."""
        try:
            server_params = StdioServerParameters(**server_config)
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read, write = stdio_transport
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            await session.initialize()
            self.sessions.append(session)

            # List available tools for this session
            response = await session.list_tools()
            tools = response.tools
            print(f"Connected to {server_name} with tools:", [t.name for t in tools])

            for tool in tools:
                self.tool_to_session[tool.name] = session
                # Convert MCP tool to OpenAI tool format
                openai_tool = {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema,
                    },
                }
                self.available_tools.append(openai_tool)
        except Exception as e:
            print(f"Failed to connect to {server_name}: {e}")

    async def connect_to_servers(self):
        """Connect to all configured MCP servers."""
        try:
            with open("server_config.json", "r") as file:
                data = json.load(file)

            servers = data.get("mcpServers", {})
            for server_name, server_config in servers.items():
                await self.connect_to_server(server_name, server_config)
        except Exception as e:
            print(f"Error loading server configuration: {e}")
            raise

    async def process_query(self, query: str):
        """Process a query using OpenAI with MCP tools."""
        messages = [{"role": "user", "content": query}]

        response = await self.client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=messages,
            tools=self.available_tools if self.available_tools else None,
        )

        process_query = True
        while process_query:
            message = response.choices[0].message

            if message.content:
                print(message.content)

            # Handle tool calls
            if message.tool_calls:
                messages.append(
                    {
                        "role": "assistant",
                        "content": message.content,
                        "tool_calls": message.tool_calls,
                    }
                )

                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    print(f"Calling tool {tool_name} with args {tool_args}")

                    # Use the correct session for this tool
                    session = self.tool_to_session[tool_name]
                    result = await session.call_tool(tool_name, arguments=tool_args)

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": str(result.content),
                        }
                    )

                # Get the next response
                response = await self.client.chat.completions.create(
                    model=Config.OPENAI_MODEL,
                    messages=messages,
                    tools=self.available_tools if self.available_tools else None,
                )
            else:
                process_query = False

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nOpenAI MCP Chatbot Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == "quit":
                    break
                await self.process_query(query)
            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Cleanly close all resources."""
        await self.exit_stack.aclose()


# Usage example
async def main():
    Config.LLM_PROVIDER = "openai"
    Config.validate()
    chatbot = OpenAIMCPChatBot(api_key=Config.OPENAI_API_KEY)
    try:
        await chatbot.connect_to_servers()
        await chatbot.chat_loop()
    finally:
        await chatbot.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
