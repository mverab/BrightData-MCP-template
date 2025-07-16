import asyncio
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def debug_brightdata_detailed():
    """Comprehensive debugging of BrightData MCP server"""
    
    print("=== BrightData MCP Debug Session ===")
    print(f"API_TOKEN: {'SET' if os.getenv('API_TOKEN') else 'MISSING'}")
    print(f"WEB_UNLOCKER_ZONE: {os.getenv('WEB_UNLOCKER_ZONE')}")
    
    env = {
        "API_TOKEN": os.getenv("API_TOKEN"),
        "WEB_UNLOCKER_ZONE": os.getenv("WEB_UNLOCKER_ZONE"),
        "BROWSER_ZONE": "brd-customer-hl_ab73365a-zone-web_scraping_1:saza0h5zptxv@brd.superproxy.io:9222"
    }
    
    process = await asyncio.create_subprocess_exec(
        "npx", "@brightdata/mcp",
        env=env,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    request_id = 1
    
    async def send_request(method, params=None):
        nonlocal request_id
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method
        }
        if params:
            request["params"] = params
            
        payload = json.dumps(request) + "\n"
        print(f"\n>>> Sending: {method}")
        print(f"    Request: {json.dumps(request, indent=2)}")
        
        process.stdin.write(payload.encode())
        await process.stdin.drain()
        
        try:
            line = await asyncio.wait_for(process.stdout.readline(), timeout=30.0)
            if line:
                response = json.loads(line.decode())
                print(f"<<< Response: {json.dumps(response, indent=2)}")
                request_id += 1
                return response
            else:
                print("<<< No response received")
                return None
        except asyncio.TimeoutError:
            print("<<< TIMEOUT - No response in 30 seconds")
            stderr = await process.stderr.read()
            if stderr:
                print(f"STDERR: {stderr.decode()}")
            return None
        except Exception as e:
            print(f"<<< ERROR: {e}")
            return None
    
    try:
        # 1. Initialize
        init_response = await send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "debug-client", "version": "1.0.0"}
        })
        
        if not init_response or "error" in init_response:
            print("FAILED: Initialize failed")
            return
        
        # 2. List tools
        tools_response = await send_request("tools/list")
        if not tools_response or "error" in tools_response:
            print("FAILED: Cannot list tools")
            return
            
        tools = tools_response.get("result", {}).get("tools", [])
        print(f"\n=== Found {len(tools)} tools ===")
        for tool in tools[:5]:  # Show first 5
            print(f"- {tool['name']}: {tool.get('description', 'No description')[:100]}")
        
        # 3. Test session_stats first (simple tool)
        stats_response = await send_request("tools/call", {
            "name": "session_stats",
            "arguments": {}
        })
        
        # 4. Test Amazon product extraction with detailed debugging
        amazon_urls = [
            "https://www.amazon.com.mx/dp/B07NJG12GB",
            "https://www.amazon.com.mx/K-VISION-Pantalla-LED-Marca-KV3210/dp/B07NJG12GB",
            "https://www.amazon.com.mx/K-VISION-Pantalla-LED-Marca-KV3210/dp/B07NJG12GB?th=1&psc=1"
        ]
        
        for url in amazon_urls:
            print(f"\n=== Testing Amazon URL: {url} ===")
            amazon_response = await send_request("tools/call", {
                "name": "web_data_amazon_product",
                "arguments": {"url": url}
            })
            
            if amazon_response and "result" in amazon_response:
                result = amazon_response["result"]
                if result:
                    print(f"SUCCESS: Got data for {url}")
                    if isinstance(result, dict):
                        print(f"  Title: {result.get('title', 'N/A')}")
                        print(f"  Price: {result.get('final_price', 'N/A')}")
                        print(f"  Brand: {result.get('brand', 'N/A')}")
                    break
                else:
                    print(f"EMPTY: Tool returned None/empty for {url}")
            else:
                print(f"FAILED: No result for {url}")
        
        # 5. Test general scraping as fallback
        print(f"\n=== Testing scrape_as_markdown as fallback ===")
        scrape_response = await send_request("tools/call", {
            "name": "scrape_as_markdown",
            "arguments": {"url": "https://www.amazon.com.mx/dp/B07NJG12GB"}
        })
        
        if scrape_response and "result" in scrape_response:
            result = scrape_response["result"]
            if result:
                content = str(result)[:500] + "..." if len(str(result)) > 500 else str(result)
                print(f"SCRAPE SUCCESS: {content}")
            else:
                print("SCRAPE EMPTY: Returned None")
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        process.terminate()
        await process.wait()

if __name__ == "__main__":
    asyncio.run(debug_brightdata_detailed())