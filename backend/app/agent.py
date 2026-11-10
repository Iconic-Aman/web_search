import asyncio
import json
from openai import AsyncOpenAI
from app.config import settings
from app.tools.web_search import run_search

client = AsyncOpenAI(
    api_key=settings.openrouter_api_key,
    base_url=settings.openrouter_base_url,
)

TOOL_SCHEMA = [{
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web for current or unknown facts. Do not use for greetings, math, or stable general knowledge.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Short, specific search query"}
            },
            "required": ["query"]
        }
    }
}]

MAX_ROUNDS = 2


async def run_agent(messages: list[dict]):
    """Async generator — yields token / source / done events."""
    sources = []

    for round_idx in range(MAX_ROUNDS):
        use_tools = round_idx == 0
        tc_map = {}
        finish_reason = None

        stream = await client.chat.completions.create(
            model=settings.openrouter_model,
            messages=messages,
            tools=TOOL_SCHEMA if use_tools else None,
            tool_choice="auto" if use_tools else None,
            stream=True,
        )

        async for chunk in stream:
            choice = chunk.choices[0]
            finish_reason = choice.finish_reason or finish_reason

            if choice.delta.content:
                yield {"type": "token", "content": choice.delta.content}

            for tc in (choice.delta.tool_calls or []):
                e = tc_map.setdefault(tc.index, {"id": "", "name": "", "arguments": ""})
                e["id"] = e["id"] or (tc.id or "")
                if tc.function:
                    e["name"] += tc.function.name or ""
                    e["arguments"] += tc.function.arguments or ""

        if finish_reason == "tool_calls" and tc_map:
            yield {"type": "status", "status": "searching"}
            messages.append({
                "role": "assistant", "content": None,
                "tool_calls": [
                    {"id": t["id"], "type": "function",
                     "function": {"name": t["name"], "arguments": t["arguments"]}}
                    for t in tc_map.values()
                ]
            })

            queries = []
            for t in tc_map.values():
                try:
                    queries.append(json.loads(t["arguments"]).get("query", ""))
                except json.JSONDecodeError:
                    queries.append("")

            results = await asyncio.gather(*[run_search(q) for q in queries], return_exceptions=True)

            for t, result in zip(tc_map.values(), results):
                if isinstance(result, list):
                    sources.extend(result)
                    content = json.dumps([r.model_dump() for r in result])
                else:
                    content = str(result)
                messages.append({"role": "tool", "tool_call_id": t["id"], "content": content})
            continue

        break

    for s in sources:
        yield {"type": "source", **s.model_dump()}
    yield {"type": "done"}
