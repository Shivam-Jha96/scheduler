# Omnichannel & WhatsApp Message Scheduler — Documentation Portal

Welcome to the **Master Documentation Portal** for the **Omnichannel & WhatsApp Message Scheduler** platform.

This portal serves as the authoritative entry point and navigational index for all architectural specifications, system designs, business requirements, scale-out strategies, and executive briefing artifacts across the project lifecycle.

---

## 1. System Overview & Core Value Proposition

The **Omnichannel Message Scheduler** is an enterprise-grade, distributed message scheduling engine engineered to overcome the core technical and operational challenges of scheduled messaging across consumer and enterprise communication platforms (WhatsApp, Telegram, Discord, Slack, Viber, Signal, SMS, and Webhooks).

### Key Architectural Tenets:
1. **Pluggable Integration Architecture**: Core scheduling, state machine persistence, and queuing layers are completely decoupled from transport protocols via the typed `@scheduler/adapter-sdk` interface (`IChannelAdapter`) and dynamic IoC `AdapterRegistry`.
2. **Two-Tier Hybrid Distributed Scheduler**:
   - **Tier 1 (Durable State Ledger)**: PostgreSQL 16 database storing persistent schedule definitions. A lightweight poller runs every 60 seconds using `FOR UPDATE SKIP LOCKED` to stage impending jobs into the fast buffer.
   - **Tier 2 (Sub-Second In-Memory Buffer)**: BullMQ backed by Redis managing a 5-minute delayed execution sliding window for sub-second ($< 1.0\text{ s}$) dispatch accuracy.
3. **Mathematical Precision & Zero Drift**: Calendar-anchored timezone calculations using Luxon ensure zero minute ($0.0\text{ min}$) wall-clock drift across seasonal Daylight Saving Time (DST) boundaries and anchor-day preservation for month ends.
4. **Zero Double-Send Guarantee**: Cryptographic deduplication (deterministic SHA-256 idempotency locks) combined with Redis Redlock distributed mutexes ensures $0.0\%$ duplicate dispatches under network partitions or worker reboots.
5. **Anti-Ban Behavioral Pacing**: Natural typing simulation ($35\text{--}55\text{ ms/char}$), humanized read receipts, and presence status emulation protect companion device sessions against automated algorithmic bans.
6. **Compelling Unit Economics**: Operational footprint designed to cost $< \$30.00/\text{month}$ per 10,000 active scheduled messages (up to 85% savings compared to direct Meta Cloud API messaging conversation charges).

---

## 2. Master Document Matrix

All project documents are maintained in version-controlled Markdown (`.md`), interactive web presenter views (`.html`), and publication-grade high-resolution printable formats (`.pdf`).

