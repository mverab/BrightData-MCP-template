import asyncio
import os
from typing import List, Dict, Any, Optional

class MCPClient:
    """Native MCP client using stdio for communication with external processes."""
    def __init__(self, command: List[str], env: Optional[Dict[str, str]] = None):
        self.command = command
        self.env = env or os.environ.copy()
        # make sure PATH is set to find npx
        self.env["PATH"] = os.environ.get("PATH", "")
        self.process = None

    async def connect(self):
        """Launch the mcp process and prepare stdio communication."""
        print(f"[MCPClient] Launching process: {' '.join(self.command)}")
        print(f"[MCPClient] PATH used: {self.env.get('PATH')}")
        try:
            self.process = await asyncio.create_subprocess_exec(
                *self.command,
                env=self.env,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            print("[MCPClient] mcp process started successfully.")
            
            # Initialize MCP connection
            await self._initialize()
            
        except Exception as e:
            print(f"[MCPClient][ERROR] mcp process failed to start: {e}")
            raise
    
    async def _initialize(self):
        """Initialize MCP protocol"""
        import json
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "brightdata-client", "version": "1.0.0"}
            }
        }
        
        payload = json.dumps(init_request) + "\n"
        self.process.stdin.write(payload.encode())
        await self.process.stdin.drain()
        
        # Read initialize response
        try:
            line = await asyncio.wait_for(self.process.stdout.readline(), timeout=10.0)
            if line:
                response = json.loads(line.decode())
                if "error" in response:
                    raise Exception(f"MCP Initialize error: {response['error']}")
        except Exception as e:
            print(f"[MCPClient] Initialize failed: {e}")
            raise

    async def send_mcp_request(self, method: str, params: Dict[str, Any] = None) -> Any:
        """Send an MCP request using the JSON-RPC protocol."""
        import json
        if not self.process:
            raise RuntimeError("MCPClient not connected. Call connect() first.")
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        
        payload = json.dumps(request) + "\n"
        self.process.stdin.write(payload.encode())
        await self.process.stdin.drain()
        
        try:
            line = await asyncio.wait_for(self.process.stdout.readline(), timeout=30.0)
        except asyncio.TimeoutError:
            print(f"[MCPClient][ERROR] Timeout: mcp process did not respond in 30 seconds for {method}.")
            try:
                err_output = await self.process.stderr.read()
                print(f"[MCPClient][STDERR] mcp process error output:\n{err_output.decode(errors='replace')}")
            except Exception as e:
                print(f"[MCPClient][STDERR] could not read stderr: {e}")
            return None

        if not line:
            return None

        try:
            response = json.loads(line.decode())
            if "error" in response:
                raise Exception(f"mcp error in {method}: {response['error']}")
            return response.get("result")
        except json.JSONDecodeError as e:
            print(f"[MCPClient][ERROR] invalid mcp response: {line.decode()}")
            return None

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Call an mcp tool."""
        return await self.send_mcp_request("tools/call", {
            "name": name,
            "arguments": arguments
        })

    async def list_tools(self) -> List[Dict[str, Any]]:
        """Lista las herramientas disponibles del servidor MCP."""
        result = await self.send_mcp_request("tools/list", {})
        if result and "tools" in result:
            return result["tools"]
        return result or []

    async def close(self):
        if self.process:
            self.process.terminate()
            await self.process.wait()
