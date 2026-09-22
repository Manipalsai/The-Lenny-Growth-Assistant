# UI/UX Design System & Specification
# The Lenny Growth Assistant

---

## 1. Design Principles & Aesthetic Direction

The design of **The Lenny Growth Assistant** is crafted to feel like a tier-one internal product built for product and growth leaders (reminiscent of Claude, Linear, and ChatGPT):
- **Clarity Over Clutter:** High information density without cognitive overload. Clean lines, generous padding, and clear typographic hierarchy.
- **Dynamic & Responsive Split-Pane:** Chat on the left; instant, live Claude-style Artifact Viewer on the right.
- **Grounding Transparency:** Every factual insight links directly to verifiable citations. Citations are interactive badges that reveal supporting transcript text in a dedicated Source Inspector.
- **Predictive Velocity:** Instant follow-up chips ("Create Ship 30 Essay", "Build 1-Page Framework", "Compare Guest Tactics") accelerate executive workflows.

---

## 2. Layout & Information Architecture

### Desktop Layout (Split-Pane Grid)
```text
+---------------------------------------------------------------------------------------+
|  [Logo] Lenny Growth Assistant      [Status: Ollama / Cloud]   [New Chat (+)]  [Docs] |
+------------------+----------------------------------------+---------------------------+
| SIDEBAR          | CHAT PANEL                             | ARTIFACT VIEWER (Split)   |
| - Recent Chats   | - Grounded Answers                     | [Preview] [Code] [Copy]   |
| - Session List   | - Citations: [Brian Chesky - Moats]    | ------------------------- |
| - Settings Modal | - Source Inspector Drawer Trigger      | Live Sandboxed Rendering  |
| - Ingestion Info | - Suggested Action Chips               | of Frameworks / HTML      |
|                  | - Streaming Response Input Box         | Dashboards / Essays       |
+------------------+----------------------------------------+---------------------------+
```

### Tablet & Mobile Responsive Behavior
- **Desktop ($\ge 1024\text{px}$):** Persistent two-column split-pane (50% Chat / 50% Artifact).
- **Tablet ($768\text{px} - 1023\text{px}$):** Collapsible right pane with tabbed switcher.
- **Mobile ($< 768\text{px}$):** Full-width chat view; when an artifact is generated or selected, it slides up smoothly as an interactive full-screen drawer.

---

## 3. Visual System & Typography

- **Color Palette (Dark & Modern Neutral):**
  - Background Base: `#0f172a` (Slate 900)
  - Surface Card / Sidebar: `#1e293b` (Slate 800)
  - Borders & Dividers: `#334155` (Slate 700)
  - Primary Accent: `#38bdf8` (Sky 400) & `#6366f1` (Indigo 500)
  - Text Primary: `#f8fafc` (Slate 50)
  - Text Muted: `#94a3b8` (Slate 400)
  - Citation Badge: `#0284c7` (Sky 600) with hover glow
- **Typography:**
  - Modern Sans-Serif font stack: `Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`.
  - Monospace font stack for code and JSON: `"JetBrains Mono", "Fira Code", monospace`.

---

## 4. Standout UX Features

1. **Source Inspector:**
   - Clicking any citation badge opens a drawer showing:
     - Episode Name & Guest Photo/Avatar
     - Exact timestamp / chapter tag
     - Verbatim excerpt from the transcript
     - Relevance match indicator
2. **Retrieval Transparency Banner:**
   - While streaming, subtle micro-indicator displays:
     `"Scanning 250+ Lenny podcast transcripts... Found 5 supporting passages"`
3. **Artifact Actions Bar:**
   - Every artifact preview includes:
     - `Preview` / `Source Code` toggle
     - `Copy Markdown / HTML` button with instant toast notification
     - `Regenerate with Feedback` button
     - `Download File (.html / .md)`
4. **Suggested Follow-up Action Chips:**
   - Automatically suggested after every grounded response:
     - `Turn into Ship 30 Essay`
     - `Create Interactive HTML Dashboard`
     - `What did other guests say on this topic?`
