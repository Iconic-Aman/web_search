import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from openai import AsyncOpenAI
from app.db import run_migrations
from app.config import settings
from app.schemas import ChatRequest, MessageOut
from app.context import build_context
from app.memory import save_message, load_all_messages, delete_session
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Search Chat Agent")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

client = AsyncOpenAI(
    api_key=settings.openrouter_api_key,
    base_url=settings.openrouter_base_url,
)


@app.on_event("startup")
async def startup():
    await run_migrations()


@app.get("/health")
async def health():
    return JSONResponse({"status": "ok"})


@app.post("/chat")
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


@app.get("/sessions/{session_id}/messages", response_model=list[MessageOut])
async def get_messages(session_id: str):
    rows = await load_all_messages(session_id)
    if not rows:
        raise HTTPException(status_code=404, detail="Session not found")
    return [MessageOut(**{**r, "sources": json.loads(r["sources"] or "[]")}) for r in rows]


@app.delete("/sessions/{session_id}")
async def remove_session(session_id: str):
    await delete_session(session_id)
    return JSONResponse({"status": "deleted"})