| Document Name | Primary Focus | Available Formats | Key Specs & Scope |
|---|---|---|---|
| **Monorepo Boilerplate & Architecture Plan** | Codebase Architecture & Developer Velocity | [Markdown](monorepo_boilerplate_plan.md) | Turborepo layout (`apps/`, `adapters/`, `packages/`, `tools/`), `IChannelAdapter` SDK contract, Scaffolding CLI (`create-adapter`), Prisma schema, CI/CD pipeline |
| **Master Technical Plan (HLD & LLD)** | End-to-End System Design & WhatsApp Engine | [Markdown](whatsapp_message_scheduler_master_plan.md) · [HTML](WhatsApp_Scheduler_Master_Technical_Plan.html) · [PDF](WhatsApp_Scheduler_Master_Technical_Plan.pdf) | Dual operational models (Cloud API vs Baileys Companion), two-tier hybrid queuing, Redis Redlock idempotency, 60s Dead-Man Sweeper, anti-ban pacing, 5-phase roadmap |
| **Business & Functional Requirements (BRD & FRD)** | Business Rules & Product Specifications | [Markdown](whatsapp_scheduler_brd_frd.md) · [HTML](WhatsApp_Scheduler_BRD_FRD.html) · [PDF](WhatsApp_Scheduler_BRD_FRD.pdf) | SMART Objectives (BO-01 to BO-06), Business Rules (BR-01 to BR-05), Functional Modules (FR-AUTH, FR-WIZ, FR-CLI, FR-QUEUE, FR-RECUR, FR-SAFETY, FR-OBSERV) |
| **Omnichannel Scale-Out Architecture** | Multi-Platform Expansion & Adapter Matrix | [Markdown](omnichannel_messaging_scheduler_plan.md) · [HTML](Omnichannel_Scheduler_BRD_FRD_ScaleOut.html) · [PDF](Omnichannel_Scheduler_BRD_FRD_ScaleOut.pdf) | Platform landscape (WhatsApp, Viber, Discord, Signal, LINE, WeChat), transport feasibility, polymorphic schema, isolation boundaries, 5-phase scale-out |
| **Executive Briefing & Strategic Partner Q&A** | Commercial Defensibility & Partner FAQ | [HTML](Partner_Meeting_Briefing_QnA.html) · [PDF](Partner_Meeting_Briefing_QnA.pdf) | Meta policy defensibility, commercial viability, partner integration patterns, unit economics, ban risk mitigation, operational cost models |
| **Architecture Conversation Transcript** | Project History & Architectural Evolution | [Markdown](conversation_transcript.md) | Chronological 13-turn engineering discussion covering technical feasibility, trade-offs, architecture decisions, and document generation |

---

## 3. Deep-Dive Document Profiles

### 3.1 Monorepo Boilerplate & Architecture Plan
- **Primary File**: [`monorepo_boilerplate_plan.md`](monorepo_boilerplate_plan.md)
- **Format**: Markdown (`.md`)
- **Target Audience**: Software Engineers, Technical Leads, DevOps Engineers
- **Core Topics**:
  - Modular Turborepo structure decoupling core microservices from channel transports.
  - `@scheduler/adapter-sdk`: Defines `IChannelAdapter`, message payload interfaces, lifecycle methods (`initialize`, `connect`, `disconnect`), and send methods (`sendMessage`, `sendMedia`, `simulateTyping`).
  - `@scheduler/adapter-registry`: Dynamic inversion-of-control registry for loading and resolving adapters at runtime.
  - Scaffolding Tooling: Automated CLI (`npm run create:adapter -- --name <channel>`) generating complete boilerplate adapter code and test suites.
  - Contract Testing: `@scheduler/adapter-test-kit` validating adapter compliance against core engine expectations.

### 3.2 Master Technical Implementation Plan (HLD & LLD)
- **Primary Files**:
  - Markdown Source: [`whatsapp_message_scheduler_master_plan.md`](whatsapp_message_scheduler_master_plan.md)
  - Interactive HTML Presenter: [`WhatsApp_Scheduler_Master_Technical_Plan.html`](WhatsApp_Scheduler_Master_Technical_Plan.html)
  - Printable Publication PDF: [`WhatsApp_Scheduler_Master_Technical_Plan.pdf`](WhatsApp_Scheduler_Master_Technical_Plan.pdf)
- **Target Audience**: System Architects, Senior Backend Engineers, Reliability/SRE Teams
- **Core Topics**:
  - **The Sender Identity Paradox**: Why users cannot schedule messages from their personal identity using Meta's Cloud API without companion web socket emulation (Baileys Multi-Device protocol).
  - **Two-Tier Scheduling Engine Topology**: Detailed interaction diagrams between PostgreSQL (Tier 1 master ledger), Feeder Worker (`FOR UPDATE SKIP LOCKED`), and BullMQ / Redis (Tier 2 fast execution pool).
  - **Dead-Man's-Switch Sweeper Daemon**: 60-second background recovery thread reclaiming crashed, orphaned, or unacknowledged execution jobs.
  - **Anti-Ban Emulation Protocol**: Human typing simulation with character-count jitter, delivery receipts, and presence notifications.

