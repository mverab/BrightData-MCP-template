import os
from openai import AsyncOpenAI
from pydantic import BaseModel
from typing import List, Optional

class Message(BaseModel):
    role: str
    content: str

class CompletionResult(BaseModel):
    messages: List[Message]
    usage: Optional[dict] = None
    model: Optional[str] = None
    tool_calls: Optional[List] = None

class OpenAIClient:
    def __init__(self, model: str = "gpt-4.1-2025-04-14"):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def chat(self, messages: List[dict], stream: bool = False, tools: List[dict] = None) -> CompletionResult:
        kwargs = {
            "model": self.model,
            "messages": messages,
            "stream": stream
        }
        if tools:
            kwargs["tools"] = tools
            
        response = await self.client.chat.completions.create(**kwargs)
        
        # Si stream=True, response es un generador async
        if stream:
            collected = []
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    collected.append(chunk.choices[0].delta.content)
            content = ''.join(collected)
            return CompletionResult(messages=[Message(role="assistant", content=content)])
        else:
            message = response.choices[0].message
            content = message.content
            tool_calls = message.tool_calls if hasattr(message, 'tool_calls') else None
            
            return CompletionResult(
                messages=[Message(role="assistant", content=content or "")],
                usage=response.usage.dict() if response.usage else None,
                model=response.model,
                tool_calls=tool_calls
            )
