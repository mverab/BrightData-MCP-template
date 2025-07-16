from pydantic import BaseModel
from typing import Optional, Dict, Any, List, Callable
import asyncio
import json

class ToolInput(BaseModel):
    name: str
    parameters: Optional[Dict[str, Any]] = None

class ToolOutput(BaseModel):
    name: str
    result: Any
    success: bool = True
    error: Optional[str] = None

class AgentStep(BaseModel):
    input: ToolInput
    output: Optional[ToolOutput] = None
    metadata: Optional[Dict[str, Any]] = None

class AgentSession(BaseModel):
    steps: list[AgentStep]
    session_id: Optional[str] = None
    status: Optional[str] = None

class BrightDataTool(BaseModel):
    """Base model for BrightData tools"""
    name: str
    description: str
    parameters: Dict[str, Any]
    executor: Optional[Callable[..., Any]] = None

    async def execute(self, **kwargs) -> Any:
        if self.executor:
            if asyncio.iscoroutinefunction(self.executor):
                return await self.executor(**kwargs)
            else:
                return self.executor(**kwargs)
        raise NotImplementedError("No executor defined for this tool.")

class OpenAIAgent:
    """Main agent with OpenAI and BrightData tools"""
    def __init__(self, model: str, tools: List[BrightDataTool]):
        from llm.openai_client import OpenAIClient
        self.client = OpenAIClient(model=model)
        self.tools = {tool.name: tool for tool in tools}

    async def chat(self, messages: List[Dict[str, Any]]) -> str:
        """Convert tools to OpenAI function format"""
        functions = []
        for tool in self.tools.values():
            functions.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": tool.parameters,
                        "required": list(tool.parameters.keys()) if tool.parameters else []
                    }
                }
            })
        
        # Call OpenAI with function calling enabled
        response = await self.client.chat(messages, tools=functions)
        
        # Check if OpenAI wants to call a function
        if response.tool_calls:
            # Execute the tool calls
            for tool_call in response.tool_calls:
                tool_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                try:
                    result = await self.call_tool(tool_name, **arguments)
                    # Add tool result to conversation
                    messages.append({
                        "role": "assistant", 
                        "content": None,
                        "tool_calls": [tool_call]
                    })
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result)
                    })
                except Exception as e:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": f"Error: {str(e)}"
                    })
            
            # Get final response from OpenAI with tool results
            final_response = await self.client.chat(messages)
            return final_response.messages[-1].content
        
        return response.messages[-1].content

    async def call_tool(self, tool_name: str, **kwargs) -> Any:
        tool = self.tools.get(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found.")
        return await tool.execute(**kwargs)
