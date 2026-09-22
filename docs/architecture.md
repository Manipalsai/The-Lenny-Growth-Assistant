# System Architecture & Technical Specification
# The Lenny Growth Assistant

---

## 1. High-Level Architectural Diagram

```text
+-----------------------------------------------------------------------+
|                           React / Vite Frontend                       |
|  +---------------------------+   +---------------------------------+  |
|  |   Chat & Session Stream   |   | Claude-Style Sandboxed Artifact |  |
|  | - Markdown Renderer       |   | - Isolated <iframe>             |  |
|  | - Source Citations        |   | - HTML / CSS / Markdown Preview |  |
|  | - Source Inspector Modal  |   | - Copy / Code Inspector         |  |
|  | - Provider Switcher Badge |   +---------------------------------+  |
|  +---------------------------+                                        |
+-----------------------------------▲-----------------------------------+
                                    │ Server-Sent Events (SSE) / JSON REST
+-----------------------------------▼-----------------------------------+
|                        FastAPI Backend Engine                         |
|                                                                       |
|  +-----------------------------------------------------------------+  |
|  |                        API Routing Layer                        |  |
|  |  /api/health   |   /api/sessions   |   /api/chat   |  /api/artifacts |
|  +-----------------------------------------------------------------+  |
|                                   │                                   |
|  +--------------------------------▼---------------------------------+  |
|  |               Agent Router & Specialized Skills Layer            |  |
|  |  - Router: Intent Classification (Q&A vs Ship30 vs Artifact)    |  |
|  |  - Grounded QA Skill: Strict Citation Synthesis                 |  |
|  |  - Ship 30 for 30 Skill: 1,250-word Framework Essay Writer      |  |
|  |  - Artifact Generator: Structured JSON / Markdown / HTML         |  |
|  +--------------------------------┬---------------------------------+  |
|                                   │                                   |
|  +--------------------------------▼---------------------------------+  |
|  |                       RAG Retrieval Pipeline                     |  |
|  |  Query -> Embedding Generator -> Vector Search (pgvector)       |  |
|  |        -> Cosine Similarity Threshold (>= 0.70)                 |  |
|  |        -> Source Diversity & Deduplication                      |  |
|  |        -> Context Assembler & Citation Validator                 |  |
|  +--------------------------------┬---------------------------------+  |
|                                   │                                   |
|  +--------------------------------▼---------------------------------+  |
|  |                    Unified LLM Provider Factory                  |  |
|  |  - OllamaProvider (Local llama3.2:3b via HTTP)                  |  |
|  |  - CloudProvider (OpenAI gpt-4o-mini / Anthropic claude-3-5)    |  |
|  |  - Fallback Engine (Automatic fallback with zero user downtime) |  |
|  +--------------------------------┬---------------------------------+  |
+-----------------------------------┼-----------------------------------+
                                    │
       +----------------------------┴----------------------------+
       │                                                         │
+------▼-------------------------------+     +-------------------▼----+
|      PostgreSQL + pgvector Database    |     |   Local Ollama / Cloud |
| - Sessions (UUID, timestamps)        |     |   LLM APIs             |
| - Messages (Role, content, sources)  |     +------------------------+
| - Transcript Chunks & Embeddings     |
| - Artifacts (Type, version, HTML)    |
| - (Automatic SQLite fallback)        |
+--------------------------------------+
```

---

## 2. Component Breakdown

### 2.1 Backend (`backend/app`)
- **`main.py`**: FastAPI setup, lifespan startup hooks (DB initialization, health status check), global error handlers, and CORS configuration.
- **`config.py`**: Pydantic `BaseSettings` reading environment variables with sensible defaults.
- **`database.py`**: SQLAlchemy engine and session makers. Supports PostgreSQL with `pgvector` vector extension, with graceful automatic fallback to SQLite + in-memory cosine similarity if PostgreSQL is not active.
- **`models/`**:
  - `db_models.py`: Declarative SQLAlchemy models (`SessionModel`, `MessageModel`, `ArtifactModel`, `TranscriptChunkModel`).
  - `schemas.py`: Pydantic V2 schemas for requests, responses, streaming events, and artifact payloads.
