# Skill Exchange Platform

A full-stack Skill Exchange Platform with a FastAPI backend, React frontend, SQLite storage by default, and local Ollama-powered AI enrichment.

## Stack

- Backend: FastAPI, SQLAlchemy, Alembic
- Frontend: React + Vite
- Auth: JWT bearer tokens
- Database: SQLite by default, configurable through `DATABASE_URL`
- Local AI runtime: Ollama

## Features

- User signup, login, logout, and JWT authentication
- Profile management with bio, city, and profile photo URL
- Skill listings for both offers and requests
- AI-assisted skill listing normalization
- Automatic skill tag generation
- Natural-language skill search
- Semantic match scoring between requested and offered skills
- Exchange request workflow with status updates
- In-platform chat after request acceptance
- Environment-driven backend configuration
- Alembic migration scaffold with initial schema

## Backend setup

1. Create and activate a Python virtual environment.
2. Install dependencies:

```bash
python3 -m pip install -r backend/requirements.txt
```

3. Create a backend env file:

```bash
cp backend/.env.example backend/.env
```

4. Make sure Ollama is running locally and the required models are installed:

```bash
ollama list
```

Expected models for the current default setup:

- `llama3.2:latest`
- `nomic-embed-text:latest`

5. Run migrations:

```bash
PYTHONPATH=backend python3 -m alembic upgrade head
```

6. Start the API:

```bash
PYTHONPATH=backend python3 -m uvicorn app.main:app --reload
```

The API is served at `http://127.0.0.1:8000` and routes are namespaced under `/api/v1`.

## Frontend setup

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Copy environment values if needed:

```bash
cp .env.example .env
```

3. Start the frontend:

```bash
npm run dev
```

By default, the frontend expects the API at `http://localhost:8000/api/v1`.

## LLM configuration

The backend loads environment values from `backend/.env`.

Model defaults:

- Listing assistant and auto-tagging: `llama3.2:latest`
- Semantic matching and natural-language search embeddings: `nomic-embed-text:latest`

Required for live model-backed behavior:

- local Ollama server running on `http://localhost:11434`
- models pulled locally

Optional:

- `LLM_BASE_URL`
- `LLM_MODEL`
- `EMBEDDING_MODEL`

If `LLM_API_KEY` is not set, the app falls back to deterministic heuristics so local development still works.

Current default `backend/.env` shape:

```env
LLM_API_KEY=ollama
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=llama3.2:latest
EMBEDDING_MODEL=nomic-embed-text:latest
```

## Database configuration

If `DATABASE_URL` is not set, the backend uses:

```text
sqlite:///backend/skill_exchange.db
```

You can point it to MySQL or PostgreSQL by exporting a compatible SQLAlchemy URL before starting the backend and running migrations.

## Key API routes

- `POST /api/v1/auth/signup`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `GET /api/v1/users/me`
- `PUT /api/v1/users/me`
- `GET /api/v1/skills/`
- `GET /api/v1/skills/me`
- `POST /api/v1/skills/ai-suggest`
- `POST /api/v1/skills/`
- `PUT /api/v1/skills/{skill_id}`
- `DELETE /api/v1/skills/{skill_id}`
- `GET /api/v1/skills/matches/me`
- `GET /api/v1/skills/search?q=...`
- `GET /api/v1/exchange-requests/`
- `POST /api/v1/exchange-requests/`
- `PATCH /api/v1/exchange-requests/{request_id}/status`
- `GET /api/v1/chat/threads`
- `POST /api/v1/chat/threads/{exchange_request_id}`
- `GET /api/v1/chat/threads/{thread_id}`
- `POST /api/v1/chat/threads/{thread_id}/messages`

## Data storage

By default the application stores data in:

```text
backend/skill_exchange.db
```

Main persisted tables:

- `users`
- `skills`
- `skill_tags`
- `exchange_requests`
- `chat_threads`
- `chat_messages`

AI-generated enrichment is stored on each skill record:

- `ai_summary`
- `search_document`
- `embedding_vector`

See [flow.txt](/home/ruproy9924/projects/skill_exchange_platform/flow.txt:1) for the full end-to-end workflow.

## Verification completed

- Python modules compile successfully with `python3 -m compileall backend`
- Alembic migration applies successfully against SQLite
- Frontend builds successfully with `npm run build`
- Backend service flow verified against SQLite for:
  - signup
  - login
  - profile update
  - skill creation
  - AI suggestion
  - semantic match generation
  - natural-language search
  - exchange request creation
  - exchange request acceptance
  - chat thread creation and messaging
