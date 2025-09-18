# Gemini Code Assistant Context

## Project Overview

This is a full-stack lead generation application with an agentic RAG (Retrieval-Augmented Generation) pipeline.

*   **Frontend:** A Next.js (React/TypeScript) application using Tailwind CSS. It provides a user interface for lead capture (a form) and a chat interface for interacting with the RAG agent.
*   **Backend:** A Python API built with FastAPI. It handles lead creation, session management, and exposes the RAG agent's capabilities.
    *   **Database:** Uses a PostgreSQL database (via Supabase) with SQLAlchemy as the ORM to store lead information, chat history, and recommendations.
    *   **RAG Pipeline:** Uses LangChain, ChromaDB, and an LLM (Anthropic or OpenAI) to answer user queries based on a local knowledge base of documents (PDFs, DOCX, etc.).
    *   **Agentic Features:** The backend supports actions like "agreeing" to a plan (which can trigger an email) and "exploring" more options, suggesting a multi-step, agent-like workflow.

The typical user flow is:
1.  A user fills out a form on the landing page.
2.  A `Lead` and a `Session` are created in the database.
3.  The user is redirected to a chat page (`/chat`).
4.  The chat interface interacts with the RAG agent to provide personalized recommendations from the knowledge base.

## Building and Running

### Backend (`/backend`)

1.  **Set up environment:**
    ```bash
    cd backend
    python -m venv .venv
    # On Windows
    .venv\Scripts\activate
    # On macOS/Linux
    source .venv/bin/activate
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure environment variables:**
    *   Copy `.env.example` to `.env`.
    *   Fill in `SUPABASE_DB_URL` and your `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`.
4.  **Ingest knowledge base:**
    *   Add documents (PDF, DOCX, CSV, TXT) to the `knowledge_base/` directory.
    *   Run the ingestion script:
        ```bash
        python -m rag.ingestion
        ```
5.  **Run the server:**
    ```bash
    uvicorn main:app --reload --port 8000
    ```

### Frontend (`/frontend`)

1.  **Set up environment:**
    ```bash
    cd frontend
    ```
2.  **Install dependencies:**
    ```bash
    npm install
    ```
3.  **Configure environment variables:**
    *   Copy `.env.local.example` to `.env.local`. The default points to the backend API at `http://localhost:8000`.
4.  **Run the development server:**
    ```bash
    npm run dev
    ```
5.  **Access the application:**
    *   Open [http://localhost:3000](http://localhost:3000) in your browser.

## Development Conventions

*   **Backend:** The backend follows a standard FastAPI structure.
    *   `main.py`: Defines API endpoints.
    *   `database.py`: Handles database initialization and session management.
    *   `schemas.py`: Contains Pydantic models for data validation.
    *   `rag/`: Contains the logic for the RAG pipeline (`ingestion.py`, `rag_agents.py`).
*   **Frontend:** The frontend is a standard Next.js application.
    *   `app/page.tsx`: The main landing/form page.
    *   `app/chat/page.tsx`: The chat interface.
    *   API calls are made to the backend service defined in `NEXT_PUBLIC_API_BASE_URL`.
*   **State Management:** The frontend uses a `session_token` stored in `localStorage` to maintain the user's session with the backend across requests.
