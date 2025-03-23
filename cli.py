from dotenv import load_dotenv
from typing import List
import asyncio
import logfire
import pathlib

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, TextPart, UserPromptPart

# Load environment variables
load_dotenv()

# Configure logfire to suppress warnings
logfire.configure(send_to_logfire='never')


class CLI:
    def __init__(self):
        self.messages: List[ModelMessage] = []
        server = MCPServerStdio('npx.cmd', ['-y', '@modelcontextprotocol/server-filesystem', str(pathlib.Path(__file__).parent)])
        server2 = MCPServerStdio('python', ["-m", "mcp_server_time", "--local-timezone=Europe/Athens"])
        self.mcp_agent = Agent('openai:gpt-4o', mcp_servers=[server, server2])

    async def chat(self):

        async with self.mcp_agent.run_mcp_servers():
            print("GitHub Agent CLI (type 'quit' to exit)")
            print("Enter your message:")
            while True:
                user_input = input("> ").strip()
                if user_input.lower() == 'quit':
                    break

                
                result = await self.mcp_agent.run(
                    user_input,
                    message_history=self.messages
                )

                # Store the user message
                self.messages.append(
                    ModelRequest(parts=[UserPromptPart(content=user_input)])
                )

                # Store itermediatry messages like tool calls and responses
                filtered_messages = [msg for msg in result.new_messages() 
                                if not (hasattr(msg, 'parts') and 
                                        any(part.part_kind == 'user-prompt' or part.part_kind == 'text' for part in msg.parts))]
                self.messages.extend(filtered_messages)

                # Optional if you want to print out tool calls and responses
                # print(filtered_messages + "\n\n")

                print(result.data)

                # Add the final response from the agent
                self.messages.append(
                    ModelResponse(parts=[TextPart(content=result.data)])
                )


async def main():
    cli = CLI()
    await cli.chat()

if __name__ == "__main__":
    asyncio.run(main())