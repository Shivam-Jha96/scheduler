# Omnichannel & WhatsApp Message Scheduler — Documentation Portal

Welcome to the **Master Documentation Portal** for the **Omnichannel & WhatsApp Message Scheduler** platform.

This portal serves as the authoritative entry point and navigational index for all architectural specifications, system designs, business requirements, scale-out strategies, and executive briefing artifacts across the project lifecycle.

---

## 1. System Overview & Core Value Proposition

The **Omnichannel Message Scheduler** is an enterprise-grade, distributed message scheduling engine engineered to overcome the core technical and operational challenges of scheduled messaging across consumer and enterprise communication platforms (WhatsApp, Telegram, Discord, Slack, Viber, Signal, SMS, and Webhooks).

### Key Architectural Tenets:
1. **Pluggable Integration Architecture**: Core scheduling, state machine persistence, and queuing layers are completely decoupled from transport protocols via the typed `@scheduler/adapter-sdk` interface (`IChannelAdapter`) and dynamic IoC `AdapterRegistry`.
2. **PostgreSQL-Native ACID Queuing Engine**:
   - Schedule creation and queue enrollment execute in a single atomic ACID transaction (`BEGIN; INSERT INTO scheduled_jobs; SELECT pgboss.send(...); COMMIT;`) within PostgreSQL 16 via `pg-boss`, eliminating the distributed dual-write hazard and phantom schedules.
   - Redis 7 is retained strictly as an ephemeral, zero-PII cache for distributed locks (`SETNX`), rate limiting token buckets, and interactive wizard session drafts.
3. **Zero-Trust Network Segmentation & Ingress**:
   - Cloudflare Tunnels (`cloudflared`) enforce **0 open inbound public ports** on the VPS host firewall.
   - Administrative SSH is restricted exclusively to private **Tailscale WireGuard Mesh VPN** overlay IPs (`100.x.y.z`) with SSO + FIDO2 MFA (public port 22 disabled).
4. **End-to-End PII Data Protection & Compliance**:
   - Thin-pointer queuing stores zero recipient phone numbers or message bodies in RAM.
   - Two-tier AWS KMS envelope encryption (FIPS 140-3 HSM Root KEK -> tenant DEK via AES-256-GCM).
   - Cryptographic Blind Indexing (`recipient_bindex = HMAC-SHA256(phone, salt)[0..31]`) enables <0.1ms B-tree lookups without plaintext phone exposure.
   - Right-to-be-Forgotten & DPDP Act 2023 Crypto-Shredding: deleting a tenant DEK mathematically annihilates all historical records ($2^{256}$ complexity).
5. **Mathematical Precision & Zero Drift**: Calendar-anchored timezone calculations using Luxon ensure zero minute ($0.0\text{ min}$) wall-clock drift across seasonal Daylight Saving Time (DST) boundaries and anchor-day preservation for month ends.
6. **Zero Double-Send Guarantee**: Cryptographic deduplication (deterministic SHA-256 idempotency locks) combined with Redis distributed mutexes and Baileys socket `msgId` injection ensures $0.0\%$ duplicate dispatches under network partitions or worker reboots.
7. **Anti-Ban Behavioral Pacing**: Natural typing simulation ($35\text{--}55\text{ ms/char}$), humanized read receipts, and presence status emulation protect companion device sessions against automated algorithmic bans.
8. **Compelling Unit Economics**: Operational footprint designed to cost strictly **$9.50 – $25.90/month** on a hardened Linux VPS (Hetzner CPX21 / DigitalOcean Droplet), well within the $30.00–$50.00/month budget.

---

## 2. Master Document Matrix

All project documents are maintained in version-controlled Markdown (`.md`), interactive web presenter views (`.html`), publication-grade high-resolution printable formats (`.pdf`), and collaborative cloud formats in Google Drive.