### 3.3 Business Requirements (BRD) & Functional Requirements (FRD)
- **Primary Files**:
  - Markdown Source: [`whatsapp_scheduler_brd_frd.md`](whatsapp_scheduler_brd_frd.md)
  - Interactive HTML Presenter: [`WhatsApp_Scheduler_BRD_FRD.html`](WhatsApp_Scheduler_BRD_FRD.html)
  - Printable Publication PDF: [`WhatsApp_Scheduler_BRD_FRD.pdf`](WhatsApp_Scheduler_BRD_FRD.pdf)
- **Target Audience**: Product Managers, QA Engineers, Business Analysts, Scrum Masters
- **Core Topics**:
  - **SMART Business Objectives**: BO-01 (In-App Scheduling), BO-02 (Zero Double-Send), BO-03 (Anti-Ban Rate < 0.01%), BO-04 (Sub-Second Latency), BO-05 (Unit Economics < $30/mo), BO-06 (Zero DST Drift).
  - **Business Rules**: BR-01 (Meta Window Compliance), BR-02 (Anti-Spam Pacing), BR-03 (AES-256-GCM Zero-Knowledge Key Storage), BR-04 (Wall-Clock Recurrence Invariance), BR-05 (Omnichannel Isolation).
  - **Functional Requirements Matrix**: FR-AUTH (Pairing & Session Management), FR-WIZ (Conversational 5-step FSM), FR-CLI (Slash Commands), FR-QUEUE (Hybrid Scheduling), FR-RECUR (Luxon Recurrence Engine), FR-SAFETY (Cadence Pacing), FR-OBSERV (Prometheus Metrics & Health Checks).

### 3.4 Omnichannel Scale-Out Architecture
- **Primary Files**:
  - Markdown Source: [`omnichannel_messaging_scheduler_plan.md`](omnichannel_messaging_scheduler_plan.md)
  - Interactive HTML Presenter: [`Omnichannel_Scheduler_BRD_FRD_ScaleOut.html`](Omnichannel_Scheduler_BRD_FRD_ScaleOut.html)
  - Printable Publication PDF: [`Omnichannel_Scheduler_BRD_FRD_ScaleOut.pdf`](Omnichannel_Scheduler_BRD_FRD_ScaleOut.pdf)
- **Target Audience**: Solutions Architects, Platform Engineers, Product Strategists
- **Core Topics**:
  - Multi-platform comparative feasibility analysis across 7 major platforms: WhatsApp, Telegram, Discord, Slack, Viber, Signal, and generic Webhooks.
  - Polymorphic database design supporting arbitrary channel metadata without destructive schema migrations.
  - Fault isolation boundary: Failure of one channel adapter (e.g. Baileys socket disconnect) has zero ripple effect on Discord, Telegram, or Webhook dispatches.
  - 5-Phase Expansion Roadmap from MVP WhatsApp to enterprise multi-tenant unified messaging hub.

### 3.5 Executive Briefing & Strategic Partner Q&A
- **Primary Files**:
  - Interactive HTML Presenter: [`Partner_Meeting_Briefing_QnA.html`](Partner_Meeting_Briefing_QnA.html)
  - Printable Publication PDF: [`Partner_Meeting_Briefing_QnA.pdf`](Partner_Meeting_Briefing_QnA.pdf)
- **Target Audience**: Executive Stakeholders, Investors, Strategic Partners, Commercial Leads
- **Core Topics**:
  - Commercial defensibility against Meta: Personal companion device scheduling vs enterprise Cloud API.
  - Monetization vectors: Multi-tenant SaaS subscriptions, volume-based quotas, enterprise SLA tiers.
  - Risk governance & mitigation: Account ban rate management, privacy adherence, zero-knowledge payload encryption.
  - Unit economics and cloud operational cost breakdown.

