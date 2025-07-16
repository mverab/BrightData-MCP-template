from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()

model = ChatOpenAI(model="gpt-4.1-2025-04-14")
api_key=os.getenv("OPENAI_API_KEY")

server_params = StdioServerParameters(
    command="npx",
    env={
        "API_TOKEN": os.getenv("API_TOKEN"),
        "BROWSER_AUTH": os.getenv("BROWSER_AUTH"),
        "WEB_UNLOCKER_ZONE": os.getenv("WEB_UNLOCKER_ZONE"),
    },
    args=["@brightdata/mcp"],
)

async def chat_with_agent():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_react_agent(model, tools)

            print(f"✅ Connected with {len(tools)} BrightData tools")
            print("🔍 You can now ask for real web scraping and data extraction!")
            print("Example: 'Extract specs for Amazon ASIN B07NJG12GB'")

            # Start conversation history
            messages = [
                {
                    "role": "system",
                    "content": "You have access to BrightData web scraping tools. Use them to fulfill user requests for web data extraction, scraping, and research. Always use the appropriate tool when asked to scrape or extract data from websites. Think step by step and use multiple tools if needed.",
                }
            ]

            print("\nType 'exit' or 'quit' to end the chat.")
            while True:
                user_input = input("\nYou: ")
                if user_input.strip().lower() in {"exit", "quit"}:
                    print("Goodbye!")
                    break

                # Add user message to history
                messages.append({"role": "user", "content": user_input})

                try:
                    # Call the agent with the full message history
                    agent_response = await agent.ainvoke({"messages": messages})

                    # Extract agent's reply and add to history
                    ai_message = agent_response["messages"][-1].content
                    print(f"Agent: {ai_message}")
                    messages.append({"role": "assistant", "content": ai_message})
                    
                except Exception as e:
                    print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(chat_with_agent())