# Multi-Agent System — Build Tasks

## Phase 1: Foundation & Infrastructure

### Docker & Environment
- [x] `docker-compose.yml` — MongoDB + Redis + Django + Vite
- [x] `.env.example` — Environment variable template
- [x] `Dockerfile.backend` / `Dockerfile.frontend`

### Backend Scaffold
- [x] Django project scaffold (`backend/config/`)
- [x] `config/settings/base.py` — Common settings (mongoengine, DRF, Channels)
- [x] `config/settings/development.py` — Dev overrides
- [x] `config/settings/production.py` — Prod overrides
- [x] `config/urls.py` — API URL routing
- [x] `config/asgi.py` — ASGI with Channels

### Backend Utilities
- [x] `common/security.py` — Secret resolution (`get_secret`)
- [x] `common/llm_client.py` — OpenRouter client with retry/fallback
- [x] `common/validators.py` — Input validation utilities
- [x] `common/exceptions.py` — Custom DRF exception handler

### Agent Orchestration
- [x] `agents/event_bus.py` — Redis pub/sub wrapper
- [x] `agents/event_schemas.py` — Versioned event payload schemas (Pydantic)
- [x] `agents/agent_registry.py` — Agent subscription registry
- [x] `agents/management/commands/run_agents.py` — Start agents command

### Frontend Scaffold
- [x] Vite + React initialization
- [x] `src/index.css` — Design system
- [x] `src/api/client.js` — Axios instance (CSRF, HTTPS)

### Requirements
- [x] `requirements.txt` — Backend Python dependencies

---

## Phase 2: Auth + Employee Profile Agent
- [/] Authentication models, views, permissions, middleware
- [/] Employee models, views, signals
- [/] Login/Register pages (frontend)
- [/] AuthContext + useAuth hook

## Phase 3: Skill Assessment Agent
- [ ] Assessment models, views, tasks

## Phase 4: Recommendation Agent (CrewAI + LLM)
- [ ] Recommendation models, crew, tasks, views

## Phase 5: Training Mgmt + Progress Monitor
- [ ] Training models, tasks, views
- [ ] Progress models, tasks, views

## Phase 6: AI Chatbot (WebSocket + CrewAI)
- [ ] Chatbot models, consumers, routing, crew
- [ ] ChatWidget frontend components
- [ ] useWebSocket hook

## Phase 7: Analytics Dashboard + Reports
- [ ] Analytics models, tasks, views
- [ ] Notifications models, tasks, views
- [ ] HR Dashboard, Employee Dashboard, Manager pages (frontend)