### 3.6 Architecture Conversation Transcript
- **Primary File**: [`conversation_transcript.md`](conversation_transcript.md)
- **Format**: Markdown (`.md`)
- **Target Audience**: Engineering Historians, Forensic Auditors, Onboarding Engineers
- **Core Topics**:
  - Chronological 13-turn engineering log documenting the genesis of the system architecture, mathematical DST proofs, trade-off analyses, and decision records.

---

## 4. Role-Based Reading Paths

To optimize onboarding and review efficiency, follow the targeted path designed for your role:

```
┌────────────────────────────────────────────────────────────────────────┐
│                          ROLE READING PATHWAYS                         │
└────────────────────────────────────────────────────────────────────────┘

 [1. Backend & Platform Developers]
   │
   ├─► 1. docs/monorepo_boilerplate_plan.md (Monorepo Layout & Plugin SDK)
   ├─► 2. docs/whatsapp_message_scheduler_master_plan.md (Two-Tier Scheduler & Redis)
   └─► 3. docs/omnichannel_messaging_scheduler_plan.md (IChannelAdapter Contract)

 [2. System Architects & SREs]
   │
   ├─► 1. docs/WhatsApp_Scheduler_Master_Technical_Plan.html (Mermaid Topologies)
   ├─► 2. docs/whatsapp_message_scheduler_master_plan.md (Redlock, Feeder, Dead-Man)
   └─► 3. docs/Omnichannel_Scheduler_BRD_FRD_ScaleOut.html (Polymorphic DB & Isolation)

 [3. Product Managers, QA & Scrum Masters]
   │
   ├─► 1. docs/WhatsApp_Scheduler_BRD_FRD.html (Interactive BRD & FRD Search)
   ├─► 2. docs/whatsapp_scheduler_brd_frd.md (Acceptance Criteria & Epics)
   └─► 3. docs/Omnichannel_Scheduler_BRD_FRD_ScaleOut.html (Traceability Matrix)

 [4. Executive Leadership, Investors & Commercial Partners]
   │
   ├─► 1. docs/Partner_Meeting_Briefing_QnA.html (Strategic Overview & FAQ)
   ├─► 2. docs/Partner_Meeting_Briefing_QnA.pdf (Printable Executive Briefing)
   └─► 3. docs/WhatsApp_Scheduler_BRD_FRD.pdf § Section 1.5 (Unit Economics)
```

---

## 5. Document Build & Generation Pipeline

All HTML presentation decks and PDF deliverables are programmatically compiled from source markdown and structured templates using headless browser automation scripts in `scripts/`.

### 5.1 Compilation Engine Architecture
The document build pipeline leverages **Headless Google Chrome / Microsoft Edge** via CLI execution flags:
- `--headless=new`: Modern Chrome headless rendering engine.
- `--disable-gpu`: Headless stability in continuous integration environments.
- `--no-pdf-header-footer`: Clean document edge-to-edge rendering without browser stamps.
- `--virtual-time-budget=6000`: Allows 6,000ms for client-side JavaScript execution (Mermaid.js diagram rendering and Tailwind CSS styles) before PDF capture.
- `--run-all-compositor-stages-before-draw`: Forces complete layout rendering and font rasterization prior to PDF export.

### 5.2 Build Script Catalog

| Script | Primary Output | Description |
|---|---|---|
| `scripts/build_v2_plan.py` | `docs/WhatsApp_Scheduler_Master_Technical_Plan.html`<br/>`docs/WhatsApp_Scheduler_Master_Technical_Plan.pdf` | Compiles the Rectified V2.0 Master Technical Plan with dark-mode Tailwind UI, dynamic Mermaid diagrams, and database DDL blocks. |
| `scripts/build_brd_frd_html_pdf.py` | `docs/WhatsApp_Scheduler_BRD_FRD.html`<br/>`docs/WhatsApp_Scheduler_BRD_FRD.pdf` | Builds the interactive BRD/FRD presentation deck with live requirement filtering, KPI stat cards, and full acceptance criteria. |
| `scripts/build_hld_lld_html.py` | Presenter HTML | Compiles the High-Level & Low-Level Design specification with interactive architectural diagrams. |
| `scripts/build_pdf.py` | Target PDF files | Generic Markdown-to-PDF compilation pipeline using Python `markdown` with table, TOC, and fenced code extensions. |
| `scripts/generate_presenter_html.py` | Presenter HTML | Compiles standalone presentation views of markdown specifications. |

