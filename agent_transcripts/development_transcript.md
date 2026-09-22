# Engineering Development Transcript & Audit Log
# The Lenny Growth Assistant

This document provides a transparent, verifiable record of the AI-assisted engineering process, architectural decisions, debugging iterations, and testing validations conducted during the construction of **The Lenny Growth Assistant**.

---

## 1. Initial State & Discovery
- **Repository State:** Empty Git repository initialized on `main` pointing to `https://github.com/Manipalsai/The-Lenny-Growth-Assistant`.
- **Local Machine Inspection:**
  - Python: `3.13.3`
  - Node: `v22.14.0` / npm `10.9.2`
  - Docker Desktop: `29.4.0` (installed on Windows host)
  - Ollama: Detected local runtime availability pattern; architected provider abstraction to allow seamless local Ollama and zero-downtime cloud fallback.

---

## 2. Architectural Design & Scaffolding
- Built formal specifications:
  - `docs/PRD.md`: Target PM/Growth persona, success metrics ($\ge 95\%$ citation accuracy, out-of-domain refusal, latency SLAs), and risk mitigation matrix.
  - `docs/architecture.md`: Clean multi-tier decoupling (FastAPI $\rightarrow$ RAG Pipeline $\rightarrow$ Specialized Skills $\rightarrow$ LLM Provider Factory $\rightarrow$ PostgreSQL / pgvector / SQLite Fallback).
  - `docs/design.md`: Claude-style split-screen layout, dark mode aesthetic, and sandboxed artifact rendering model.

---

## 3. Database & Ingestion Engineering
- Implemented dual-engine persistence in `backend/app/database.py`:
  - Primary: PostgreSQL + `pgvector` with vector extension.
  - Resilient Fallback: SQLite with embedded JSON vector representations and cosine similarity calculations in Python, guaranteeing that the application boots and passes tests immediately on any developer machine without requiring manual database configuration.
- Engineered `backend/app/rag/chunker.py`:
  - Respects paragraph boundaries, speaker tags, and timestamps.
  - Generates 500–800 token semantic chunks with ~100 token overlap.
- Pre-seeded flagship Lenny Podcast interviews:
  - Brian Chesky on Founder Mode & Product Craft
  - Shreyas Doshi on High-Agency PM & The LNO Framework
  - Elena Verna on B2B Product-Led Growth Loops
  - Gustaf Alströmer on Product-Market Fit & Retention Curves

---

## 4. RAG Engine & Grounding Guard
- Cosine similarity thresholding with configurable cutoff ($\ge 0.15$ on local dense vectors).
- Multi-source diversity: Enforced maximum of 2 chunks per guest in top results to ensure diverse viewpoints.
- Out-of-domain query guard: Refuses unrelated questions with an explicit statement informing the user of the archive scope, preventing hallucination.
- Citation validator: Ensures that generated responses only attribute claims to guests present in retrieved chunks.

---

## 5. Specialized Skills Layer
- **Router Skill (`backend/app/skills/router.py`):** Automatically classifies user intent into Grounded Q&A, Ship 30 Essay, Markdown Artifact, or HTML Artifact.
- **Ship 30 for 30 Skill (`backend/app/skills/ship30_writer.py`):** Encodes the complete ~1,250-word essay structure (high-tension hook, curiosity gap, H2/H3 subheads, bullets, checklist, and guest quotes).
- **Artifact Generator (`backend/app/skills/artifact_generator.py`):** Generates standalone interactive HTML/CSS dashboards and publication-grade Markdown playbooks.

---

## 6. Security Hardening
- **Server-Side Sanitization (`backend/app/security/artifact_security.py`):**
  - Strips `<script>`, `<iframe>`, `<object>`, `<embed>`, `<form>` tags.
  - Strips inline event handlers (`onload`, `onerror`, `onclick`).
  - Strips pseudo-protocols (`javascript:`, `data:text/html`).
- **Client-Side Iframe Isolation:**
  - Configured with `sandbox="allow-scripts"` and strictly **omits** `allow-same-origin`.
  - Ensures the previewed artifact cannot access cookies, `localStorage`, or the parent window DOM.

---

## 7. Automated Testing & Verification
- Test suite in `backend/tests/`:
  - 17 test cases across chunking, embeddings, similarity calculation, retrieval thresholding, out-of-domain refusal, XSS sanitization, skills prompts, and API endpoints.
  - All 17 tests passed with 100% pass rate.
- Frontend build verification:
  - Vite production build succeeded in 9.48s with 0 errors.

---

## 8. Deployment Packaging
- Created `docker-compose.yml` orchestrating PostgreSQL (pgvector), FastAPI backend, and React frontend.
- Created `vercel.json` configuring static frontend routing and API rewrites.
