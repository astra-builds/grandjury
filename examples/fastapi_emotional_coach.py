"""
FastAPI Emotional Support Coach — GrandJury integration demo.

Run:
  uvicorn examples.fastapi_emotional_coach:app --reload --port 8000

Requires:
  .env with GRANDJURY_API_KEY, OPENAI_API_KEY, OPENAI_API_BASE, MODEL
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
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

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    prompt = f"{SYSTEM_PROMPT}\n\nStudent's concern: {req.message}"
    response = llm.invoke(prompt)
    response_text = response.content if hasattr(response, "content") else str(response)
    
    inference_id = gj.trace(
        name="emotional-support-coach",
        input=req.message,
        output=response_text,
        model=os.environ["MODEL"],
    )
    
    if inference_id is None:
        print("⚠️ Trace submission failed - check GRANDJURY_API_KEY and network")
    else:
        print(f"✅ Trace submitted: {inference_id}")
    
    return ChatResponse(response=response_text, trace_id=inference_id)

@app.get("/health")
async def health():
    return {"status": "ok", "grandjury_connected": bool(gj._api_key)}