### 5.3 Executing Document Builds
To recompile all documentation artifacts locally:

```powershell
# Ensure Python prerequisites are available
pip install markdown

# Rebuild Master Technical Plan (HTML + PDF)
python scripts/build_v2_plan.py

# Rebuild BRD & FRD (HTML + PDF)
python scripts/build_brd_frd_html_pdf.py
```

---

## 6. Monorepo Organization & Code Layout

The project follows standard Turborepo conventions:

```
scheduler/
├── apps/                        # Application services
│   ├── api-gateway/             # Fastify webhook and API ingest
│   ├── scheduler-feeder/        # 60s PostgreSQL Look-Ahead Poller daemon
│   ├── delivery-worker/         # BullMQ millisecond execution pool
│   └── web-dashboard/           # Next.js administrative control plane
│
├── adapters/                    # Pluggable channel transport implementations
│   ├── whatsapp-baileys/        # Companion device socket connection
│   ├── whatsapp-cloud-api/      # Official Meta Graph REST API
│   ├── telegram/                # Telegram Bot API adapter
│   ├── discord/                 # Discord Gateway Bot adapter
│   ├── slack/                   # Slack Bolt API adapter
│   └── webhook/                 # Generic outbound HTTP webhook adapter
│
├── packages/                    # Shared internal libraries
│   ├── adapter-sdk/             # IChannelAdapter TypeScript interface & port
│   ├── adapter-registry/        # Inversion-of-Control adapter manager
│   ├── adapter-test-kit/        # Automated contract test suite
│   ├── database/                # Prisma client & PostgreSQL schemas
│   ├── queue/                   # BullMQ connection & job abstractions
│   ├── crypto/                  # AES-256-GCM envelope encryption
│   └── temporal/                # Luxon timezone and DST calculation engine
│
├── docs/                        # Master Documentation Portal (this directory)
│   ├── README.md                # Master Documentation Index & Guide
│   ├── monorepo_boilerplate_plan.md
│   ├── whatsapp_message_scheduler_master_plan.md
│   ├── WhatsApp_Scheduler_Master_Technical_Plan.html / .pdf
│   ├── whatsapp_scheduler_brd_frd.md
│   ├── WhatsApp_Scheduler_BRD_FRD.html / .pdf
│   ├── omnichannel_messaging_scheduler_plan.md
│   ├── Omnichannel_Scheduler_BRD_FRD_ScaleOut.html / .pdf
│   ├── Partner_Meeting_Briefing_QnA.html / .pdf
│   └── conversation_transcript.md
│
├── scripts/                     # Document build & headless PDF compilation scripts
├── tools/                       # Developer velocity tooling (create-adapter CLI)
└── PROJECT.md                   # Monorepo Roadmap & Milestone Decomposition
```

---

## 7. Contribution & Document Maintenance Guidelines

- **Source of Truth**: When making changes to system behavior or architecture, update the corresponding Markdown specification file first (`whatsapp_message_scheduler_master_plan.md`, `whatsapp_scheduler_brd_frd.md`, or `omnichannel_messaging_scheduler_plan.md`).
- **Artifact Recompilation**: Run the appropriate Python build script in `scripts/` to refresh the associated `.html` and `.pdf` files.
- **Portability**: Maintain relative links within the `docs/` tree. Avoid absolute filesystem paths (`file:///C:/...`).