> 📁 **Dedicated Google Drive Subfolder**: All refined deliverables and Preeti recommendations are published to [**Refined Architecture & Preeti Recommendations**](https://drive.google.com/drive/folders/1ccvVj-GPDfzQr1SP7ZDHv-TKi2ZFc5cE) (Folder ID: `1ccvVj-GPDfzQr1SP7ZDHv-TKi2ZFc5cE`).

| Document Name | Primary Focus | Available Formats | Key Specs & Scope |
|---|---|---|---|
| **Document 1: Preeti's Recommendations and Summary Doc** | Strategic Analysis, Technical Audit & 5-Doc Synthesis | [Markdown](preeti_recommendations_and_summary.md) · [Google Doc](https://docs.google.com/document/d/1q0tzWkIbMMXOTNz4StZ-acAwl7iSTcAqXiqQjjYZY0Y/edit?usp=drivesdk) · [Drive MD](https://drive.google.com/file/d/1WYGa3TUXocQobcgeZ6L_Jv7yiJk05rms/view?usp=drivesdk) | Exhaustive synthesis of all 5 documents authored/updated by Preeti (`preeti.choraria0@gmail.com`). Complete deprecation of Baileys in production, ban/compliance risk mitigation, 20-user VPS bottleneck elimination (50k+ users on 4GB VPS), official operational models (A, B, C), 4 personal scheduling architectures, PostgreSQL 16 DDL migrations, dual token-bucket rate limiting (80 mps global + 1 msg/6s pair), Graph API error taxonomy, quantitative SLAs (Macro-F1 >= 0.92, ECE <= 0.05, Fast-ACK < 20ms, Drift p95 < 1s), Vitest + Testcontainers + WireMock testing stack, and ISO 27001/27701/25010/42001 compliance. |
| **Document 2: REA MS Teams Findings & Architectural Blueprint** | MS Teams Forensic Reverse-Engineering & 7-Layer Deep Dive | [Markdown](ms_teams_reverse_engineering_findings.md) · [Google Doc](https://docs.google.com/document/d/1ZbLMEipVlXDosNS30WQRYa5VmSXIB1C6XqvvKoRC-vA/edit?usp=drivesdk) · [Drive MD](https://drive.google.com/file/d/1a67LSozozafosVld8Yx9Dk5fTz2P-ysG/view?usp=drivesdk) | Exhaustive 7-layer architectural blueprint: Layer 1 (Client UX, LevelDB `skypeMessageLocal` optimistic caching, scheduled draft banner docked above compose box, edit/cancel/send-now workflows); Layer 2 (Network protocols, `/api/chatsvc/...`, virtual container `48:drafts`, JSON payload schemas, headers); Layer 3 (Trouter full-duplex WebSocket signaling, HTTP long polling fallback, client ACK); Layer 4 (Azure Cosmos DB `DraftMessages` container partitioned by `userId`, document schema, 8-day TTL auto-purge, draft lifecycle state machine); Layer 5 (Azure Service Bus `ScheduledEnqueueTimeUtc`, zero-polling dormant partition indexes, PeekLock workers, 64-bit `SequenceNumber` $O(1)$ cancellation, atomic CAS via `_etag` headers with HTTP 412 handling); Layer 6 (Continuous Access Evaluation / CAE at trigger time via OpenID CAEP/SSE push streams to a sub-0.5ms in-memory revocation cache, conversation roster check, dynamic Purview DLP pre-flight scans, compliance boundary separation where unindexed `48:drafts` are shielded from eDiscovery/Legal Hold while post-delivery messages are mirrored to Exchange Online's hidden `TeamChat` mailbox folder); Layer 7 (Failure modes & 12 edge cases). |
| **Document 3: Refined HLD & Target Stack Specification (v3.0)** | Harmonized Target Architecture, Schemas & Production Stack | [Markdown](refined_hld_and_target_stack.md) · [Google Doc](https://docs.google.com/document/d/14OxFhry9f7kfBpAs9OljzgKH2WovWqpwbckFfhigtLU/edit?usp=drivesdk) · [Drive MD](https://drive.google.com/file/d/1n7l6m1EafcueASZXv0jQqCa0JjcvCdV7/view?usp=drivesdk) | Definitive production architecture integrating Preeti's rectifications and MS Teams REA innovations. 10-dimension comparative matrix (Old HLD vs Refined HLD vs Teams Learnings); Quad-Tier Message Delivery Topology (Model A with Escalating Nudge, Model B Business Coexistence, Model C Official Bot Relay, Hybrid Edge-Triggered Companion via iOS Shortcuts / Android Intents, and power-user BYON Bridge); 4-Step Trigger-Time Pre-Flight Compliance Gate; Optimistic CAS Concurrency & Two-Phase Resilient Queuing (Phase 1 pure pg-boss ACID, Phase 2 Two-Tier Partitioned Feeder + Sweeper Dead-Man's Switch); Canonical PostgreSQL 16 DDL; Sub-50ms regex bypass; Calibrated NLU (ECE <= 0.05); Luxon calendar-anchored month-end recurrence math; Lean $8.90–$12.50/mo OpEx on Hetzner CPX21 supporting 50,000+ users. |
| **Microsoft Teams Reverse Engineering & WhatsApp Scheduler Master Architecture** | Teams Decompilation, Protocol Specs & Enterprise WhatsApp Translation | [Markdown](microsoft_teams_and_whatsapp_scheduler_architecture.md) | Comprehensive decompilation of Microsoft Teams `chatsvc`, `48:drafts`, Cosmos DB, Service Bus `ScheduledEnqueueTimeUtc`, Substrate/Exchange compliance, CAE/DLP pre-flight gates, and 10-dimension translation to Enterprise WhatsApp Scheduler (24h Care Window Tri-Tier Fallback, Token Bucket, Anti-Ban Pacing, Two-Tier PostgreSQL 16 + Delayed Queue, Full DDL, $12–28/mo OpEx). |
| **Infrastructure Architecture & Zero-Trust Blueprint** | Infrastructure Feasibility, Security & Cost Plan | [Markdown](whatsapp_scheduler_infrastructure_blueprint.md) · [Google Doc](https://docs.google.com/document/d/1SD4jJ841wNVjGjXn0UzzU65fH2M7Jf5I9Nbuywqgiu0/edit) | Hetzner CPX21 vs DO Droplet ($9.50–$25.90/mo), Cloudflare Tunnels (0 open ports), Tailscale VPN, AWS KMS envelope encryption, HMAC blind index, 7 visual diagrams |
| **Master Technical Plan (HLD & LLD)** | End-to-End System Design & WhatsApp Engine | [Markdown](whatsapp_message_scheduler_master_plan.md) · [HTML](WhatsApp_Scheduler_Master_Technical_Plan.html) · [PDF](WhatsApp_Scheduler_Master_Technical_Plan.pdf) | Dual operational models, PostgreSQL-native ACID queuing (`pg-boss`), zero-trust network ingress, PII encryption & crypto-shredding, anti-ban pacing, 4-phase roadmap |
| **Business & Functional Requirements (BRD & FRD)** | Business Rules & Product Specifications | [Markdown](whatsapp_scheduler_brd_frd.md) · [Google Doc](https://docs.google.com/document/d/1PjNencZ1ASDM4fRqWGSo6nxiiR1KnmmjQe62Jbx89gE/edit) · [HTML](WhatsApp_Scheduler_BRD_FRD.html) · [PDF](WhatsApp_Scheduler_BRD_FRD.pdf) | SMART Objectives (BO-01 to BO-09), Business Rules (BR-01 to BR-06), Modules (FR-AUTH through FR-NET), ACID Queuing, PII Guardrails |
| **Monorepo Boilerplate & Architecture Plan** | Codebase Architecture & Developer Velocity | [Markdown](monorepo_boilerplate_plan.md) | Turborepo layout (`apps/`, `adapters/`, `packages/`, `tools/`), `IChannelAdapter` SDK contract, Scaffolding CLI (`create-adapter`), Prisma schema, CI/CD pipeline |
| **Omnichannel Scale-Out Architecture** | Multi-Platform Expansion & Adapter Matrix | [Markdown](omnichannel_messaging_scheduler_plan.md) · [HTML](Omnichannel_Scheduler_BRD_FRD_ScaleOut.html) · [PDF](Omnichannel_Scheduler_BRD_FRD_ScaleOut.pdf) | Platform landscape (WhatsApp, Viber, Discord, Signal, LINE, WeChat), transport feasibility, polymorphic schema, isolation boundaries, 5-phase scale-out |
| **Executive Briefing & Strategic Partner Q&A** | Commercial Defensibility & Partner FAQ | [HTML](Partner_Meeting_Briefing_QnA.html) · [PDF](Partner_Meeting_Briefing_QnA.pdf) | Meta policy defensibility, commercial viability, partner integration patterns, unit economics, ban risk mitigation, operational cost models |
| **Architecture Conversation Transcript** | Project History & Architectural Evolution | [Markdown](conversation_transcript.md) | Chronological engineering discussion covering technical feasibility, trade-offs, architecture decisions, and document generation |

---

## 3. Deep-Dive Document Profiles

### 3.0A Document 1: Preeti's Recommendations and Summary Doc
- **Reference**: `REC-PREETI-SUMMARY-001`
- **Primary Files**:
  - Local Markdown: [`preeti_recommendations_and_summary.md`](preeti_recommendations_and_summary.md)
  - Google Doc: [Native Google Doc](https://docs.google.com/document/d/1q0tzWkIbMMXOTNz4StZ-acAwl7iSTcAqXiqQjjYZY0Y/edit?usp=drivesdk)
  - Google Drive Markdown: [Drive File Attachment](https://drive.google.com/file/d/1WYGa3TUXocQobcgeZ6L_Jv7yiJk05rms/view?usp=drivesdk)
- **Target Audience**: Founders, Principal Architects, Lead Backend & QA Engineers
- **Core Topics**:
  - **Comprehensive 5-Document Synthesis**: Detailed technical breakdown of all documents authored/updated by Preeti (`preeti.choraria0@gmail.com`) in the shared Google Drive folder.
  - **Deprecation of Baileys in Production**: Technical rationale for dropping `@whiskeysockets/baileys` from hosted production (SIM bans, protocol schema fragility, 20-session/4GB VPS memory bottleneck, and compliance barriers).
  - **Reconciled Operational Models**: Model A (Assistive `wa.me` CTA Redirect with 24h Customer Service Window fee catch), Model B (Official WhatsApp Business App Coexistence via `smb_message_echoes`), and Model C (Official Bot Relay with Bob opt-in).
  - **4 Alternative Personal User Architectures**: Hybrid Edge-Triggered Companion (iOS Shortcuts / Android Helper), Zero-Friction Escalating Nudge + 1-Tap Deep Link + Bot Relay Fallback, Bring-Your-Own-Node (BYON) Desktop Bridge, and Group-First Viral Scheduler Bot.
  - **Canonical PostgreSQL 16 DDL**: Dropping legacy session tables, adding `recipient_consents`, and adding fields to `channel_accounts` and `scheduled_jobs`.
  - **Dual-Layer Rate Limiting**: Redis Lua script enforcing 80 mps global WABA throughput + 1 message / 6s per recipient pair (Error 131056 guard).
  - **Deterministic Error Taxonomy**: Actionable recovery for Graph API errors 130429, 131056, 131047, 131026, 131031.
  - **Quantitative Benchmarking SLAs**: Macro-F1 $\ge 0.92$, ECE $\le 0.05$, Webhook Fast-ACK $< 20\text{ ms}$, Drift p95 $< 1,000\text{ ms}$, 0.00% double-sends.
  - **Testing Stack & Tooling Justification**: Vitest + Testcontainers (PG16 + Redis 7), Injectable `ClockProvider`, WireMock Graph API stubs, and Grafana k6 load tests.
  - **ISO Compliance Pillars**: ISO 27001, ISO 27701 (GDPR/DPDP Crypto-Shredding), ISO 25010, and ISO 42001.

### 3.0B Document 2: REA MS Teams Findings & Architectural Blueprint
- **Reference**: `REA-M365-TEAMS-SCHED-002`
- **Primary Files**:
  - Local Markdown: [`ms_teams_reverse_engineering_findings.md`](ms_teams_reverse_engineering_findings.md)
  - Google Doc: [Native Google Doc](https://docs.google.com/document/d/1ZbLMEipVlXDosNS30WQRYa5VmSXIB1C6XqvvKoRC-vA/edit?usp=drivesdk)
  - Google Drive Markdown: [Drive File Attachment](https://drive.google.com/file/d/1a67LSozozafosVld8Yx9Dk5fTz2P-ysG/view?usp=drivesdk)
- **Target Audience**: Principal Backend Architects, Infrastructure Engineers, Security & Compliance Officers
- **Core Topics**:
  - **7-Layer Architectural Blueprint**:
    - *Layer 1 (Client UX)*: Fluent UI Popover, LevelDB `skypeMessageLocal` optimistic caching, scheduled draft banner docked above compose box, edit/cancel/send-now workflows.
    - *Layer 2 (Network Protocols)*: Azure Front Door Anycast routing, Next-Gen regional gateways (`*.ng.msg.teams.microsoft.com`), virtual thread container `48:drafts`, JSON payload schemas, headers.
    - *Layer 3 (Real-Time Signaling)*: Trouter full-duplex WebSocket push, binary ping/pong keepalives, HTTP long-polling fallback, client sequence ACK.
    - *Layer 4 (Cosmos DB Storage)*: `DraftMessages` container partitioned by `userId`, document schema, 8-day TTL auto-purge, draft lifecycle state machine.
    - *Layer 5 (Distributed Broker Scheduling)*: Elimination of database polling anti-pattern; Azure Service Bus `ScheduledEnqueueTimeUtc` dormant partition staging; PeekLock consumer workers; 64-bit `SequenceNumber` $O(1)$ cancellation; atomic CAS via Cosmos DB `_etag` headers with HTTP 412 handling.
    - *Layer 6 (Enterprise Governance & Compliance)*: Continuous Access Evaluation (CAE) at trigger time via OpenID CAEP/SSE push streams to a sub-0.5ms in-memory revocation cache; conversation roster check; dynamic Purview DLP pre-flight scans; compliance boundary separation shielding `48:drafts` from eDiscovery/Legal Hold while post-delivery messages are mirrored to Exchange Online's hidden `TeamChat` mailbox folder.
    - *Layer 7 (Failure Modes & Recovery)*: 12-edge-condition resolution matrix (offline sender, time zone travel, lazy thread provisioning, 7-day boundary limits, concurrent edits near send window, channel deletion, worker host crash, B2B federation, physical clock drift).
  - **Strategic Takeaways**: 5 fundamental architectural principles for omnichannel messaging systems.

### 3.0C Document 3: Refined High-Level Design (HLD) & Target Architecture Stack
- **Reference**: `HLD-SCHED-REFINED-003`
- **Primary Files**:
  - Local Markdown: [`refined_hld_and_target_stack.md`](refined_hld_and_target_stack.md)
  - Google Doc: [Native Google Doc](https://docs.google.com/document/d/14OxFhry9f7kfBpAs9OljzgKH2WovWqpwbckFfhigtLU/edit?usp=drivesdk)
  - Google Drive Markdown: [Drive File Attachment](https://drive.google.com/file/d/1n7l6m1EafcueASZXv0jQqCa0JjcvCdV7/view?usp=drivesdk)
- **Target Audience**: Core Implementation Team, Backend Engineers, DevOps & SRE
- **Core Topics**:
  - **Part I: Master Architectural Delta-Mapping Matrix**: 10-dimension comparative matrix tracing baseline HLD v2.0 vs. MS Teams REA vs. Preeti's rectifications vs. Target Refined HLD v3.0.
  - **Part II: Quad-Tier Message Delivery Topology**: Model A (Assistive `wa.me` CTA Redirect with Escalating Nudge & T+3 min Bot Relay Fallback), Model B (Official Business App Coexistence), Model C (Official Bot Relay), Hybrid Edge-Triggered Companion (iOS Shortcuts / Android Intents), and Bring-Your-Own-Node (BYON) Desktop Bridge (`@scheduler/byon-bridge`).
  - **Part III: The 4-Step Trigger-Time Pre-Flight Compliance Gate**: Adapted directly from MS Teams CAE & Purview DLP: (1) Opt-out / Blacklist check (<0.5ms), (2) 24h Customer Service Window check, (3) Dual token-bucket rate limiter, (4) System token validity check.
  - **Part IV: Optimistic CAS Concurrency & Two-Phase Resilient Queuing**: Cosmos DB ETag pattern translated to PostgreSQL `version INT` column; Phase 1 pure `pg-boss` ACID queuing eliminating dual-write hazards; Phase 2 Two-Tier Partitioned Feeder (PostgreSQL Ledger + BullMQ/Redis Thin Pointers + Redlock + Sweeper Dead-Man's Switch).
  - **Part V: Canonical Production PostgreSQL 16 DDL**: Production schemas for `tenants`, `channel_accounts`, `recipient_consents`, `scheduled_jobs`, `opt_outs`, `audit_log`, composite indexes.
  - **Part VI: Conversational NLU, Deterministic Fast-Paths & Recurrence Precision**: Sub-50ms regex router bypass; Calibrated NLU (ECE $\le 0.05$); Luxon wall-clock invariant recurrence math preserving month-end anchor days (Jan 31 $\to$ Feb 28 $\to$ Mar 31).
  - **Part VII: Target Technology Stack & Operational Cost Blueprint**: Node.js 22 LTS, Fastify 5.x, Prisma 6.x, PostgreSQL 16, Redis 7, Cloudflare Zero Trust, AWS KMS; $8.90–$12.50/month OpEx on Hetzner CPX21 supporting 50,000+ active users.
  - **Part VIII: Phased Implementation Roadmap**: 4-phase 14-day transition roadmap with concrete verification runbooks and invalidation conditions.

### 3.0 Microsoft Teams Reverse Engineering & WhatsApp Scheduler Master Architecture
- **Primary File**: [`microsoft_teams_and_whatsapp_scheduler_architecture.md`](microsoft_teams_and_whatsapp_scheduler_architecture.md)
- **Format**: Markdown (`.md`)
- **Target Audience**: Principal Backend Architects, Systems Engineers, Security Officers, and Enterprise Developers
- **Core Topics**:
  - **Microsoft Teams Decompilation**: Technology stack matrix, `chatsvc` internal protocol, `48:drafts` virtual container, `sendAt` UTC epochs, Trouter WebSocket signaling, and LevelDB local storage forensics.
  - **Cosmos DB & Service Bus Scheduling**: Azure Cosmos DB operational persistence, Azure Service Bus `ScheduledEnqueueTimeUtc` zero-polling hierarchical partition indexes, PeekLock consumer workers, atomic CAS via ETags, and clock drift resilience.
  - **Enterprise Governance & Compliance**: Continuous Access Evaluation (CAE) at trigger time, dynamic Purview DLP content evaluation, and M365 Substrate / Exchange Online hidden `TeamChat` mailbox eDiscovery and Legal Hold.
  - **10-Dimension Architectural Translation**: Comparative analysis between closed enterprise and open restricted channels.
  - **WhatsApp Enterprise Safeguards**: Meta 24-hour Customer Care Window Tri-Tier Fallback Engine (Session -> Utility Template -> Model A Assistive `wa.me` CTA Link), 80 mps Token Bucket limiter, Baileys companion anti-ban 4-tier warm-up matrix, human typing presence simulation, positive jitter (+5s to +45s), Fastify HMAC webhook hardening, and instant STOP opt-out suppression.
  - **Conversational UX & DST Recurrence**: 5-step guided wizard FSM, slash command grammar, `@chrono-node` NLP entity parsing, interactive Quick-Reply and List Pickers, and Luxon wall-clock invariant recurrence math (0.0 min drift across DST changes).
  - **Production HLD & SQL DDL**: End-to-end component topology, Two-Tier Scheduler (PostgreSQL 16 master ledger + in-memory delayed queue + Dead-Man's-Switch Sweeper), complete PostgreSQL 16 DDL with AES-256-GCM envelope encryption and HMAC-SHA256 blind indexing, job lifecycle state machine, and OpEx bill-of-materials ($11.95–$27.80/month).

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
  - **PostgreSQL-Native ACID Queuing**: Single atomic transaction (`BEGIN; INSERT schedule; SELECT pgboss.send(...); COMMIT;`) replacing BullMQ distributed dual-write hazard.
  - **Zero-Trust Network Segmentation**: Cloudflare Tunnels (0 open inbound ports), Tailscale WireGuard Mesh VPN (port 22 closed to internet), and Fastify raw-body HMAC-SHA256 verification.
  - **PII Data Protection & Crypto-Shredding**: AWS KMS 2-tier envelope encryption, HMAC-SHA256 blind indexing (`recipient_bindex`), Pino compiled log scrubbing, and 7-day payload TTL purge.
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