- **`providers/`**:
  - `base.py`: Abstract `BaseLLMProvider` defining `generate()`, `stream()`, and `health_check()`.
  - `ollama_provider.py`: Async client for local Ollama HTTP API (`/api/generate` / `/api/chat`).
  - `cloud_provider.py`: Unified provider for OpenAI and Anthropic SDKs/REST endpoints.
  - `factory.py`: Instantiates active provider based on runtime settings, handles automatic fallback from Ollama to Cloud on connection timeouts or errors.
- **`rag/`**:
  - `chunker.py`: Token-aware semantic chunker respecting paragraph boundaries (500–800 tokens, 100 overlap).
  - `embeddings.py`: Generates dense vector representations (local sentence-transformers or hash-based normalized vector fallback for zero-dependency portability).
  - `retriever.py`: Executes similarity search, applies similarity cutoff ($\ge 0.70$), source deduplication across episodes, and confidence rating.
  - `citation.py`: Parses, formats, and validates citations (`[Episode: Guest — Topic]`).
- **`skills/`**:
  - `router.py`: Determines whether user intent is Grounded Q&A, Ship 30 essay, or Artifact generation.
  - `grounded_qa.py`: Synthesizes concise, direct, transcript-supported answers.
  - `ship30_writer.py`: Generates complete, ~1,250-word Ship 30 for 30 essays with hook, tension, and framework.
  - `artifact_generator.py`: Generates standalone Markdown and HTML/CSS deliverables.
- **`security/`**:
  - `artifact_security.py`: Server-side sanitization, strict CSP headers, and iframe sandboxing attributes.
- **`observability/`**:
  - `logging.py`: Structured JSON logger tracing request IDs, session IDs, model latencies, and token counts.

### 2.2 Frontend (`frontend/src`)
- **Vite + React + TypeScript**: Fast, reactive client interface.
- **`Sidebar.tsx`**: Multi-session management, New Chat button, session title editing, and provider status badge.
- **`ChatPane.tsx`**: Streaming conversation display with smooth auto-scroll, message timestamps, suggested follow-up chips, and citation badges.
- **`SourceInspector.tsx`**: Side drawer/modal exposing exact episode, guest name, timestamp, and verbatim supporting transcript chunk when a citation is clicked.
- **`ArtifactViewer.tsx`**: Claude-style side panel with:
  - Sandboxed `<iframe>` preview for HTML/CSS.
  - Rendered Markdown view.
  - Raw source code toggle with 1-click copy.
  - Responsive split-pane on desktop, collapsible drawer on mobile.

---

## 3. Data Ingestion & Indexing Pipeline

```text
ChatPRD GitHub Transcripts (.md / .txt)
                    │
                    ▼
          [scripts/ingest.py]
                    │
         1. Parse & Clean Markdown
            Extract: Episode Title, Guest Name, Date, Topic Tags
                    │
                    ▼
         2. Intelligent Semantic Chunking
            Chunk Size: 500-800 tokens
            Overlap: ~100 tokens
            Metadata: {episode, guest, topic, source_url}
                    │
                    ▼
         3. Vector Embedding Generation
            Dimension: 384 / 1536
                    │
                    ▼
         4. Batch Ingestion into PostgreSQL / pgvector
            Indexed via IVFFlat / HNSW for sub-millisecond retrieval
```

---

## 4. Security Architecture

1. **Untrusted HTML Rendering Isolation**:
   - Generated HTML is rendered exclusively within an `<iframe>` configured with:
     ```html
     <iframe
       sandbox="allow-scripts"
       csp="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline';"
       srcdoc="..."
     />
     ```
   - **Prohibited Flags**: `allow-same-origin` is omitted, guaranteeing the iframe has an opaque origin with zero access to `localStorage`, `sessionStorage`, `document.cookie`, or parent window DOM.
2. **Server-Side Payload Cleansing**:
   - Disallows `<object>`, `<embed>`, external `action` form submissions, and `javascript:` pseudo-protocols.
3. **Secret Protection**:
   - Cloud API keys (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) are accessed strictly on the backend server and never leaked in HTTP responses or telemetry.
