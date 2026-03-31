# Skill Exchange Platform

A production-oriented full-stack Skill Exchange Platform with a FastAPI backend and React frontend.

## Stack

- Backend: FastAPI, SQLAlchemy, Alembic
- Frontend: React + Vite
- Auth: JWT bearer tokens
- Database: SQLite by default, configurable through `DATABASE_URL`

## Features

- User signup, login, logout, and JWT authentication
- Profile management with bio, city, and profile photo URL
- Skill listings for both offers and requests
- Automatic match discovery based on requested skills and other users' offered skills
- Exchange request workflow with status updates
- Environment-driven backend configuration
- Alembic migration scaffold with initial schema

## Backend setup

1. Create and activate a Python virtual environment.
2. Install dependencies:

```bash
python3 -m pip install -r backend/requirements.txt
```

3. Run migrations:

```bash
PYTHONPATH=backend python3 -m alembic upgrade head
```

4. Start the API:

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
- `POST /api/v1/skills/`
- `PUT /api/v1/skills/{skill_id}`
- `DELETE /api/v1/skills/{skill_id}`
- `GET /api/v1/skills/matches/me`
- `GET /api/v1/exchange-requests/`
- `POST /api/v1/exchange-requests/`
- `PATCH /api/v1/exchange-requests/{request_id}/status`

## Verification completed

- Python modules compile successfully with `python3 -m compileall backend`
- Alembic migration applies successfully against SQLite
- Frontend builds successfully with `npm run build`
- Backend service flow verified against SQLite for:
  - signup
  - login
  - profile update
  - skill creation
  - match generation
  - exchange request creation
  - exchange request acceptance
