from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import asyncio
import os
import sys
import threading
import time
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

load_dotenv()

model = ChatOpenAI(model="gpt-4.1-2025-04-14", api_key=os.getenv("OPENAI_API_KEY"))

server_params = StdioServerParameters(
    command="npx",
    env={
        "API_TOKEN": os.getenv("API_TOKEN"),
        "BROWSER_AUTH": os.getenv("BROWSER_AUTH"),
        "WEB_UNLOCKER_ZONE": os.getenv("WEB_UNLOCKER_ZONE"),
    },
    args=["@brightdata/mcp"],
)

def loading_animation():
    """Show a loading animation"""
    chars = "|/-\\"
    idx = 0
    while not stop_loading:
        sys.stdout.write(f"\r{chars[idx % len(chars)]} Loading...")
        sys.stdout.flush()
        time.sleep(0.1)
        idx += 1
    sys.stdout.write("\r" + " " * 20 + "\r")
    sys.stdout.flush()

def start_loading():
    """Start loading animation in background"""
    global stop_loading
    stop_loading = False
    loading_thread = threading.Thread(target=loading_animation)
    loading_thread.daemon = True
    loading_thread.start()
    return loading_thread

def stop_loading_animation():
    """Stop loading animation"""
    global stop_loading
    stop_loading = True

async def chat_with_agent():
    # Redirect stderr to suppress BrightData verbose output
    original_stderr = sys.stderr
    sys.stderr = open(os.devnull, 'w')
    
    try:
        print("🚀 Starting BrightData Agent...")
        
        # Start loading animation
        loading_thread = start_loading()
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await load_mcp_tools(session)
                agent = create_react_agent(model, tools)

                # Stop loading animation
                stop_loading_animation()
                
                print(f"✅ Connected with {len(tools)} BrightData tools")
                print("🔍 Ready for web scraping and data extraction!")
                print("💡 Examples:")
                print("  - Extract specs for Amazon ASIN B07NJG12GB")
                print("  - Scrape product data from amazon.mx")
                print("  - Get LinkedIn company info")
                print("  - Search Google for monitors")

                # Start conversation history
                messages = [
                    {
                        "role": "system",
                        "content": "You have access to BrightData web scraping tools. Use them to fulfill user requests for web data extraction, scraping, and research. Always use the appropriate tool when asked to scrape or extract data from websites. Think step by step and use multiple tools if needed. Be concise and helpful.",
                    }
                ]

                print("\n" + "="*50)
                print("Type 'exit' or 'quit' to end the chat.")
                print("="*50)
                
                while True:
                    try:
                        user_input = input("\n🔍 You: ")
                        if user_input.strip().lower() in {"exit", "quit"}:
                            print("👋 Goodbye!")
                            break

                        if not user_input.strip():
                            print("💬 Please enter a command or question.")
                            continue

                        # Add user message to history
                        messages.append({"role": "user", "content": user_input})

                        # Show processing indicator
                        print("🤖 Processing", end="", flush=True)
                        dots = 0
                        
                        # Call the agent with the full message history
                        agent_response = await agent.ainvoke({"messages": messages})

                        # Clear processing indicator
                        print("\r" + " " * 20 + "\r", end="", flush=True)

                        # Extract agent's reply and add to history
                        ai_message = agent_response["messages"][-1].content
                        print(f"🤖 Agent: {ai_message}")
                        messages.append({"role": "assistant", "content": ai_message})
                        
                    except KeyboardInterrupt:
                        print("\n\n👋 Goodbye!")
                        break
                    except Exception as e:
                        print(f"\n❌ Error: Something went wrong. Please try again.")
                        # Only show actual error in debug mode
                        if os.getenv("DEBUG") == "1":
                            print(f"Debug: {e}")
                            
    finally:
        # Restore stderr
        sys.stderr.close()
        sys.stderr = original_stderr

if __name__ == "__main__":
    asyncio.run(chat_with_agent())