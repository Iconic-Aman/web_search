# Search Chat Agent

A chat agent with one tool — web search. Answers fast, cites sources, and remembers what you asked and when.

---

## Setup (3 commands)

```bash
# Terminal 1: Backend
cd backend
cp .env.example .env        # fill in your keys
uvicorn app.main:app --reload

# Terminal 2: Frontend (Dev)
pnpm -C frontend dev
# or open http://localhost:8000 directly (FastAPI serves the built frontend)

---

## Keys needed

| Key | Where to get |
|-----|-------------|
| `OPENROUTER_API_KEY` | [openrouter.ai](https://openrouter.ai) |
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` |
| `OPENROUTER_MODEL` | e.g. `openai/gpt-4o-mini` |
| `TAVILY_API_KEY` | [tavily.com](https://tavily.com) |

---

## Run evals

```bash
# Terminal 1
uvicorn app.main:app

# Terminal 2
cd backend
python -m evals.run_evals
```

---

## Latency (from evals)

| Case | TTFT | Total |
|------|------|-------|
| No search (stable facts, greetings) | ~0.8s | ~1s |
| With search (fresh facts) | ~4–6s | ~6–10s |

---

## Deploy to Render

1. Push repo to GitHub
2. Create a new **Web Service** on Render, point to this repo
3. Render auto-detects `render.yaml` — build + start commands are pre-configured
4. Add `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL`, `OPENROUTER_MODEL`, `TAVILY_API_KEY` in Render dashboard
5. The persistent disk (`/data/chat.db`) is configured in `render.yaml`

---

## Architecture

- **FastAPI** — API + SSE streaming
- **OpenRouter** — LLM access (swappable model)
- **Tavily** — web search (LLM-ready results)
- **SQLite** — sessions, messages, search cache
- **One tool** — `web_search`, max 2 rounds, parallel calls, 10-min cache
