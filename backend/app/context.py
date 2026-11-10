from app.memory import load_recent, load_question_log, load_summary
from app.prompts import build_system_prompt
from datetime import datetime, timezone
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo


def _to_local(utc_str: str, tz: str) -> str:
    try:
        dt = datetime.fromisoformat(utc_str).replace(tzinfo=timezone.utc)
        return dt.astimezone(ZoneInfo(tz)).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return utc_str


def _fmt_turn(role: str, content: str, ts: str, tz: str) -> dict:
    return {"role": role, "content": f"[{ts} {tz}] {content}"}


async def build_context(session_id: str, user_message: str, tz: str = "UTC") -> list[dict]:
    summary = await load_summary(session_id)
    recent = await load_recent(session_id)
    q_log = await load_question_log(session_id)

    system = build_system_prompt(tz)

    if summary:
        system += f"\n\nSummary of earlier conversation:\n{summary}"

    if q_log:
        lines = "\n".join(f"- [{_to_local(r['created_at'], tz)} {tz}] {r['content']}" for r in q_log)
        system += f"\n\nAll questions asked this session:\n{lines}"

    messages = [{"role": "system", "content": system}]

    for r in recent:
        ts = _to_local(r['created_at'], tz)
        messages.append({"role": r["role"], "content": f"[{ts} {tz}] {r['content']}"})

    messages.append({"role": "user", "content": user_message})
    return messages
