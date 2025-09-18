
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Agentic Financial Advisor application built as a Turborepo monorepo. The application consists of:

- **Frontend**: Next.js 15 web application (`apps/web`) running on port 3000
- **Backend**: FastAPI Python API (`apps/api`) running on port 8000  
- **Database**: Supabase (PostgreSQL) for data storage
- **Architecture**: Full-stack application with RAG (Retrieval-Augmented Generation) pipeline for personalized financial recommendations

## Development Commands

### Root Level (Turborepo commands)
- `npm run dev` - Start all applications in development mode
- `npm run build` - Build all applications
- `npm run lint` - Lint all applications (with max warnings = 0)
- `npm run format` - Format code with Prettier
- `npm run check-types` - Type check all applications

### Web App (apps/web)
- `npm run dev` - Start Next.js dev server with Turbopack on port 3000
- `npm run build` - Build Next.js application
- `npm run start` - Start production server
- `npm run test` - Run Jest tests
- `npm run lint` - Lint with ESLint (max warnings = 0)
- `npm run check-types` - TypeScript type checking

### API (apps/api)
- Python FastAPI application
- Install dependencies: `pip install -r apps/api/requirements.txt`
- Run API: `uvicorn apps.api.main:app --reload --port 8000`
- Run tests: `pytest apps/api/tests/`
- Dependencies include: FastAPI, Supabase client, Uvicorn, pytest

## Project Structure

```
agentic-financial-advisor/
├── apps/
│   ├── web/          # Next.js frontend application
│   ├── api/          # FastAPI backend application  
│   └── docs/         # Documentation app (if exists)
├── packages/
│   ├── ui/           # Shared React components
│   ├── eslint-config/# Shared ESLint configuration
│   └── typescript-config/ # Shared TypeScript configuration
└── [root config files]
```

## Tech Stack

### Frontend
- **Framework**: Next.js 15 with React 19
- **Language**: TypeScript 5.9
- **Styling**: Tailwind CSS + Shadcn/UI components
- **State Management**: Zustand
- **Testing**: Jest + React Testing Library
- **Build Tool**: Turbopack for development

### Backend  
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Database**: Supabase (PostgreSQL)
- **Testing**: pytest
- **Vector Store**: ChromaDB (for RAG)

### Data Models
- **Lead**: User information (name, email, DOB, consent)
- **Session**: Chat session tracking with status (active/agreed/abandoned)
- **Message**: Individual chat messages (user/bot)
6
## Environment Setup

### Required Environment Variables (API)
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase anon/service role key

### Prerequisites
- Node.js 18+
- Python 3.11+
- npm 10.9.3+
- PostgreSQL (via Supabase)

## Development Workflow

1. Install dependencies: `npm install` (root level installs all workspaces)
2. Set up environment variables for API
3. Start development: `npm run dev` (starts both frontend and backend)
4. Frontend runs on http://localhost:3000
5. API runs on http://localhost:8000

## Key API Endpoints

- `GET /health` - Health check
- `POST /api/leads` - Create new lead
- `POST /chat/query` - Chat message handling
- `POST /session/agree` - Mark session as agreed

## Testing

- Frontend: Jest with React Testing Library
- Backend: pytest
- E2E: Playwright (mentioned in architecture but not yet implemented)
- Run linting and type checking before commits

## Architecture Notes

- Local development setup (no containers)
- RAG pipeline for financial recommendations
- Repository pattern for database abstraction
- Component-based React UI
- REST API design
- Turborepo for monorepo management with caching