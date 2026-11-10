import json
from openai import AsyncOpenAI
from app.db import get_db
from app.config import settings

RECENT_LIMIT = 10
SUMMARY_THRESHOLD = 20  # summarise when total messages exceed this

_llm = AsyncOpenAI(api_key=settings.openrouter_api_key, base_url=settings.openrouter_base_url)


async def save_message(session_id: str, role: str, content: str, sources: list = [], tz: str = "UTC"):
    async with await get_db() as db:
        await db.execute(
            "INSERT OR IGNORE INTO sessions (id, timezone) VALUES (?, ?)",
            (session_id, tz)
        )
        await db.execute(
            "INSERT INTO messages (session_id, role, content, sources) VALUES (?, ?, ?, ?)",
            (session_id, role, content, json.dumps(sources))
        )
        await db.execute(
            "UPDATE sessions SET updated_at = datetime('now') WHERE id = ?",
            (session_id,)
        )
        await db.commit()


async def load_recent(session_id: str) -> list[dict]:
    async with await get_db() as db:
        db.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
        async with db.execute(
            "SELECT role, content, sources, created_at FROM messages "
            "WHERE session_id = ? ORDER BY id DESC LIMIT ?",
            (session_id, RECENT_LIMIT)
        ) as cur:
            rows = await cur.fetchall()
    return list(reversed(rows))


async def load_question_log(session_id: str) -> list[dict]:
    async with await get_db() as db:
        db.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
        async with db.execute(
            "SELECT content, created_at FROM messages WHERE session_id = ? AND role = 'user' ORDER BY id",
            (session_id,)
        ) as cur:
            return await cur.fetchall()


async def load_summary(session_id: str) -> str:
    async with await get_db() as db:
        async with db.execute(
            "SELECT summary FROM sessions WHERE id = ?", (session_id,)
        ) as cur:
            row = await cur.fetchone()
    return row[0] if row else ""


async def load_all_messages(session_id: str) -> list[dict]:
    async with await get_db() as db:
        db.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
        async with db.execute(
            "SELECT id, session_id, role, content, sources, created_at FROM messages "
            "WHERE session_id = ? ORDER BY id",
            (session_id,)
        ) as cur:
            return await cur.fetchall()


async def delete_session(session_id: str):
    async with await get_db() as db:
        await db.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        await db.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        await db.commit()


async def maybe_summarise(session_id: str):
    """Summarise older turns if total messages exceed threshold. Runs off critical path."""
    rows = await load_all_messages(session_id)
    if len(rows) <= SUMMARY_THRESHOLD:
        return
    to_summarise = rows[:-RECENT_LIMIT]
    text = "\n".join(f"{r['role']}: {r['content']}" for r in to_summarise)
    resp = await _llm.chat.completions.create(
        model=settings.openrouter_model,
        messages=[
            {"role": "system", "content": "Summarise this conversation in 3-4 sentences."},
            {"role": "user", "content": text}
        ]
    )
    summary = resp.choices[0].message.content or ""
    async with await get_db() as db:
        await db.execute("UPDATE sessions SET summary = ? WHERE id = ?", (summary, session_id))
        await db.commit()

