import asyncio
import time
import uuid
import yaml
import httpx
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"
QUESTIONS_FILE = Path(__file__).parent / "questions.yaml"
TIMEOUT = 30


async def run_question(client: httpx.AsyncClient, session_id: str, question: str) -> dict:
    t_start = time.monotonic()
    t_first_token = None
    tokens = []
    sources = []

    async with client.stream(
        "POST", f"{BASE_URL}/chat",
        json={"session_id": session_id, "message": question, "timezone": "UTC"},
        timeout=TIMEOUT
    ) as resp:
        async for line in resp.aiter_lines():
            if not line.startswith("data: "):
                continue
            ev = json.loads(line[6:])
            if ev["type"] == "token":
                if t_first_token is None:
                    t_first_token = time.monotonic() - t_start
                tokens.append(ev["content"])
            elif ev["type"] == "source":
                sources.append(ev["url"])

    return {
        "answer": "".join(tokens),
        "sources": sources,
        "ttft": round(t_first_token or 0, 3),
        "total": round(time.monotonic() - t_start, 3),
    }


def evaluate(result: dict, q: dict) -> tuple[bool, str]:
    expect = q.get("expect", "")
    answer = result["answer"].lower()
    has_sources = len(result["sources"]) > 0

    if expect == "no_search" and has_sources:
        return False, "searched when it shouldn't have"
    if expect == "search" and not has_sources:
        return False, "no sources returned"
    if expect == "no_invention":
        for phrase in ["couldn't find", "no results", "unable to", "don't know", "not find",
                       "no reliable", "cannot find", "does not appear", "doesn't appear",
                       "no information", "not a known", "fictional"]:
            if phrase in answer:
                return True, "correctly admitted uncertainty"
        return False, "may have invented an answer"
    if "answer_contains" in q and q["answer_contains"].lower() not in answer:
        return False, f"expected '{q['answer_contains']}' in answer"
    return True, "pass"


async def main():
    data = yaml.safe_load(QUESTIONS_FILE.read_text())
    questions = data["questions"]
    session_id = str(uuid.uuid4())
    results = []

    async with httpx.AsyncClient() as client:
        for q in questions:
            print(f"\n[{q['id']}] {q['question'][:60]}")
            try:
                result = await run_question(client, session_id, q["question"])
                passed, reason = evaluate(result, q)
                status = "✓ PASS" if passed else "✗ FAIL"
                print(f"  {status} | ttft={result['ttft']}s | total={result['total']}s | {reason}")
                results.append({"id": q["id"], "passed": passed, "reason": reason, **result})
            except Exception as e:
                print(f"  ERROR: {e}")
                results.append({"id": q["id"], "passed": False, "reason": str(e)})

    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    avg_ttft = sum(r.get("ttft", 0) for r in results) / total
    print(f"\n--- Results: {passed}/{total} passed | avg ttft: {avg_ttft:.2f}s ---")


if __name__ == "__main__":
    asyncio.run(main())
