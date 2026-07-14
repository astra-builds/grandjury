"""
FastAPI Emotional Support Coach — GrandJury integration demo.

Run:
  uvicorn examples.fastapi_emotional_coach:app --reload --port 8000

Requires:
  .env with GRANDJURY_API_KEY, OPENAI_API_KEY, OPENAI_API_BASE, MODEL
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
import uuid
import time
from typing import List, Optional
from langchain_openai import ChatOpenAI
from grandjury import GrandJury

load_dotenv()

app = FastAPI(title="Emotional Support Coach API")

gj = GrandJury()
llm = ChatOpenAI(
    model=os.environ["MODEL"],
    openai_api_key=os.environ.get("OPENAI_API_KEY"),
    openai_api_base=os.environ.get("OPENAI_API_BASE"),
    temperature=0.7,
)

SYSTEM_PROMPT = """You are a compassionate emotional support coach for students.
Respond with empathy, validate their feelings, and offer practical suggestions.
Never give medical advice. Keep responses warm and supportive."""


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    trace_id: str | None = None


# OpenAI-compatible models for benchmark enrollment
class OpenAIMessage(BaseModel):
    role: str
    content: str


class OpenAIChatRequest(BaseModel):
    model: str
    messages: List[OpenAIMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False


class OpenAIChatChoice(BaseModel):
    index: int
    message: OpenAIMessage
    finish_reason: str = "stop"


class OpenAIChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[OpenAIChatChoice]
    usage: dict = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}


async def generate_response(prompt: str, model_name: str) -> tuple[str, str | None]:
    """Returns (response_text, trace_id)"""
    full_prompt = f"{SYSTEM_PROMPT}\n\nStudent's concern: {prompt}"
    response = llm.invoke(full_prompt)
    response_text = response.content if hasattr(response, "content") else str(response)

    trace_id = gj.trace(
        name="emotional-support-coach",
        input=prompt,
        output=response_text,
        model=model_name,
    )
    if trace_id is None:
        print("⚠️ Trace submission failed - check GRANDJURY_API_KEY and network")
    else:
        print(f"✅ Trace submitted: {trace_id}")

    return response_text, trace_id


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    response_text, trace_id = await generate_response(req.message, os.environ["MODEL"])
    return ChatResponse(response=response_text, trace_id=trace_id)


@app.post("/v1/chat/completions", response_model=OpenAIChatResponse)
async def openai_chat_completions(req: OpenAIChatRequest):
    # Extract last user message as prompt
    user_messages = [m for m in req.messages if m.role == "user"]
    if not user_messages:
        raise HTTPException(400, "No user message found")
    prompt = user_messages[-1].content

    # Generate response (reuses tracing)
    response_text, _ = await generate_response(prompt, req.model)

    # Return OpenAI format
    return OpenAIChatResponse(
        id=f"chatcmpl-{uuid.uuid4().hex[:8]}",
        created=int(time.time()),
        model=req.model,
        choices=[OpenAIChatChoice(
            index=0,
            message=OpenAIMessage(role="assistant", content=response_text),
            finish_reason="stop"
        )],
        usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    )


@app.get("/health")
async def health():
    return {"status": "ok", "grandjury_connected": bool(gj._api_key)}