import asyncio
import os
from pathlib import Path
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from dotenv import load_dotenv
import httpx

load_dotenv()  # Load environment variables from .env
SONAR_API_KEY = os.getenv('SONAR_API_KEY')

class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.api_url = "https://api.perplexity.ai/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {SONAR_API_KEY}",
            "Content-Type": "application/json"
        }

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server"""
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")
        
        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )
        
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()
        
        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def call_sonar(self, messages, tools=None):
        """Send message to Perplexity Sonar"""
        payload = {
            "model": "sonar-small-chat",
            "messages": messages,
            "temperature": 0.7
        }
        if tools:
            payload["tools"] = tools

        async with httpx.AsyncClient() as client:
            response = await client.post(self.api_url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def process_query(self, query: str) -> str:
        """Process a query using Sonar and available tools"""
        messages = [{"role": "user", "content": query}]

        response = await self.session.list_tools()
        available_tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema  # Perplexity uses "parameters" not "input_schema"
            }
            for tool in response.tools
        ]

        # Initial call to Sonar
        sonar_response = await self.call_sonar(messages, tools=available_tools)

        tool_results = []
        final_text = []

        for choice in sonar_response.get("choices", []):
            for content in choice.get("message", {}).get("content", []):
                if isinstance(content, str):
                    final_text.append(content)
                elif content.get("type") == "tool_use":
                    tool_name = content["name"]
                    tool_args = content["input"]

                    # Call the tool
                    result = await self.session.call_tool(tool_name, tool_args)
                    tool_results.append({"call": tool_name, "result": result})
                    final_text.append(f"[Called tool {tool_name} with args {tool_args}]")

                    # Continue conversation with tool result
                    messages.append({"role": "assistant", "content": content.get("text", "")})
                    messages.append({"role": "user", "content": result.content})

                    sonar_response = await self.call_sonar(messages)
                    follow_up = sonar_response.get("choices", [])[0].get("message", {}).get("content", "")
                    if isinstance(follow_up, list):
                        final_text.extend(follow_up)
                    else:
                        final_text.append(follow_up)

        return "\n".join(final_text)

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")
        
        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\n" + response)
            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

async def main():
    # Use relative path to server.py
    current_dir = Path(__file__).parent
    server_script_path = current_dir / "server.py"

    client = MCPClient()
    try:
        await client.connect_to_server(str(server_script_path))
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())