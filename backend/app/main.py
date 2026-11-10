from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
from app.db import run_migrations
from app.routers import chat, sessions
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Search Chat Agent")

app.include_router(chat.router)
app.include_router(sessions.router)

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")


@app.on_event("startup")
async def startup():
    await run_migrations()


@app.get("/health")
async def health():
    return JSONResponse({"status": "ok"})
