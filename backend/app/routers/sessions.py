import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.schemas import MessageOut
from app.memory import load_all_messages, delete_session

router = APIRouter()


@router.get("/sessions/{session_id}/messages", response_model=list[MessageOut])
async def get_messages(session_id: str):
    rows = await load_all_messages(session_id)
    if not rows:
        raise HTTPException(status_code=404, detail="Session not found")
    return [MessageOut(**{**r, "sources": json.loads(r["sources"] or "[]")}) for r in rows]


@router.delete("/sessions/{session_id}")
async def remove_session(session_id: str):
    await delete_session(session_id)
    return JSONResponse({"status": "deleted"})
