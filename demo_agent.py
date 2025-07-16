import asyncio
import os
from dotenv import load_dotenv
from models.schemas import BrightDataTool, OpenAIAgent
from agent.mcp_client import MCPClient

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
BROWSER_AUTH = os.getenv("BROWSER_AUTH")
WEB_UNLOCKER_ZONE = os.getenv("WEB_UNLOCKER_ZONE")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-2025-04-14")

async def sumar(a: int, b: int) -> int:
    return a + b

async def main():
    # Inicializa cliente MCP (puedes comentar si no tienes MCP corriendo)
    try:
        mcp = MCPClient(
            command=["npx", "@brightdata/mcp"],
            env={
                "API_TOKEN": API_TOKEN,
                "WEB_UNLOCKER_ZONE": WEB_UNLOCKER_ZONE,
                "BROWSER_ZONE": "brd-customer-hl_ab73365a-zone-web_scraping_1:saza0h5zptxv@brd.superproxy.io:9222"
            }
        )
        await mcp.connect()
        tools_info = await mcp.list_tools()
        print(f"[DEBUG] tools_info recibido: {tools_info}")
        if tools_info:
            print(f"Herramientas MCP detectadas: {[t['name'] for t in tools_info]}")
        else:
            print("[WARN] MCP conectado pero no se detectaron herramientas. Verifica tu API_TOKEN y permisos en BrightData.")
    except Exception as e:
        print(f"[WARN] MCP no disponible: {e}")
        # Imprime el stderr del proceso MCP si existe
        if mcp and hasattr(mcp, 'process') and mcp.process and mcp.process.stderr:
            try:
                err = await mcp.process.stderr.read()
                print(f"[MCPClient][STDERR]: {err.decode(errors='replace')}")
            except Exception as ex:
                print(f"[MCPClient][STDERR] Error al leer stderr: {ex}")
        mcp = None

    # Herramienta nativa
    suma_tool = BrightDataTool(
        name="sumar",
        description="Suma dos números",
        parameters={"a": int, "b": int},
        executor=sumar
    )

    brightdata_tools = [suma_tool]

    if mcp:
        try:
            for tool in tools_info:
                brightdata_tools.append(
                    BrightDataTool(
                        name=tool["name"],
                        description=tool.get("description", ""),
                        parameters=tool.get("parameters", {}),
                        executor=lambda **kwargs: mcp.call_tool(tool["name"], kwargs),
                    )
                )
        except Exception as e:
            print(f"[WARN] No se pudieron registrar herramientas MCP: {e}")

    # Inicializa agente con todas las herramientas
    agent = OpenAIAgent(model=OPENAI_MODEL, tools=brightdata_tools)

    # Ejemplo de uso: sumar
    print("--- Ejemplo: sumar 2 + 3 ---")
    suma_result = await agent.call_tool("sumar", a=2, b=3)
    print(f"Resultado sumar: {suma_result}")

    # Ejemplo de uso: MCP echo (solo si está registrada)
    if any(t.name == "echo" for t in brightdata_tools):
        print("--- Ejemplo: MCP echo ---")
        mcp_result = await agent.call_tool("echo", text="Hola desde MCP")
        print(f"Resultado MCP echo: {mcp_result}")
    else:
        print("--- Ejemplo: MCP echo ---")
        print("Herramienta 'echo' no disponible (MCP no detectado o sin herramientas registradas).")

    # Ejemplo de chat
    print("--- Ejemplo: Chat con OpenAI ---")
    messages = [
        {"role": "system", "content": "Eres un asistente que puede usar herramientas."},
        {"role": "user", "content": "Dime un saludo y luego suma 4+5."}
    ]
    respuesta = await agent.chat(messages)
    print(f"Respuesta OpenAI: {respuesta}")

    if mcp:
        await mcp.close()

if __name__ == "__main__":
    asyncio.run(main())
