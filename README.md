# Multi-Agent System for Employee Training & Onboarding

An event-driven, AI-powered employee learning and onboarding platform built with **Django**, **MongoDB**, **Redis Pub/Sub**, **CrewAI**, and **React (Vite)** with a glassmorphism UI.

---

## 🌟 Features & AI Agents

The platform uses a decoupled, event-driven multi-agent architecture where agents communicate asynchronously over a Redis Pub/Sub Event Bus.

### 🤖 The 6 AI Agents
1. **Employee Profile Agent** (`apps/employees`): Manages employee profile lifecycles and emits profile events (`employee.registered`).
2. **Skill Assessment Agent** (`apps/assessments`): Evaluates employee assessment responses using an LLM, scores proficiency, and identifies weak skill areas (`assessment.completed`).
3. **Learning Recommendation Agent** (`apps/recommendations`): Powered by **CrewAI** (Data Analyst Agent + Curriculum Designer Agent). Generates personalized multi-module learning plans based on assessment results (`plan.created`).
4. **Training Management & Progress Agent** (`apps/training`): Assigns learning modules with staggered due dates. Rewards active completion by automatically granting deadline extensions on overdue modules (`training.assigned`, `progress.updated`).
5. **Support Chatbot Agent** (`apps/chatbot`): A 24/7 interactive assistant operating via WebSockets (`ws://localhost:8000/ws/chat/`). Uses a two-agent CrewAI pipeline (Context Retriever + Support Agent) with guardrails against PII leakage.
6. **Analytics & Notifications Agent** (`apps/analytics`, `apps/notifications`): Aggregates system metrics and delivers real-time notifications to employees and managers.

### 🎨 User Interface & RBAC
- **Role-Based Access Control (RBAC)**: Supports `Employee`, `Manager`, and `HR` roles with dynamic UI routing.
- **Glassmorphism Aesthetic**: Styled with modern Tailwind CSS gradients, micro-animations, and responsive cards.

---

## 🏗️ Technology Stack

- **Backend**: Python 3.12, Django 4.2+, Django REST Framework (DRF), Django Channels (WebSockets), Daphne ASGI Server
- **Database**: MongoDB 7.0 (via `mongoengine`)
- **Event Bus & Cache**: Redis 7.2 Pub/Sub & Key-Value Store
- **AI Orchestration**: CrewAI, LangChain, OpenRouter API Gateway
- **Frontend**: React 18, Vite, Tailwind CSS, Lucide / Heroicons
- **Containerization**: Docker, Docker Compose

---

## 🚀 Quick Start (Docker Compose)

The easiest way to run the entire stack (MongoDB, Redis, Backend + Agents, and Frontend) is using Docker Compose.

### 1. Prerequisites
- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/) installed.

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(Optional)* Add your OpenRouter API key to `.env` if you want to test live LLM responses:
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

Generate new values for `DJANGO_SECRET_KEY`, `JWT_SECRET_KEY`, and the database/Redis passwords. Do not reuse any previously exposed values.

### 3. Build & Run Containers
Start all services in detached mode:
```bash
docker compose up -d --build
```

### Provision the first HR/admin account

Public registration creates only unlinked employee accounts. Provision elevated roles from the backend container (the command securely prompts for a password):

```bash
docker compose exec backend python manage.py provision_user --email hr@example.com --role hr_admin
```

### Demo course catalog

The backend seeds eight idempotent demo courses at startup, covering Python, SQL, communication, soft skills, project management, data analysis, problem solving, and system design. To seed them manually in local development:

```bash
python manage.py seed_training_catalog
```
*(Note: If your user is not in the `docker` group on Linux, use `sg docker -c "docker compose up -d --build"` or `sudo docker compose up -d --build`).*

---

## 🌐 Access Points

Once all containers are running:

| Service | Endpoint | Details |
| :--- | :--- | :--- |
| **Frontend Web App** | [http://localhost:5173](http://localhost:5173) | Interactive Dashboard (Employee / Manager / HR) |
| **Backend REST API** | [http://localhost:8000/api/v1/](http://localhost:8000/api/v1/) | API base route |
| **Health Check** | [http://localhost:8000/health/](http://localhost:8000/health/) | Returns `{"status": "ok"}` |
| **WebSocket Chat** | `ws://localhost:8000/ws/chat/` | Chatbot real-time WebSocket connection |
| **MongoDB** | `127.0.0.1:27017` | Direct database connection |
| **Redis** | `127.0.0.1:6379` | Event bus connection |

---

## 📋 Useful Commands

### Check Container Status
```bash
docker compose ps
```

### View Live Logs
```bash
# Tail logs for all services
docker compose logs -f

# Tail logs specifically for backend (Daphne server & AI agent worker)
docker compose logs -f backend

# Tail logs for frontend (Vite dev server)
docker compose logs -f frontend
```

### Restart Services
```bash
docker compose restart backend
```

### Stop Containers
```bash
docker compose down
```

---

## 🛠️ Local Development (Without Docker)

If you prefer to run services individually on host:

### Prerequisites
- Python 3.12+
- Node.js 18+
- Local MongoDB running on `localhost:27017`
- Local Redis running on `localhost:6379`

### 1. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/venv/activate
pip install -r requirements.txt

# Start the Event Bus Agent Worker (in terminal 1)
python manage.py run_agents

# Start the Daphne ASGI Web Server (in terminal 2)
daphne -b 127.0.0.1 -p 8000 config.asgi:application
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 📁 Project Structure

```
.
├── backend/
│   ├── agents/               # Redis EventBus, Pydantic event schemas, & run_agents command
│   ├── apps/
│   │   ├── analytics/        # Report generation & agent tasks
│   │   ├── assessments/      # Skill assessment & evaluation agent
│   │   ├── authentication/   # JWT auth, RBAC permissions, Security middleware
│   │   ├── chatbot/          # Real-time WebSocket consumers & CrewAI Chatbot
│   │   ├── employees/        # Profile models & employee registration signals
│   │   ├── notifications/    # Notification delivery agent
│   │   ├── recommendations/  # CrewAI Learning Plan recommendation crew
│   │   └── training/         # Module assignment & progress monitoring agent
│   ├── common/               # Security utilities & OpenRouter LLM client
│   ├── config/               # Django ASGI/WSGI, routing, and settings
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # UI components & Glassmorphism ChatWidget
│   │   ├── context/          # Auth & Role state providers
│   │   ├── pages/            # Employee, Manager, and HR Dashboards
│   │   └── services/         # API & WebSocket client hooks
│   └── package.json
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── .env.example
└── README.md
```

---

## 📄 License
This project is licensed under the MIT License.
