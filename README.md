# The Lenny Growth Assistant 🚀
> **Production-Grade AI Knowledge & Growth Assistant Grounded in Lenny's Podcast Transcripts**

[![Backend Tests](https://img.shields.io/badge/pytest-17%20passed-emerald.svg)](backend/tests/)
[![Frontend](https://img.shields.io/badge/React%2018-Vite%20TypeScript-sky.svg)](frontend/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-blue.svg)](backend/)
[![pgvector](https://img.shields.io/badge/pgvector-PostgreSQL-indigo.svg)](backend/app/database.py)
[![License](https://img.shields.io/badge/License-MIT-slate.svg)](LICENSE)

---

## 1. Product Overview

**The Lenny Growth Assistant** is a full-stack, enterprise-grade AI conversational platform tailored for Product Managers, Growth Leads, and Founders. It indexes hundreds of hours of wisdom from Lenny's Podcast (including interviews with Brian Chesky, Shreyas Doshi, Elena Verna, Gustaf Alströmer, and more) to deliver:

1. **Strictly Grounded Answers:** Zero external hallucination. Responses are synthesized solely from verified podcast excerpts.
2. **Interactive Source Citations & Inspector:** Every insight links directly to verifiable guest quotes, timestamps, and episodes. Clicking a citation opens the **Source Inspector Drawer** revealing verbatim transcript passages.
3. **Ship 30 for 30 Essay Generator:** Transforms tactical insights into structured, ~1,250-word digital essays with hooks, curiosity tension, H2/H3 subheadings, and actionable frameworks.
4. **Claude-Style Sandboxed Artifact Viewer:** Renders interactive HTML/CSS dashboards and Markdown playbooks side-by-side with chat in a secure, isolated sandbox.
5. **Dual LLM Architecture (Local & Cloud):** Operates seamlessly on local **Ollama** (`llama3.2:3b`) with zero-downtime automatic fallback to **Cloud LLMs** (OpenAI `gpt-4o-mini` or Anthropic `claude-3-5-sonnet`).
6. **Provider-Agnostic Switching:** Instant runtime switching between local and cloud models directly from the UI header badge.

---

## 2. System Architecture

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        React / Vite Frontend                           │
│  ┌───────────────────────────┐      ┌───────────────────────────────┐  │
│  │   Chat & Session Stream   │      │ Claude-Style Sandboxed Viewer │  │
│  │ - Markdown Renderer       │      │ - Isolated <iframe> Sandbox   │  │
│  │ - Grounded Citations      │ ───► │ - HTML/CSS Live Preview       │  │
│  │ - Source Inspector Modal  │      │ - Code Toggle & 1-Click Copy  │  │
│  │ - Provider Switcher Badge │      │ - Versioning & Download       │  │
│  └───────────────────────────┘      └───────────────────────────────┘  │
└───────────────────────────────────▲────────────────────────────────────┘
                                    │ Server-Sent Events (SSE) / JSON
┌───────────────────────────────────▼────────────────────────────────────┐
│                         FastAPI Backend Engine                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ Router & Skills: Grounded QA | Ship 30 Writer | Artifact Builder │  │
│  └──────────────────────────────────┬───────────────────────────────┘  │
│                                     │                                  │
│  ┌──────────────────────────────────▼───────────────────────────────┐  │
│  │ RAG Pipeline: Cosine Retrieval (>=0.15) | Diversity | Refusal    │  │
│  └──────────────────────────────────┬───────────────────────────────┘  │
│                                     │                                  │
│  ┌──────────────────────────────────▼───────────────────────────────┐  │
│  │ Unified Provider Factory: Ollama (Local) <-> Cloud (OpenAI/Anth) │  │
│  └──────────────────────────────────┬───────────────────────────────┘  │
└─────────────────────────────────────┼──────────────────────────────────┘
                                      │
        ┌─────────────────────────────┴─────────────────────────────┐
        ▼                                                           ▼
┌─────────────────────────────────────┐             ┌─────────────────────┐
│    PostgreSQL + pgvector Database   │             │   Local / Cloud LLM │
│ (Sessions, Messages, Artifacts,     │             │ - Ollama (11434)    │
│  Chunks, Embeddings, SQLite fallbk) │             │ - OpenAI / Anthropic│
└─────────────────────────────────────┘             └─────────────────────┘
```

---

## 3. Tech Stack

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy 2.0, pgvector, Pydantic V2, httpx, pytest, pytest-asyncio.
- **Frontend:** React 18, TypeScript, Vite, Lucide Icons, Custom CSS Design System.
- **Data & Vector Storage:** PostgreSQL 16 with pgvector extension + automated SQLite zero-setup fallback.
- **LLM Engine:** Ollama (`llama3.2:3b`), OpenAI (`gpt-4o-mini`), Anthropic (`claude-3-5-sonnet`).
- **DevOps:** Docker Compose, Nginx, Vercel.

---

## 4. Quickstart (Run Locally in Under 2 Minutes)

### Prerequisites
- **Python:** 3.10+
- **Node.js:** 18+ (with npm)
- *(Optional)* [Ollama](https://ollama.com/) running locally with `ollama pull llama3.2:3b`

### Step 1: Clone Repository
```bash
git clone https://github.com/Manipalsai/The-Lenny-Growth-Assistant.git
cd The-Lenny-Growth-Assistant
```

### Step 2: Configure Environment
```bash
cp .env.example .env
```
*(Optional: add your `OPENAI_API_KEY` to `.env` if you wish to use Cloud models or test automatic fallback).*

### Step 3: Run Backend
```bash
# In the root directory:
pip install -r backend/requirements.txt
python scripts/ingest.py
uvicorn app.main:app --app-dir backend --reload --port 8000
```
*Backend will be live at: `http://localhost:8000` (API Docs at `http://localhost:8000/docs`).*

### Step 4: Run Frontend
```bash
cd frontend
npm install
npm run dev
```
*Open your browser at: `http://localhost:5173`.*

---

## 5. Docker Orchestration

To run the complete production stack (PostgreSQL + pgvector, FastAPI, React via Nginx) in Docker:
```bash
docker compose up --build
```
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

---

## 6. Vercel Deployment

The application is architected for Vercel deployment:
1. Connect this GitHub repository (`Manipalsai/The-Lenny-Growth-Assistant`) to Vercel.
2. In Vercel Project Settings:
   - **Framework Preset:** Vite
   - **Root Directory:** `./`
   - **Build Command:** `cd frontend && npm install && npm run build`
   - **Output Directory:** `frontend/dist`
3. Environment variables:
   - `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
   - `LLM_PROVIDER=openai`

---

## 7. Security Model & Untrusted HTML Isolation

Generated HTML artifacts are treated as **untrusted user input**:
1. **Server-Side Sanitizer (`backend/app/security/artifact_security.py`):**
   - Automatically strips `<script>`, `<iframe>`, `<object>`, `<embed>`, and external `<form>` tags.
   - Cleanses all inline DOM event handlers (`onload=`, `onerror=`, `onclick=`).
   - Rejects `javascript:` and `data:text/html` pseudo-protocols.
2. **Client-Side Iframe Isolation:**
   - Previews are embedded inside an `<iframe>` configured with:
     ```html
     <iframe sandbox="allow-scripts" srcdoc="..." />
     ```
   - **`allow-same-origin` is strictly omitted**, ensuring an opaque sandbox with zero access to `document.cookie`, `localStorage`, `sessionStorage`, or the parent window DOM.

---

## 8. Verification & Test Suite

All 17 unit, integration, and security tests can be run at any time:
```bash
python -m pytest backend/tests -v
```
**Results:** `17 passed in 9.56s (100% pass rate)`.

---

## 9. Evaluator Demo Walkthrough (2–3 Minutes)

1. **Ask a Core Question:**
   - Prompt: *"What did Brian Chesky say about Founder Mode and Airbnb's product reviews?"*
   - Observe: Fast streaming response, inline citation badges `[Founder Mode: Brian Chesky]`.
2. **Inspect the Grounded Source:**
   - Click the citation badge.
   - Observe: **Source Inspector Modal** appears with guest name, relevance score, and verbatim transcript passage.
3. **Generate a Ship 30 for 30 Essay:**
   - Click the suggested action chip: `✍️ Create Ship 30 Essay`.
   - Observe: Full ~1,250-word essay generated with hook, tension, H2/H3 subheads, and checklist.
4. **Generate an HTML Dashboard:**
   - Prompt: *"Create an interactive HTML dashboard visualizing Elena Verna's B2B growth loops."*
   - Observe: **Artifact Viewer** opens automatically on the right half with a live, sandboxed HTML preview, responsive styling, and raw code view.
5. **Test Out-of-Domain Refusal:**
   - Prompt: *"What is the boiling point of liquid helium?"*
   - Observe: System explicitly states that the Lenny transcript archive does not contain evidence for this question, refusing to hallucinate.
6. **Switch Providers:**
   - Toggle the Provider dropdown in the header from `Ollama` to `OpenAI` or `Anthropic`.
