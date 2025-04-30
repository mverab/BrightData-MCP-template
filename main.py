from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()

model = ChatAnthropic(model="claude-3-5-sonnet-20240620")

server_params = StdioServerParameters(
    command="npx",
    env={
        "API_TOKEN": os.getenv("API_TOKEN"),
        "BROWSER_AUTH": os.getenv("BROWSER_AUTH"),
        "WEB_UNLOCKER_ZONE": os.getenv("WEB_UNLOCKER_ZONE"),
    },
    # Make sure to update to the full absolute path to your math_server.py file
    args=["@brightdata/mcp"],
)


async def chat_with_agent():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_react_agent(model, tools)

            # Start conversation history
            messages = [
                {
                    "role": "system",
                    "content": "You can use multiple tools in sequence to answer complex questions. Think step by step.",
                }
            ]

            print("Type 'exit' or 'quit' to end the chat.")
            while True:
                user_input = input("\nYou: ")
                if user_input.strip().lower() in {"exit", "quit"}:
                    print("Goodbye!")
                    break

                # Add user message to history
                messages.append({"role": "user", "content": user_input})

                # Call the agent with the full message history
                agent_response = await agent.ainvoke({"messages": messages})

                # Extract agent's reply and add to history
                ai_message = agent_response["messages"][-1].content
                print(f"Agent: {ai_message}")


if __name__ == "__main__":
    asyncio.run(chat_with_agent())
