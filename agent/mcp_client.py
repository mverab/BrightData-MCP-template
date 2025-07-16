import asyncio
import os
from typing import List, Dict, Any, Optional

class MCPClient:
    """Cliente MCP nativo usando stdio para comunicación con procesos externos."""
    def __init__(self, command: List[str], env: Optional[Dict[str, str]] = None):
        self.command = command
        self.env = env or os.environ.copy()
        # Asegura que el PATH correcto esté presente para encontrar 'npx'
        self.env["PATH"] = os.environ.get("PATH", "")
        self.process = None

    async def connect(self):
        """Lanza el proceso MCP y prepara la comunicación stdio."""
        print(f"[MCPClient] Lanzando proceso: {' '.join(self.command)}")
        print(f"[MCPClient] PATH usado: {self.env.get('PATH')}")
        try:
            self.process = await asyncio.create_subprocess_exec(
                *self.command,
                env=self.env,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            print("[MCPClient] Proceso MCP lanzado correctamente.")
            
            # Initialize MCP connection
            await self._initialize()
            
        except Exception as e:
            print(f"[MCPClient][ERROR] No se pudo lanzar el proceso MCP: {e}")
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
        """Envía una solicitud MCP usando el protocolo JSON-RPC."""
        import json
        if not self.process:
            raise RuntimeError("MCPClient no conectado. Llama connect() primero.")
        
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
            print(f"[MCPClient][ERROR] Timeout: El proceso MCP no respondió en 30 segundos para {method}.")
            try:
                err_output = await self.process.stderr.read()
                print(f"[MCPClient][STDERR] Salida de error del proceso MCP:\n{err_output.decode(errors='replace')}")
            except Exception as e:
                print(f"[MCPClient][STDERR] No se pudo leer el stderr: {e}")
            return None

        if not line:
            return None

        try:
            response = json.loads(line.decode())
            if "error" in response:
                raise Exception(f"Error en MCP {method}: {response['error']}")
            return response.get("result")
        except json.JSONDecodeError as e:
            print(f"[MCPClient][ERROR] Respuesta no válida de MCP: {line.decode()}")
            return None

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Llama una herramienta MCP."""
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
