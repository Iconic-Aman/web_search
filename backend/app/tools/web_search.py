import asyncio
import json
from datetime import datetime, timezone, timedelta
from tavily import AsyncTavilyClient
from app.config import settings
from app.schemas import SearchResult
from app.db import get_db

_client = AsyncTavilyClient(api_key=settings.tavily_api_key)
CACHE_TTL = timedelta(minutes=10)
SNIPPET_MAX = 400


async def _get_cache(query: str) -> list[SearchResult] | None:
    async with await get_db() as db:
        async with db.execute(
            "SELECT results, fetched_at FROM search_cache WHERE query = ?", (query,)
        ) as cur:
            row = await cur.fetchone()
    if not row:
        return None
    fetched_at = datetime.fromisoformat(row[1]).replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) - fetched_at > CACHE_TTL:
        return None
    return [SearchResult(**r) for r in json.loads(row[0])]


async def _set_cache(query: str, results: list[SearchResult]):
    async with await get_db() as db:
        await db.execute(
            "INSERT OR REPLACE INTO search_cache (query, results, fetched_at) VALUES (?, ?, datetime('now'))",
            (query, json.dumps([r.model_dump() for r in results]))
        )
        await db.commit()


async def run_search(query: str) -> list[SearchResult] | str:
    q = query.lower().strip()
    cached = await _get_cache(q)
    if cached:
        return cached
    try:
        resp = await asyncio.wait_for(_client.search(q, max_results=5), timeout=4)
        results = [
            SearchResult(
                title=r["title"],
                url=r["url"],
                snippet=r.get("content", "")[:SNIPPET_MAX]
            )
            for r in resp.get("results", [])
        ]
        await _set_cache(q, results)
        return results
    except Exception as e:
        return f"Search failed: {str(e)}"
