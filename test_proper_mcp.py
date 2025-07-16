from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()

server_params = StdioServerParameters(
    command="npx",
    env={
        "API_TOKEN": os.getenv("API_TOKEN"),
        "BROWSER_AUTH": os.getenv("BROWSER_AUTH"),
        "WEB_UNLOCKER_ZONE": os.getenv("WEB_UNLOCKER_ZONE"),
    },
    args=["@brightdata/mcp"],
)

async def test_brightdata_proper():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            
            print(f"✓ Connected with {len(tools)} tools")
            
            # Find Amazon product tool
            amazon_tool = None
            for tool in tools:
                if "amazon_product" in tool.name and "web_data" in tool.name:
                    amazon_tool = tool
                    break
            
            if not amazon_tool:
                print("❌ Amazon product tool not found")
                return
            
            print(f"✓ Found tool: {amazon_tool.name}")
            
            # Test with the ASIN
            test_url = "https://www.amazon.com.mx/K-VISION-Pantalla-LED-Marca-KV3210/dp/B07NJG12GB?th=1&psc=1"
            
            print(f"\n🔍 Testing with URL: {test_url}")
            
            try:
                result = await amazon_tool.ainvoke({"url": test_url})
                
                if result:
                    print("✅ SUCCESS! Got product data:")
                    print(f"Data type: {type(result)}")
                    
                    if isinstance(result, str):
                        # Parse if it's JSON string
                        import json
                        try:
                            data = json.loads(result)
                            print(f"Title: {data.get('title', 'N/A')}")
                            print(f"Brand: {data.get('brand', 'N/A')}")
                            print(f"Price: {data.get('final_price', 'N/A')} {data.get('currency', '')}")
                            print(f"ASIN: {data.get('asin', 'N/A')}")
                        except:
                            print(f"Raw result: {result[:500]}...")
                    else:
                        print(f"Result: {result}")
                else:
                    print("❌ Tool returned None/empty")
                    
            except Exception as e:
                print(f"❌ Error calling tool: {e}")

if __name__ == "__main__":
    asyncio.run(test_brightdata_proper())