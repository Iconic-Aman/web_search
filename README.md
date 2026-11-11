# Search Chat Agent

A chat agent with one tool — web search. Answers fast, cites sources, and remembers what you asked and when.

---

## Quickstart

### 1. Run Backend & Frontend (Single Server)
```bash
cd backend
python -m venv venv
# On Windows: venv\Scripts\activate | On macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # add your API keys to .env
uvicorn app.main:app --reload
```
Open **http://localhost:8000** in your browser (FastAPI serves the pre-built UI).

### 2. Frontend Development (Optional)
If you want live hot-reloading for frontend edits:
```bash
pnpm -C frontend install
pnpm -C frontend dev
```
Open **http://localhost:5173**.

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
