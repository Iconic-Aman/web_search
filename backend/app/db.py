import aiosqlite
import os

DB_PATH = os.getenv("DATABASE_URL", "./chat.db")

CREATE_SESSIONS = """
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    summary TEXT DEFAULT '',
    timezone TEXT DEFAULT 'UTC',
    created_at DATETIME DEFAULT (datetime('now')),
    updated_at DATETIME DEFAULT (datetime('now'))
)"""

CREATE_MESSAGES = """
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT REFERENCES sessions(id),
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    sources TEXT DEFAULT '[]',
    created_at DATETIME DEFAULT (datetime('now'))
)"""

CREATE_SEARCH_CACHE = """
CREATE TABLE IF NOT EXISTS search_cache (
    query TEXT PRIMARY KEY,
    results TEXT NOT NULL,
    fetched_at DATETIME DEFAULT (datetime('now'))
)"""


async def get_db():
    return await aiosqlite.connect(DB_PATH)


async def run_migrations():
    async with await get_db() as db:
        await db.execute(CREATE_SESSIONS)
        await db.execute(CREATE_MESSAGES)
        await db.execute(CREATE_SEARCH_CACHE)
        await db.commit()
