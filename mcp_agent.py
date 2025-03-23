from dotenv import load_dotenv
import asyncio
import pathlib

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

# Load environment variables
load_dotenv()

server = MCPServerStdio('npx.cmd', ['-y', '@modelcontextprotocol/server-filesystem', str(pathlib.Path(__file__).parent)])
server2 = MCPServerStdio('python', ["-m", "mcp_server_time", "--local-timezone=Europe/Athens"])
mcp_agent = Agent('openai:gpt-4o', mcp_servers=[server, server2])

async def main():
    async with mcp_agent.run_mcp_servers():
        result = await mcp_agent.run('What are my files in this folder and what time is it right now?')
    print(result.data)

if __name__ == "__main__":
    asyncio.run(main())