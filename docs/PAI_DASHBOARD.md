# PAI Control Dashboard Functionality Matrix

The PAI Control Dashboard, orchestrating the `~/.claude/MEMORY` system via `PMServer.ts`, exposes an extensive GUI on `http://localhost:8888`. It acts as the primary cockpit for tracking cross-module tasks, LLM context windows, and structural awareness.

## 1. Global Navigation & Action Bar

The persistent header exposes immediate health metrics and global CRUD endpoints:

* **Metrics Ribbon:** 7 Missions (6 Active), 19 Projects, 831 Tasks (397 Done, 0 Overdue, 0 Blocked).
* **Action Buttons:**
  * `+ Mission`: Deploys a modal interface for declaring a high-level operational objective.
  * `+ Project`: Deploys a modal interface for instantiating a sub-goal tied to a specific mission.
* **14 Core Subsystems:** Access to Analytics, Awareness, Blockers, Board, Calendar, Email, Data, Dispatch, Git, Integration, Interview, Network, Projects, and Timeline.

## 2. Structural & Tracking Views

* **Analytics/Data:** Granular tabular interfaces for exploring Active/Planning/Completed models. Includes full metric aggregation (completion percentage, linked task ratio) and sorting tools.
* **Board (Kanban):** A global Kanban visualization managing cross-project state pipelines: *Active, Planning, In Progress, Blocked, Paused, Completed.*
* **Timeline (Gantt):** A global rendering of all active projects across a multi-month calendar, visualizing bottlenecks and multi-step duration logic.
* **Network Maps:** Force-directed 2D maps demonstrating the parent-child node graph (Mission → Project → Task). Offers semantic zooming and tag-based visual clustering.

## 3. Agents & Dispatch Execution

* **Dispatch Mode:** Exposes API wrappers to delegate queued workflow processes to automated AI subroutines. Summarizes repo states, scopes future objectives, performs risk assessments, and auto-executes 'Next Enactable Step' strategies directly from the interface.
* **Interview Mode:** Allows establishing guided, persistent multi-turn conversational agents dedicated to specific role-playing (e.g., scoping product features, designing architectural diagrams based on active projects).

## 4. Integration & Operations

* **Git Synchronization:** Complete GUI over raw `git` hooks. Provides push/pull/sync buttons, connection status monitoring, and repo linking.
* **Email & Communications:** Bridges tasks with outbound agent actions via AgentMail/Gmail templates. Supports configuring Ollama instances for offline parsing.
* **Data Portability:** Lossless conversion and syncing. Exports operational state to JSON/CSV/Markdown. Supports state-injection via JSON data imports.

## Technical Considerations

The GUI relies heavily on a real-time reactive frontend fetching from the local `/api` REST layer. Minor exceptions exist (e.g. `/api/calendar/events` 500 block during headless operation), but the foundation remains unconditionally resilient.
