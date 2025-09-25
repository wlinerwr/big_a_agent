from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
import sys
from dotenv import load_dotenv
from anthropic import Anthropic
from typing import Optional
from contextlib import AsyncExitStack

#加载环境变量
load_dotenv()

class MCPClient:
    def __init__(self):
        self.session : Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()

    async def connent_to_server(self):
        server_params = StdioServerParameters(
            command="python",
            args=["D:/Big_Agent/tushare_mcp_server.py"],
            env=None
        )
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        response = await self.session.list_tools()
        for tool in response.tools:
            print("----------------------------------------------------")
            print(f"工具名字 : {tool.name}")
            print(f"输出内容 : {tool.inputSchema}")

    async def clearup(self):
        await self.exit_stack.aclose()

async def main():
    client = MCPClient()
    try:
        await client.connent_to_server()
    except Exception as e:
        print(e)
    finally:
        await client.clearup()

if __name__ == "__main__":
    asyncio.run(main())
        