import asyncio
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def debug_mcp():
    process = await asyncio.create_subprocess_exec(
        "npx", "@brightdata/mcp",
        env={
            "API_TOKEN": os.getenv("API_TOKEN"),
            "WEB_UNLOCKER_ZONE": os.getenv("WEB_UNLOCKER_ZONE"),
            "BROWSER_ZONE": "brd-customer-hl_ab73365a-zone-web_scraping_1:saza0h5zptxv@brd.superproxy.io:9222"
        },
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    # Send initialize request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0.0"}
        }
    }
    
    payload = json.dumps(init_request) + "\n"
    process.stdin.write(payload.encode())
    await process.stdin.drain()
    
    # Read response
    try:
        line = await asyncio.wait_for(process.stdout.readline(), timeout=10.0)
        if line:
            response = json.loads(line.decode())
            print(f"Initialize response: {response}")
            
            # Now try to list tools
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            }
            
            payload = json.dumps(tools_request) + "\n"
            process.stdin.write(payload.encode())
            await process.stdin.drain()
            
            line = await asyncio.wait_for(process.stdout.readline(), timeout=10.0)
            if line:
                response = json.loads(line.decode())
                print(f"Tools list response: {response}")
                
                if "result" in response and "tools" in response["result"]:
                    tools = response["result"]["tools"]
                    print(f"Found {len(tools)} tools")
                    
                    # Try to call web_data_amazon_product
                    tool_request = {
                        "jsonrpc": "2.0",
                        "id": 3,
                        "method": "tools/call",
                        "params": {
                            "name": "web_data_amazon_product",
                            "arguments": {
                                "url": "https://www.amazon.com.mx/dp/B07NJG12GB"
                            }
                        }
                    }
                    
                    payload = json.dumps(tool_request) + "\n"
                    process.stdin.write(payload.encode())
                    await process.stdin.drain()
                    
                    line = await asyncio.wait_for(process.stdout.readline(), timeout=30.0)
                    if line:
                        response = json.loads(line.decode())
                        print(f"Amazon tool response: {response}")
                    
    except Exception as e:
        print(f"Error: {e}")
        stderr = await process.stderr.read()
        print(f"Stderr: {stderr.decode()}")
    
    process.terminate()
    await process.wait()

if __name__ == "__main__":
    asyncio.run(debug_mcp())