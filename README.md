# Sales Insight Automator — Rabbitt AI

🐰 **Transform your sales data into actionable insights with AI**

A production-grade, containerized full-stack application where users upload CSV/Excel sales data files, an LLM generates a professional narrative summary, and the summary is emailed to a specified recipient.

![CI Pipeline](https://github.com/rabbittai/sales-insight-automator/workflows/CI%20Pipeline/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Node](https://img.shields.io/badge/node-20-green.svg)

---

## 🚀 Live Links

| Service | URL |
|---------|-----|
| Frontend | [https://sales-insight.vercel.app](https://sales-insight.vercel.app) |
| API Docs | [https://api.sales-insight.com/docs](https://api.sales-insight.com/docs) |
| Health Check | [https://api.sales-insight.com/api/health](https://api.sales-insight.com/api/health) |

---

## ✨ Features

- **📁 File Upload**: Support for CSV and XLSX files up to 10MB
- **🤖 AI Analysis**: Powered by Google Gemini or Groq LLMs
- **📧 Email Delivery**: Reports sent via SendGrid or Resend
- **🔒 Security**: API key authentication, rate limiting, input validation
- **🐳 Docker**: Fully containerized for easy deployment
- **⚡ CI/CD**: GitHub Actions pipeline for testing and deployment

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        SYSTEM ARCHITECTURE                      │
├─────────────────┬───────────────────────────┬───────────────────┤
│   FRONTEND      │       BACKEND (API)        │   EXTERNAL        │
│   React/Vite    │       FastAPI (Python)     │   SERVICES        │
│   Vercel        │       Render               │                   │
│                 │                            │  - Gemini / Groq  │
│  - File Upload  │  POST /api/upload          │  - SendGrid /     │
│  - Email Input  │  GET  /api/health          │    Resend (email) │
│  - Status Feed  │  GET  /docs (Swagger)      │                   │
│  - Results View │  Rate Limiting + Auth      │                   │
└─────────────────┴───────────────────────────┴───────────────────┘
```

---

## 🚀 Quick Start (Docker)

### Prerequisites

- Docker & Docker Compose
- API keys for LLM provider (Gemini or Groq)
- API key for email provider (SendGrid or Resend)

### Steps

```bash
# Clone the repository
git clone https://github.com/rabbittai/sales-insight-automator
cd sales-insight-automator

# Copy environment templates
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit backend/.env with your API keys
# Edit frontend/.env with your API URL and key

# Build and start services
docker compose up --build
```

Visit: http://localhost:5173

---

## 🛠️ Local Development

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your keys

# Run development server
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Copy and configure environment
cp .env.example .env
# Edit .env

# Run development server
npm run dev
```

---

## 🔐 Security Implementation

| # | Security Measure | Implementation |
|---|------------------|----------------|
| 1 | API Key Authentication | `X-API-Key` header validation on all mutating endpoints |
| 2 | Rate Limiting | SlowAPI: 10 requests/minute per IP |
| 3 | File Type Validation | Extension + MIME type verification |
| 4 | File Size Cap | Configurable limit (default: 10MB) |
| 5 | Input Sanitization | Pydantic validators, email regex |
| 6 | CORS Whitelist | Explicit origin configuration |
| 7 | Non-root Container | Docker user with UID 1001 |
| 8 | No Secrets in Logs | Only email domain logged, never full addresses |
| 9 | Dependency Pinning | Exact versions in requirements.txt |
| 10 | Security Headers | TrustedHostMiddleware |

---

## 📝 Environment Variables

### Backend (`backend/.env`)

```env
# API Security
API_KEY=your-secret-api-key-here

# CORS
ALLOWED_ORIGINS=http://localhost:5173,https://your-frontend.vercel.app

# LLM Provider (gemini or groq)
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-api-key
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama3-70b-8192

# Email Provider (sendgrid or resend)
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=your-sendgrid-key
RESEND_API_KEY=your-resend-key
FROM_EMAIL=insights@rabbittai.com

# Limits
MAX_FILE_SIZE_MB=10
RATE_LIMIT=10/minute
```

### Frontend (`frontend/.env`)

```env
VITE_API_URL=http://localhost:8000
VITE_API_KEY=your-secret-api-key-here
```

---

## 🏛️ Architecture Decisions

### FastAPI Choice
- Async-first design for high concurrency
- Auto-generated OpenAPI documentation
- Pydantic for robust data validation
- Built-in dependency injection

### LLM Provider Abstraction
- Pluggable architecture supporting Gemini and Groq
- Retry logic with exponential backoff
- Fallback template generation if LLM fails

### Email Provider Abstraction
- Support for SendGrid and Resend
- Branded HTML email templates
- Secure logging (domain only, never full email)

### Multi-stage Docker
- Minimal production images
- Non-root user execution
- Health checks included

---

## ⚡ CI/CD Pipeline

The GitHub Actions workflow includes:

| Job | Description |
|-----|-------------|
| `lint-backend` | Runs Ruff linter on Python code |
| `test-backend` | Executes pytest test suite |
| `lint-frontend` | Runs ESLint on React code |
| `build-frontend` | Builds production frontend bundle |
| `build-docker` | Builds and tests Docker images |

Triggers:
- Pull requests to `main`
- Pushes to `main`

---

## 🚀 Deployment

### Backend → Render

1. Connect your GitHub repository
2. Create a new Web Service
3. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Add all keys from `.env.example`

### Frontend → Vercel

1. Import your GitHub repository
2. Configure:
   - **Framework**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Environment Variables**: `VITE_API_URL`, `VITE_API_KEY`

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend lint
cd frontend
npm run lint
```

---

## 📁 Project Structure

```
sales-insight-automator/
├── frontend/                    # React + Vite SPA
│   ├── src/
│   │   ├── components/          # UI components
│   │   ├── hooks/               # Custom React hooks
│   │   ├── services/            # API client
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── Dockerfile
│   └── package.json
│
├── backend/                     # FastAPI Python API
│   ├── app/
│   │   ├── routers/             # API endpoints
│   │   ├── services/            # Business logic
│   │   ├── middleware/          # Security & rate limiting
│   │   ├── schemas/             # Pydantic models
│   │   ├── config.py
│   │   └── main.py
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
│
├── docker-compose.yml
├── docker-compose.prod.yml
├── .github/workflows/ci.yml
└── README.md
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🐰 About Rabbitt AI

Building intelligent automation tools for modern businesses.

**Made with ❤️ by the Rabbitt AI Team**
