import json
import asyncio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.schemas import ChatRequest
from app.context import build_context
from app.memory import save_message, maybe_summarise
from app.agent import run_agent

router = APIRouter()


@router.post("/chat")
async def chat(req: ChatRequest):
    await save_message(req.session_id, "user", req.message, tz=req.timezone)
    messages = await build_context(req.session_id, req.message, req.timezone)

    async def stream():
        full_response = ""
        all_sources = []
        async for event in run_agent(messages):
            if event["type"] == "token":
                full_response += event["content"]
            elif event["type"] == "source":
                all_sources.append({"title": event["title"], "url": event["url"]})
            yield f"data: {json.dumps(event)}\n\n"
        await save_message(req.session_id, "assistant", full_response, sources=all_sources, tz=req.timezone)
        asyncio.create_task(maybe_summarise(req.session_id))

    return StreamingResponse(stream(), media_type="text/event-stream")
