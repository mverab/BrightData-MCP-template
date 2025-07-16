import asyncio
import json
import os
import time

# Adjust this command to use local install if present, else fallback to npx
PRIMARY_COMMAND = ["./node_modules/.bin/mcp"]
FALLBACK_COMMAND = ["npx", "@brightdata/mcp"]

TIMEOUT = 15.0  # seconds

async def run_subprocess(cmd, env):
    print(f"[DEBUG] Launching: {' '.join(cmd)}")
    start = time.perf_counter()
    
    # Buffer para capturar stderr
    stderr_buffer = []
    
    async def read_stderr(stream):
        while True:
            line = await stream.readline()
            if not line:
                break
            line_str = line.decode(errors='replace').strip()
            print(f"[STDERR] {line_str}")
            stderr_buffer.append(line_str)
    
    process = await asyncio.create_subprocess_exec(
        *cmd,
        env=env,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    
    # Iniciar la tarea de lectura de stderr
    stderr_task = asyncio.create_task(read_stderr(process.stderr))
    try:
        # Send a simple list_tools request using JSON-RPC 2.0 format
        # Try 'list-tools' (kebab-case method name)
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "list-tools",
            "params": {}
        }
        payload = (json.dumps(request) + '\n').encode()
        print(f"[DEBUG] Sending: {payload.decode().strip()}")
        process.stdin.write(payload)
        await process.stdin.drain()
        print("[DEBUG] Waiting for response...")
        line = await asyncio.wait_for(process.stdout.readline(), timeout=TIMEOUT)
        if not line:
            print("[ERROR] No response. stdout empty.")
        else:
            print("[INFO] MCP response:", line.decode().strip()[:500])
    except asyncio.TimeoutError:
        print(f"[ERROR] Timeout after {TIMEOUT}s waiting for response.")
        err_out = await process.stderr.read()
        if err_out:
            print("[STDERR]", err_out.decode(errors="replace"))
    finally:
        # Cancelar la tarea de stderr
        if 'stderr_task' in locals():
            stderr_task.cancel()
            try:
                await stderr_task
            except asyncio.CancelledError:
                pass
                
        process.kill()
        await process.wait()
        print(f"[DEBUG] Elapsed {time.perf_counter() - start:.1f}s")
        
        # Mostrar stderr al final si hubo error
        if stderr_buffer:
            print("\n[ERROR] Stderr output:")
            for line in stderr_buffer:
                print(f"  {line}")

async def main():
    # Load env from existing .env if present
    from dotenv import load_dotenv

    load_dotenv()
    env = os.environ.copy()

    required = ["API_TOKEN", "WEB_UNLOCKER_ZONE", "BROWSER_ZONE"]
    missing = [k for k in required if not env.get(k)]
    if missing:
        print("[WARN] Missing env vars: ", ', '.join(missing))
    else:
        print("[INFO] All required env vars found.")
    print("[DEBUG] Env vars:", {k: '***' if 'TOKEN' in k else v for k, v in env.items() if k in required})

    # Try primary command first
    if os.path.exists(PRIMARY_COMMAND[0]):
        await run_subprocess(PRIMARY_COMMAND, env)
    else:
        print("[INFO] Local MCP binary not found, trying npx ...")
        await run_subprocess(FALLBACK_COMMAND, env)

if __name__ == "__main__":
    asyncio.run(main())
