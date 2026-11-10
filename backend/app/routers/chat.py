import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from app.config import settings
from app.schemas import ChatRequest
from app.context import build_context
from app.memory import save_message

router = APIRouter()

client = AsyncOpenAI(
    api_key=settings.openrouter_api_key,
    base_url=settings.openrouter_base_url,
)


@router.post("/chat")
async def chat(req: ChatRequest):
    await save_message(req.session_id, "user", req.message, tz=req.timezone)
    messages = await build_context(req.session_id, req.message, req.timezone)

    async def stream():
        full_response = ""
        async with client.chat.completions.stream(
            model=settings.openrouter_model,
            messages=messages,
        ) as s:
            async for chunk in s:
                token = chunk.choices[0].delta.content or ""
                if token:
                    full_response += token
                    yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

        await save_message(req.session_id, "assistant", full_response, tz=req.timezone)
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")
