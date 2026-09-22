# Product Requirements Document (PRD)
# The Lenny Growth Assistant

**Status:** Approved  
**Author:** Forward Deployed Engineer & AI/RAG Architect  
**Version:** 1.0.0  
**Target Delivery:** Production Grade  

---

## 1. Executive Summary & Problem Statement

Lenny Rachitsky's podcast represents the premier repository of knowledge on product management, growth, hiring, strategy, and company building, featuring interviews with hundreds of the world's leading practitioners (e.g., Brian Chesky, Shreyas Doshi, Elena Verna, Gustaf Alströmer).

However, accessing this knowledge today suffers from severe frictions:
1. **Unsearchable Wisdom:** Insights are trapped across hundreds of hours of audio and massive transcript text files. Keyword searches lack conceptual understanding.
2. **Hallucination & Lack of Attribution:** Standard LLMs hallucinate general product advice and misattribute quotes to speakers or episodes.
3. **Inactionable Formats:** Growth leaders and PMs do not just want conversational chat; they need structured deliverables—such as Ship 30 for 30 essays, visual execution frameworks, and interactive HTML dashboards.
4. **Environment Constraints:** Enterprise and local privacy requirements demand local model support (Ollama), while scalable production environments require seamless cloud model execution (OpenAI/Anthropic).

**The Lenny Growth Assistant** solves this by providing a grounded conversational intelligence system built strictly over Lenny's Podcast transcripts with verifiable citations, structured essay/artifact creation, a sandboxed Claude-style artifact viewer, and provider-agnostic resilience.

---

## 2. Target Persona & Jobs-to-be-Done (JTBD)

### Primary Persona
- **Role:** Product Manager, VP of Product, Growth Lead, Early-stage Founder.
- **Context:** Making high-stakes decisions under time pressure (e.g., defining North Star metrics, planning PLG funnels, redesigning onboarding, pricing experiments).
- **Core Need:** Authoritative, real-world examples from proven operators without wading through noise or risking hallucinations.

### Jobs-to-be-Done (JTBD)
> *"When I face a strategic product or growth challenge, I want to quickly synthesize proven frameworks and real-world tactics from experienced operators across Lenny's interviews, so that I can validate my strategy, present a concrete framework to my team, and publish actionable playbooks without manually reading through transcripts."*

---

## 3. Success Metrics & Measurement Methodology

| Metric | Target | Measurement Methodology |
| :--- | :--- | :--- |
| **Retrieval Citation Accuracy** | $\ge 95\%$ | Automated verification test checking that every factual claim citation maps to an exact retrieved transcript chunk ID, episode, and speaker. |
| **Grounded-Answer Accuracy** | $\ge 90\%$ | RAG evaluation testing that model outputs contain zero ungrounded facts not present in retrieved context. |
| **Out-of-Domain Refusal Rate** | $100\%$ | Evaluated with negative test queries (e.g., physics, unrelated coding, celebrity gossip) confirming system explicitly refuses with transcript scope notice. |
| **First-Token Latency (Streaming)** | $\le 1.2\text{s}$ (Cloud) / $\le 2.5\text{s}$ (Local) | Measured at client receiver via Server-Sent Events (SSE) from user prompt submission. |
| **Artifact Render Success Rate** | $100\%$ | Automated rendering validation verifying valid HTML/CSS/Markdown in sandboxed container without DOM errors. |
| **Model Fallback Success Rate** | $100\%$ | Unit & failure simulation tests verifying automatic handover to Cloud provider when Ollama daemon is unreachable or model missing. |
| **Automated Test Pass Rate** | $100\%$ | Pytest test suite covering chunking, embeddings, security XSS sanitization, APIs, and provider switching. |

---

## 4. Scope

### In-Scope (Phase 1–16)
- **High-Quality Grounded RAG:** Intelligent chunking (500–800 tokens, 100 overlap), semantic embeddings, similarity thresholding ($\ge 0.70$), source deduplication, and diversity filtering.
- **Verifiable Citations:** Exact episode name, guest name, timestamp/topic tag, and expandable Source Inspector.
- **Conversational Memory:** Independent session persistence, contextual multi-turn follow-ups, and session isolation.
- **Dual LLM Architecture:** Local Ollama (`llama3.2:3b`) with automatic fallback to Cloud LLMs (OpenAI `gpt-4o-mini` / Anthropic `claude-3-5-sonnet`) and UI provider switching.
- **Specialized Skills:**
  - *Grounded QA Skill*: Direct, evidence-grounded answers.
  - *Ship 30 for 30 Skill*: ~1,250-word structured essays with hook, tension, H2/H3 subheads, and concrete takeaways.
  - *Artifact Generator Skill*: Structured Markdown and HTML/CSS dashboards and playbooks.
- **Claude-Style Artifact Viewer:** Split-screen preview, isolated iframe sandbox, copy/code toggle, and mobile responsive drawer.
- **Security Hardening:** Strict iframe sandboxing (`allow-scripts`, no same-origin, no parent DOM, no storage access), server-side XSS payload stripping.
- **Production Packaging:** PostgreSQL + pgvector support, local SQLite fallback, Docker Compose orchestration, and Vercel cloud deployment.

### Out-of-Scope (Explicit Trade-offs)
- Multi-tenant enterprise SSO (OAuth2 / SAML) – single-user / team access is prioritized for velocity and evaluation simplicity.
- Live audio speech-to-text generation – transcripts are ingested from the authoritative ChatPRD transcript archive.

---

## 5. Risk Matrix & Mitigation Strategies

| Risk Category | Risk Description | Severity | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **Hallucination** | LLM inventing quotes or mixing outside knowledge. | High | Strict prompt system constraints, similarity cutoff, citation validation, and explicit refusal if no chunks exceed confidence threshold. |
| **Retrieval Failure** | User query uses colloquial phrasing not matching transcript keywords. | Medium | Semantic dense vector embeddings, query expansion, and source diversity filtering. |
| **Local LLM Absence** | User runs application locally without Ollama installed or daemon running. | High | Graceful fallback engine: catches connection errors, notifies UI cleanly via provider badge, and routes to Cloud provider if configured. |
| **XSS / Malicious HTML** | Generated HTML artifact contains malicious scripts or redirects. | Critical | Sandboxed `<iframe>` with isolated origin (`sandbox="allow-scripts"` without `allow-same-origin`), stripping cookie/parent access, and CSP enforcement. |
| **Database Unavailability** | PostgreSQL not installed or down on local machine. | High | Resilient dual-backend database abstraction: automatically defaults to local SQLite + vector storage if PostgreSQL is unreachable. |
| **Cloud Cost Spike** | Unbounded token generation on cloud APIs. | Medium | Hard token ceilings (`max_tokens: 2048`), streaming timeouts, and default usage of cost-efficient models (`gpt-4o-mini`). |
