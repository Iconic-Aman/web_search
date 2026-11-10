from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.db import run_migrations
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Search Chat Agent")


@app.on_event("startup")
async def startup():
    await run_migrations()


@app.get("/health")
async def health():
    return JSONResponse({"status": "ok"})
