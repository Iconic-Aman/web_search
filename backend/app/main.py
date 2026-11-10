from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.db import run_migrations
from app.routers import chat, sessions
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Search Chat Agent")

app.include_router(chat.router)
app.include_router(sessions.router)


@app.on_event("startup")
async def startup():
    await run_migrations()


@app.get("/health")
async def health():
    return JSONResponse({"status": "ok"})
