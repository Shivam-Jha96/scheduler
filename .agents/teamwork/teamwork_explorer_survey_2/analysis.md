# Omnichannel & WhatsApp Message Scheduler: Requirements Analysis & Kanban Backlog Epics

**Document Identifier:** REQ-ANALYSIS-KANBAN-V1.0  
**Status:** Complete & Approved for Backlog Creation  
**Scope:** Exhaustive BRD/FRD Extraction and Kanban Epic Synthesis for GitHub Projects  

---

## 1. Executive Summary

This document provides a comprehensive extraction and synthesis of all business requirements, functional specifications, non-functional criteria, and architectural patterns found across the system documentation in `d:\Dev\repos\scheduler\docs` and the monorepo boilerplate plan.

The resulting 18 Epics are specifically categorized, prioritized, and detailed so that an engineering team or automated GitHub CLI agent can directly convert them into **GitHub Issues** and **GitHub Project Draft Items** on a Kanban Board Backlog.

---

## 2. Master Requirements Inventory (Extracted Catalog)

### 2.1 SMART Business Objectives (BRD)
- **BO-01 (In-App Scheduling)**: Enable 100% of scheduling operations natively via chat conversation without external mobile apps or web redirects.
- **BO-02 (Zero Double-Sends)**: Zero tolerance ($0.0\%$) for duplicate message deliveries across socket retries, worker restarts, or server crashes.
- **BO-03 (Account Safety & Anti-Ban)**: Maintain a personal WhatsApp account restriction and SIM-ban rate $< 0.01\%$ via human-like pacing.
- **BO-04 (Dispatch Accuracy)**: Deliver scheduled messages with $< 1.0\text{ second}$ timestamp variance/drift from target execution time.
- **BO-05 (Sustainable Unit Economics)**: Total operational hosting cost $< \$30.00 / \text{month}$ per 10,000 active scheduled messages ($< \$0.012$ per active user).
- **BO-06 (Temporal Precision & DST Invariance)**: Exactly $0.0\text{ minutes}$ drift across seasonal Daylight Saving Time clock shifts.

### 2.2 Core Business Rules (BR)
- **BR-01 (Meta Policy & 24h Window Compliance)**: For official Cloud API dispatches, conversations beyond the 24-hour customer window must automatically fall back to pre-approved Meta Utility Templates (`scheduled_reminder_cta_v1`).
- **BR-02 (Anti-Spam & Health Protection)**: Prohibits unconsented mass blasts; mandates realistic typing delays (35–55 ms/character) and serialization jitter (3–6s between sends).
- **BR-03 (Data Privacy & Encryption at Rest)**: Cryptographic Signal pre-keys, auth tokens, and session credentials must be envelope-encrypted with AES-256-GCM using AWS KMS 256-bit keys. Message bodies are scrubbed post-delivery.
- **BR-04 (Sender Authenticity)**: Peer-to-peer dispatches must originate from Alice's registered account session so Bob receives messages within their existing 1-on-1 chat history.
- **BR-05 (Wall-Clock Invariance)**: All reminders are anchored strictly to the user's localized IANA timezone rather than fixed UTC offsets.

### 2.3 Functional Requirements (FRD)
- **FR-AUTH-01 (User Auto-Provisioning)**: Auto-register user on first inbound message with default UTC timezone, locale `en-US`, and `status = 'ACTIVE'`.
- **FR-AUTH-02 (Single-Phone Pairing Code)**: Native 8-character pairing code flow (`/link` -> `sock.requestPairingCode`) for one-tap mobile pairing without scanning QR codes on a second screen.
- **FR-AUTH-03 (AES-256-GCM Signal Key Vault)**: Application-layer envelope encryption of session credentials and Signal pre-keys before PostgreSQL persistence.
- **FR-AUTH-04 (Session Lifecycle & Circuit Breaker)**: Handles socket errors (Code 401 unlinking, Code 403 account ban freeze, Code 515 restart backoff).
- **FR-WIZ-01 (Guided FSM Initiation)**: `/schedule` enters an in-memory draft state with a 15-minute inactivity TTL.
- **FR-WIZ-02 (Recipient Resolution & vCard)**: Accepts vCard 3.0 contact cards, E.164 phone numbers, saved contact aliases, and verifies `@g.us` group permissions.
- **FR-WIZ-03 (Multi-Modal Payload Capture)**: Captures text (up to 4,096 chars), images, audio/voice notes, documents (PDF), and videos with S3 pre-warming.
- **FR-WIZ-04 (Natural Language Temporal NLP)**: Uses `chrono-node` to convert expressions (e.g. *"tomorrow at 9:30am"*) relative to user timezone; enforces minimum $+60\text{s}$ future threshold.
- **FR-WIZ-05 (Confirmation Preview & Interactive Buttons)**: Renders a preview card with `[✅ Confirm]` (ACID commit), `[✏️ Edit]`, and `[❌ Cancel]`.
- **FR-CLI-01 (Fast-Path One-Line Schedule)**: `/schedule <target> <time> | <message>` for instant atomic scheduling.
- **FR-CLI-02 (Recurring CLI Schedule)**: `/schedule --repeat <rule> <target> <time> | <msg>` for recurring jobs.
- **FR-CLI-03 (Interactive Queue Inspection)**: `/list [status] [page]` returning paginated jobs with status indicators (`🟡 PENDING`, `🟢 SENT`, `🔴 FAILED`).
- **FR-CLI-04 (Cancellation & BullMQ Eviction)**: `/cancel <job_uid>` updates DB to `CANCELLED` and evicts in-flight Redis jobs via `bullQueue.remove(jobId)`.
- **FR-CLI-05 (In-Place Edit)**: `/edit <job_uid> <field> <new_val>` updates target parameters and reschedules in-flight jobs.
- **FR-CLI-06 (Timezone Configuration)**: `/timezone <IANA_zone>` updates user's default timezone anchor.
- **FR-SCHED-01 (Two-Tier Look-Ahead Feeder)**: 60-second poller queries PostgreSQL using `FOR UPDATE SKIP LOCKED` for jobs due in next 5 minutes and buffers them to BullMQ.
- **FR-SCHED-02 (Idempotency & Zero Double-Send)**: Acquires distributed Redis lock `lock:msg:{id} NX EX 600` and enforces unique DB constraints.
- **FR-REC-01 (Single-Active-Row Recurrence)**: Exactly one active DB row per recurring schedule; advances timestamp in-place upon execution.
- **FR-REC-02 (Wall-Clock DST Disambiguation)**: Luxon-based calendar arithmetic adjusting UTC offsets during Spring-Forward gaps and Fall-Back folds.
- **FR-REC-03 (Anchor Day & Reboot Fast-Forward)**: Preserves month-end anchor day (e.g. day 31) through February and fast-forwards overdue jobs past `NOW()` upon server reboot.
- **FR-REL-01 (Exponential Backoff & Jitter)**: Retries transient socket errors up to 5 times (2s, 4s, 8s, 16s, 32s) plus random 500ms jitter.
- **FR-REL-02 (Dead Letter Queue & Alerting)**: Moves exhausted jobs to DLQ (`FAILED_PERMANENTLY`) and sends out-of-band notification to the sender.
- **FR-REL-03 (Dead-Man's Recovery Sweeper)**: Runs every 2–5 minutes recovering stale `PROCESSING` jobs older than 5 minutes without racing the feeder.
- **FR-META-01 (Human Typing Emulation)**: Emulates human typing cadence (`composing` state for 35–55 ms/character, clamped 1.5s–4.0s).
- **FR-META-02 (Inter-Message Serialization & Jitter)**: Spaces consecutive outbound messages from the same sender by 3–6s (existing contacts) or 8–15s (new contacts).
- **FR-META-03 (1-Click CTA wa.me Redirector)**: Provides `https://sched.app/r/{job_uid}` which 302-redirects to `whatsapp://send?phone={phone}&text={msg}` for policy-compliant assistive sending.
- **FR-META-04 (24h Service Window Watchdog)**: Automatically falls back to Meta Utility Template if `NOW() - last_inbound >= 24h`.

### 2.4 Omnichannel & Monorepo Scale-Out Requirements
- **OMNI-01 (Transport-Agnostic Core)**: Decouple scheduler engine from any specific chat provider via `IMessagingTransportAdapter` and dynamic `@scheduler/adapter-registry`.
- **OMNI-02 (Multi-Platform Sessions)**: Support polymorphic `user_platform_sessions` / `channel_accounts` across WhatsApp, Viber, Discord, Signal, LINE, iMessage, Slack, Telegram, and Webhooks.
- **OMNI-03 (Viber Integration)**: Official Viber REST Bot API adapter with 1-to-1 reminders and interactive carousels.
- **OMNI-04 (Discord Integration)**: Official Discord Bot API (`discord.js`, Gateway v10) with native slash commands, threads, and channel announcements.
- **OMNI-05 (Signal Integration)**: Headless containerized `signal-cli` RPC daemon acting as secondary linked device for cloud-queued E2EE scheduling.
- **OMNI-06 (Developer Extensibility SDK)**: `@scheduler/adapter-sdk`, `@scheduler/adapter-test-kit`, and `npm run create:adapter` scaffolding tool.
- **OMNI-07 (Web Management Portal)**: Next.js responsive control plane for multi-account QR pairing, calendar queue inspection, and cross-platform scheduling.
- **OMNI-08 (Monetization & Tier Limits)**: Free Tier (15 msgs/mo), Pro Tier ($7.99–$9.99/mo), Business Tier ($29.99–$49.99/mo) with bulk CSV / Google Sheets sync.

---

## 3. Definitive Kanban Backlog Epics (EPIC-01 to EPIC-18)

Below is the complete set of 18 synthesized Epics ready for direct conversion to GitHub Issues / Project Draft Items.

```
+──────────────────────────────────────────────────────────────────────────────────────────────────────────+
|                                  KANBAN BACKLOG EPICS OVERVIEW                                           |
+─────────┬─────────────────────────────────────────────────────────────────────────┬──────────┬───────────+
| Epic ID | Title                                                                   | Domain   | Priority  |
+─────────┼─────────────────────────────────────────────────────────────────────────┼──────────┼───────────+
| EPIC-01 | Enterprise Monorepo Boilerplate & Pluggable Adapter SDK                 | DX/Infra | P0        |
| EPIC-02 | Core Relational Data Model, Polymorphic Ledger & Migrations             | Database | P0        |
| EPIC-03 | Two-Tier Hybrid Scheduling Engine & Look-Ahead Feeder                   | Engine   | P0        |
| EPIC-04 | Wall-Clock Recurrence Engine & DST Invariance Mathematics               | Temporal | P0        |
| EPIC-05 | Zero-Double-Send Guarantee, Distributed Mutex & Crash Recovery          | Reliab.  | P0        |
| EPIC-06 | Cryptographic Security Vault & PII Privacy Enforcement                  | Security | P0        |
| EPIC-07 | WhatsApp In-Chat Conversational 5-Step Guided Wizard                    | UX/FSM   | P0        |
| EPIC-08 | Fast-Path Slash Command Grammar & Execution Engine                      | CLI/UX   | P0        |
| EPIC-09 | WhatsApp Companion Device Integration (Baileys Engine)                  | WhatsApp | P0        |
| EPIC-10 | Anti-Ban Heuristics & Human Behavioral Emulation Engine                  | Safety   | P0        |
| EPIC-11 | Meta Cloud API Assistive Model & Utility Template Fallback               | Meta WABA| P1        |
| EPIC-12 | Omnichannel High-Volume Channels: Discord & Viber Adapters               | Omni     | P1        |
| EPIC-13 | Privacy Ecosystem Expansion: Headless Signal Integration                | Omni/E2EE| P1        |
| EPIC-14 | Regional & Prosumer Bridges: LINE & iMessage Integrations                | Omni     | P2        |
| EPIC-15 | Universal Web Management Dashboard & Cross-Platform Control Plane       | Web UI   | P1        |
| EPIC-16 | SaaS Monetization, Tier Quotas & Subscription Billing                   | Business | P1        |
| EPIC-17 | Production Observability, Distributed Health Sweeper & Alerting         | SRE/Ops  | P1        |
| EPIC-18 | Multi-Modal Media Storage Pipeline & Pre-Warming Cache                  | Storage   | P1        |
+─────────┴─────────────────────────────────────────────────────────────────────────┴──────────┴───────────+
```

---

### EPIC-01: Enterprise Monorepo Boilerplate & Pluggable Adapter SDK
- **Epic ID**: `EPIC-01`
- **Category / Domain**: Platform Infrastructure & Developer Experience
- **Priority**: `P0`
- **Detailed Description & Business Value**:  
  Establish an enterprise-grade, modular TypeScript monorepo using Turborepo and pnpm/npm workspaces. The architecture isolates the core scheduling engine from chat transports through a standardized `IChannelAdapter` contract (`@scheduler/adapter-sdk`) and an Inversion-of-Control registry (`@scheduler/adapter-registry`). This allows dozens of distributed engineers to author, test, and deploy new channel adapters (WhatsApp, Telegram, Discord, Slack, etc.) without touching core database or scheduling pipelines.
- **Key Functional Specifications / Stories Included**:
  - Root monorepo workspace configuration (`apps/`, `packages/`, `adapters/`, `tools/`).
  - `@scheduler/adapter-sdk` defining `IChannelAdapter`, `ChannelCapabilities`, `OutboundPayload`, and `DeliveryResult`.
  - Dynamic `AdapterRegistry` with IoC container for runtime adapter injection.
  - Automated contract test suite `@scheduler/adapter-test-kit`.
  - CLI scaffolding generator `npm run create:adapter -- --name <channel>`.
  - Shared packages: `types`, `logger` (Pino), `crypto`, `config` (Zod), `temporal`.
- **Acceptance Criteria**:
  - [ ] Turborepo task pipeline builds, tests, and lints all workspaces with caching enabled.
  - [ ] Running `npm run create:adapter -- --name test-channel` generates a fully compliant boilerplate adapter package with passing contract tests.
  - [ ] Core scheduling modules have zero direct imports from any specific adapter package.
  - [ ] Docker Compose environment orchestrates local PostgreSQL 16 and Redis 7 dependencies.

---

### EPIC-02: Core Relational Data Model, Polymorphic Ledger & Migrations
- **Epic ID**: `EPIC-02`
- **Category / Domain**: Core Data Architecture
- **Priority**: `P0`
- **Detailed Description & Business Value**:  
  Design and implement the production relational persistence layer on PostgreSQL 16. The schema provides a durable, horizontal multi-platform ledger for all scheduled messages, multi-account platform sessions, contact address books, and append-only execution audit logs. Partial B-tree indexing keeps polling scans $< 0.2\text{ ms}$ under heavy production loads.
- **Key Functional Specifications / Stories Included**:
  - Database schema definition with Prisma ORM / PostgreSQL DDL.
  - Tables: `users`, `user_platform_sessions` / `channel_accounts`, `contacts`, `scheduled_messages` / `scheduled_jobs`, `job_execution_logs` / `dispatch_audit_log`.
  - Polymorphic platform discrimination via `platform_type` enum or normalized channel identifiers.
  - Partial B-tree index on `(next_run_at_utc ASC) WHERE status IN ('PENDING', 'QUEUED')`.
  - Automated migration scripts and database seed harnesses.
- **Acceptance Criteria**:
  - [ ] Schema applies cleanly with zero errors on PostgreSQL 16.
  - [ ] Polling query `EXPLAIN ANALYZE` confirms Index Scan on partial index with execution time $< 0.5\text{ ms}$ on 100,000 synthetic rows.
  - [ ] Cascading foreign key deletes properly purge child contacts and execution logs when a user account is deleted.
  - [ ] Enforces unique constraint on `(user_id, platform, platform_user_id)` and `(idempotency_key)`.

---

### EPIC-03: Two-Tier Hybrid Scheduling Engine & Look-Ahead Feeder
- **Epic ID**: `EPIC-03`
- **Category / Domain**: Core Scheduler Engine
- **Priority**: `P0`
- **Detailed Description & Business Value**:  
  Implement the high-performance Two-Tier Hybrid Scheduler that combines PostgreSQL 16 durable long-term storage with BullMQ/Redis in-memory delay queues. This eliminates database connection starvation and high-frequency polling while preventing millions of future jobs from bloating Redis RAM. Delivers messages with sub-second temporal accuracy ($< 1.0\text{ second}$ drift, BO-04).
- **Key Functional Specifications / Stories Included**:
  - **Tier 1 (Postgres Master)**: Stores all future jobs durably on disk.
  - **Look-Ahead Feeder Daemon**: 60-second cron polling PostgreSQL with `FOR UPDATE SKIP LOCKED` for jobs maturing within $T + 5\text{ minutes}$.
  - **Tier 2 (BullMQ Buffer)**: Stages due jobs into BullMQ Redis delayed queue with millisecond countdown timers.
  - **Distributed Delivery Worker Pool**: Consumes BullMQ triggers at execution timestamp and invokes the target channel adapter.
- **Acceptance Criteria**:
  - [ ] Jobs scheduled 30 days in advance execute within $\pm 1000\text{ ms}$ of target timestamp.
  - [ ] Redis memory consumption for 10,000 pending jobs remains below $250\text{ KB}$ (only staging the 5-minute sliding window).
  - [ ] Multiple horizontal feeder instances querying simultaneously via `SKIP LOCKED` never claim the same job twice.
  - [ ] Poller query execution time remains $< 0.2\text{ ms}$ per scan.

---

### EPIC-04: Wall-Clock Recurrence Engine & DST Invariance Mathematics
- **Epic ID**: `EPIC-04`
- **Category / Domain**: Temporal & Recurrence Engine
- **Priority**: `P0`
- **Detailed Description & Business Value**:  
  Build a mathematically rigorous temporal recurrence engine using Luxon that guarantees local wall-clock invariance across seasonal Daylight Saving Time (DST) shifts (BO-06, BR-05). Daily reminders scheduled for 9:00 AM local time will always trigger at 9:00 AM regardless of 23-hour "spring forward" or 25-hour "fall back" transitions.
- **Key Functional Specifications / Stories Included**:
  - Formula: UTC $\rightarrow$ User Local IANA Time $\rightarrow$ Calendar Add $\rightarrow$ UTC.
  - Single-Active-Row recurrence state machine (updating the existing row in-place upon execution).
  - Month-End Anchor Day preservation (e.g., day 31 preserved: Jan 31 $\rightarrow$ Feb 28/29 $\rightarrow$ Mar 31 $\rightarrow$ Apr 30).
  - DST Spring-Forward gap (advances to valid time) and Fall-Back fold (executes earlier standard occurrence) handling.
  - Reboot fast-forwarding / misfire handling: `SKIP` overdue recurrences after extended server downtime to prevent spam bursts.
- **Acceptance Criteria**:
  - [ ] Comprehensive unit test suite (39+ timezone assertions) passes with $100\%$ success across New York, London, Sydney, and UTC.
  - [ ] A job set for the 31st of every month correctly runs on Feb 28 (or 29) and restores to Mar 31 and Apr 30 without day drift.
  - [ ] Server downtime of 4 hours fast-forwards overdue recurring jobs past `NOW()` and marks skipped executions as `MISFIRED`.

---

### EPIC-05: Zero-Double-Send Guarantee, Distributed Mutex & Crash Recovery
- **Epic ID**: `EPIC-05`
- **Category / Domain**: Reliability & Fault Tolerance
- **Priority**: `P0`
- **Detailed Description & Business Value**:  
  Enforce a multi-layered zero-double-send guarantee ($0.0\%$ tolerance, BO-02, BR-02) to prevent relationship-damaging duplicate message dispatches. Enforces distributed Redis mutexes, deterministic stanza IDs, atomic database status updates, and a background recovery sweeper for sudden node crashes.
- **Key Functional Specifications / Stories Included**:
  - Deterministic 22-character WhatsApp stanza ID generation: `"3EB0" + SHA256(job_uid + ":" + run_time).slice(0,18)`.
  - Deterministic SHA-256 idempotency key stored with unique constraint in PostgreSQL.
  - Distributed Redis mutex (`SET lock:job:{id} NX EX 600`) acquired prior to transport dispatch.
  - Atomic database state progression (`QUEUED` $\rightarrow$ `PROCESSING` $\rightarrow$ `SENT`).
  - Active BullMQ queue eviction: `bullQueue.remove(jobId)` when a user cancels an in-flight message.
  - Dead-Man's-Switch Sweeper: Cron running every 2 minutes resetting orphaned `PROCESSING` jobs older than 5 minutes.
- **Acceptance Criteria**:
  - [ ] Chaos testing with worker `SIGKILL` mid-socket dispatch results in exactly 0 duplicate sends.
  - [ ] Re-sending the same stanza ID to WhatsApp socket results in an automatic server-level deduplication drop.
  - [ ] Cancelling a message 60 seconds before execution removes it from Redis memory and prevents transmission.
  - [ ] Feeder and Sweeper query windows never overlap or race for the same job record.

---

### EPIC-06: Cryptographic Security Vault & PII Privacy Enforcement
- **Epic ID**: `EPIC-06`
- **Category / Domain**: Security & Compliance
- **Priority**: `P0`
- **Detailed Description & Business Value**:  
  Implement enterprise-grade encryption and privacy controls to safeguard sensitive user session keys and message contents (BR-03). Protects users against data breaches, enforces zero-knowledge storage principles, and satisfies global data privacy regulations (GDPR).
- **Key Functional Specifications / Stories Included**:
  - Application-layer AES-256-GCM envelope encryption for Baileys Signal pre-keys, OAuth tokens, and session credentials.
  - AWS KMS or local KMS master key integration with random 12-byte initialization vectors (IV) and authentication tags.
  - Zero plain-text credentials stored anywhere in the database or cache.
  - Ephemeral message retention policy: Message payloads permanently scrubbed post-delivery, retaining only anonymized delivery receipts and hashes.
  - Zero contact address book scraping: Only specific scheduled recipient numbers are recorded.
  - User account deletion cascade: Purges all associated keys, sessions, and contacts upon request.
- **Acceptance Criteria**:
  - [ ] Automated security scan verifies no raw private keys or plaintext session credentials exist in PostgreSQL tables.
  - [ ] Corrupted authentication tags or tampered ciphertext immediately fail decryption with an explicit cryptographic error.
  - [ ] Successfully dispatched messages have their `content_enc` column set to `NULL` or purged within 60 seconds of ACK.

---

### EPIC-07: WhatsApp In-Chat Conversational 5-Step Guided Wizard
- **Epic ID**: `EPIC-07`
- **Category / Domain**: Conversational UX & State Machine
- **Priority**: `P0`
- **Detailed Description & Business Value**:  
  Deliver a seamless, conversational 5-step wizard directly inside WhatsApp (BO-01, FR-WIZ-01 to FR-WIZ-05). Everyday users can schedule reminders for friends, family, or business groups without installing third-party apps, navigating external web pages, or learning complex syntax.
- **Key Functional Specifications / Stories Included**:
  - Redis-backed finite state machine (FSM) session with 15-minute inactivity TTL.
  - **Step 1 (Recipient)**: Ingests vCard 3.0 contact cards, E.164 phone numbers, or saved aliases; pre-flight check for `@g.us` group chat permissions.
  - **Step 2 (Payload)**: Captures text (up to 4,096 chars) or streams media attachments (images, voice notes, PDFs, videos) to S3.
  - **Step 3 (Timing)**: Natural language temporal parsing via `chrono-node` in user timezone; rejects times $\le \text{Now} + 60\text{s}$.
  - **Step 4 (Recurrence)**: Interactive buttons for Once, Daily, Weekdays, Weekly, Monthly.
  - **Step 5 (Confirmation)**: Renders a structured preview card with `[✅ Confirm]`, `[✏️ Edit]`, and `[❌ Cancel]` buttons.
- **Acceptance Criteria**:
  - [ ] User can complete end-to-end scheduling flow in under 30 seconds by sharing a contact card and voice/text note.
  - [ ] Tapping `[✏️ Edit]` allows navigating backward to any step without re-entering unchanged fields.
  - [ ] Inactive sessions cleanly expire after 15 minutes with Redis memory reclaimed.
  - [ ] Confirmation triggers an ACID database transaction and returns a human-readable summary card with Job UID.

---

### EPIC-08: Fast-Path Slash Command Grammar & Execution Engine
- **Epic ID**: `EPIC-08`
- **Category / Domain**: Conversational CLI & Power User Interface
- **Priority**: `P0`
- **Detailed Description & Business Value**:  
  Provide a high-speed, single-line command grammar for power users, business operators, and automated systems (FR-CLI-01 to FR-CLI-06). Enables instant scheduling, queue inspection, in-flight cancellation, in-place editing, and timezone configuration in one atomic message turn.
- **Key Functional Specifications / Stories Included**:
  - `/schedule <target> <time> | <message>` for one-off dispatches.
  - `/schedule --repeat <rule> <target> <time> | <message>` for recurring schedules.
  - `/list [pending|sent|all] [page]` returning formatted job summaries with status badges (`🟡 PENDING`, `🟢 SENT`, `🔴 FAILED`).
  - `/cancel <job_uid>` marking status `CANCELLED` and removing in-flight jobs from BullMQ.
  - `/edit <job_uid> <field> <new_val>` to adjust timing or message content.
  - `/timezone <IANA_zone>` updating user's anchor timezone.
- **Acceptance Criteria**:
  - [ ] Fast-path commands schedule jobs in a single turn without triggering the 5-step wizard.
  - [ ] `/list` cleanly paginates and displays times localized to user's configured timezone.
  - [ ] Executing `/cancel` on a job scheduled 2 minutes out immediately aborts delivery and notifies the user.
  - [ ] Syntax errors return helpful usage examples and parameter hints.

---

### EPIC-09: WhatsApp Companion Device Integration (Baileys Engine)
- **Epic ID**: `EPIC-09`
- **Category / Domain**: WhatsApp Channel Integration (P2P Model)
- **Priority**: `P0`
- **Detailed Description & Business Value**:  
  Implement the personal peer-to-peer delivery engine using `@whiskeysockets/baileys`. Connects as an authorized secondary companion device using WhatsApp's multi-device protocol over Noise_XX WebSockets. Messages originate from Alice's real personal phone number directly into Bob's existing chat thread without requiring corporate WABA accounts.
- **Key Functional Specifications / Stories Included**:
  - Baileys socket integration with persistent state store.
  - Single-Phone 8-character pairing code flow (`/link` -> `sock.requestPairingCode`) for seamless one-phone mobile pairing.
  - QR-code pairing fallback for desktop/web dashboard users.
  - Socket lifecycle handling: automatic reconnect with exponential backoff on code 515 (restart required).
  - Circuit breakers: immediate session freeze and user alert on code 401 (unlinked) or 403 (banned).
- **Acceptance Criteria**:
  - [ ] User can link mobile phone via 8-digit pairing code notification without a secondary screen.
  - [ ] Companion device session remains active for months as long as primary device accesses WhatsApp every 14 days.
  - [ ] Outbound messages arrive on recipient phones displaying Alice's personal phone number and avatar.
  - [ ] Socket disconnections recover automatically within 10 seconds of network restoration.

---

### EPIC-10: Anti-Ban Heuristics & Human Behavioral Emulation Engine
- **Epic ID**: `EPIC-10`
- **Category / Domain**: Account Safety & Anti-Abuse
- **Priority**: `P0`
- **Detailed Description & Business Value**:  
  Protect Alice's personal WhatsApp account from algorithmic spam flags and permanent SIM bans (BO-03, BR-02, BR-04). By mimicking authentic human typing cadences, spacing out message bursts, and serializing outbound socket traffic per sender, the system maintains $< 0.01\%$ ban frequency.
- **Key Functional Specifications / Stories Included**:
  - Presence emulation: Transition through `available` $\rightarrow$ `composing` $\rightarrow$ `paused` $\rightarrow$ `send`.
  - Realistic typing duration: $T_{\text{type}} = \min(4.0, \text{chars} \times 0.05 + \mathcal{N}(1.5, 0.4))\text{ seconds}$.
  - Per-sender serialization locks: Strictly one active outbound socket transmission per account.
  - Inter-message jitter spacing: 3–6s delay for known contacts; 8–15s for first-time recipients.
  - Token-bucket rate limiting: Hard cap at 5 messages/minute and 50 messages/hour per personal account.
- **Acceptance Criteria**:
  - [ ] Rapid scheduling of 100 messages to a contact group is smoothly serialized over 8–10 minutes rather than blasted concurrently.
  - [ ] Outbound telemetry verifies `composing` presence stanza precedes every text stanza.
  - [ ] Exceeding 5 messages/minute throttles the queue and emits pacing telemetry warnings.
  - [ ] Zero account bans observed in a 500-message burst pacing verification test run.

---

### EPIC-11: Meta Cloud API Assistive Model & Utility Template Fallback
- **Epic ID**: `EPIC-11`
- **Category / Domain**: WhatsApp Business Channel (B2C & Policy-Compliant)
- **Priority**: `P1`
- **Detailed Description & Business Value**:  
  Provide an official, zero-ban-risk operational model using Meta’s WhatsApp Business Cloud API. Solves the 24-hour customer service window constraint via an assistive 1-click CTA deep-link redirector, and provides automated fallback to pre-approved Utility Templates for automated notifications.
- **Key Functional Specifications / Stories Included**:
  - Inbound webhook receiver for official Meta Graph API v20+.
  - 1-Click CTA redirector service: `https://sched.app/r/{job_uid}` returning HTTP 302 to `whatsapp://send?phone={bob}&text={encoded_msg}`.
  - 24-Hour Customer Window Watchdog: Checks `NOW() - last_inbound >= 24h`.
  - Automated Utility Template routing: Dispatches pre-approved `scheduled_reminder_cta_v1` when 24h window has elapsed.
  - Webhook signature verification (`X-Hub-Signature-256`).
- **Acceptance Criteria**:
  - [ ] Inbound webhooks process and acknowledge Meta with `HTTP 200 OK` within $< 200\text{ ms}$.
  - [ ] Clicking the CTA button on Alice's phone opens native WhatsApp chat with Bob with pre-filled text in one tap.
  - [ ] Messages attempted outside the 24h window cleanly route through approved Meta Utility Templates without triggering `Error 131047`.

---

### EPIC-12: Omnichannel High-Volume Channels: Discord & Viber Adapters
- **Epic ID**: `EPIC-12`
- **Category / Domain**: Omnichannel Expansion
- **Priority**: `P1`
- **Detailed Description & Business Value**:  
  Scale the scheduling platform to high-volume messaging ecosystems that currently lack 1-to-1 personal scheduling whitespace: **Viber** (1.1B registered users, dominant in Eastern Europe/Balkans/Philippines) and **Discord** (200M gaming/remote tech MAUs). Both utilize official bot developer platforms with zero account ban risks.
- **Key Functional Specifications / Stories Included**:
  - **Discord Adapter**:
    - Built via `discord.js` (Gateway v10).
    - Native `/schedule` slash commands with interactive Discord time pickers.
    - Supports direct message scheduling, channel announcements, and thread reminders.
  - **Viber Adapter**:
    - Viber REST Bot API adapter and webhook receiver.
    - Conversational 1-to-1 reminder bot with rich interactive button carousels.
    - Zero message conversation fees via official Viber bot tokens.
  - Implements `IMessagingTransportAdapter` interface with contract tests.
- **Acceptance Criteria**:
  - [ ] Discord bot successfully schedules and dispatches channel messages and DMs across guild servers.
  - [ ] Viber bot handles inbound webhooks and delivers 1-to-1 reminders with rich keyboard actions.
  - [ ] Both adapters pass `@scheduler/adapter-test-kit` validation with 100% compliance.

---

### EPIC-13: Privacy Ecosystem Expansion: Headless Signal Integration
- **Epic ID**: `EPIC-13`
- **Category / Domain**: Omnichannel Expansion (Privacy Ecosystem)
- **Priority**: `P1`
- **Detailed Description & Business Value**:  
  Bring reliable, cloud-queued message scheduling to Signal's 50M privacy-focused users. Solves Signal's critical architectural flaw (where Android only schedules locally and fails if the device is offline/dead, while iOS/Desktop has zero scheduling capability) via a headless `signal-cli` secondary device bridge.
- **Key Functional Specifications / Stories Included**:
  - Containerized `signal-cli` microservice communicating via JSON-RPC over Unix sockets / TCP.
  - Secondary device linking flow: User links scheduler by scanning QR code in Signal (`Settings > Linked Devices`).
  - Headless cloud-queued dispatch executing with sub-second accuracy even when primary smartphone is offline.
  - Strict compliance with `libsignal` cryptographic protocols and E2EE standards.
- **Acceptance Criteria**:
  - [ ] User pairs Signal account via linked device QR code in web dashboard.
  - [ ] Scheduled message dispatches successfully at target second while sender's primary iPhone is powered off.
  - [ ] Recipient receives native E2EE message with full Signal security indicators.

---

### EPIC-14: Regional & Prosumer Bridges: LINE & iMessage Integrations
- **Epic ID**: `EPIC-14`
- **Category / Domain**: Omnichannel Expansion (Bridges)
- **Priority**: `P2`
- **Detailed Description & Business Value**:  
  Expand market reach into Japan/Taiwan/Thailand via **LINE** and North American prosumers via **iMessage**. Integrates official LINE Messaging APIs and a self-hosted macOS AppleScript / BlueBubbles bridge for blue-bubble scheduling.
- **Key Functional Specifications / Stories Included**:
  - **LINE Adapter**: Official LINE Messaging API bot handling flex messages and push alerts.
  - **iMessage Bridge**: Integration with self-hosted BlueBubbles server or macOS AppleScript daemon interacting with `chat.db`.
  - Recipient phone formatting and Apple ID email handle resolution.
- **Acceptance Criteria**:
  - [ ] LINE bot delivers scheduled flex message cards in LINE app.
  - [ ] iMessage bridge relays scheduled text to blue-bubble recipients via connected macOS host.

---

### EPIC-15: Universal Web Management Dashboard & Cross-Platform Control Plane
- **Epic ID**: `EPIC-15`
- **Category / Domain**: Web Experience & Control Plane
- **Priority**: `P1`
- **Detailed Description & Business Value**:  
  Deliver a centralized Next.js web application for managing accounts, viewing upcoming dispatches on an interactive calendar/Kanban, and executing cross-platform scheduling (e.g., Alice messages on WhatsApp to schedule a Discord prompt or Viber reminder).
- **Key Functional Specifications / Stories Included**:
  - Next.js 14+ responsive dashboard with Tailwind CSS and dark mode.
  - Multi-platform account management (QR pairing for WhatsApp/Signal, bot token entry for Discord/Viber).
  - Interactive schedule manager: Calendar view, list view, bulk search, filter by platform/status.
  - Cross-platform composer: Select sender session, target platform, recipient, and time.
  - Bulk scheduling via CSV upload and live Google Sheets integration.
- **Acceptance Criteria**:
  - [ ] Dashboard displays real-time connection status across all linked accounts.
  - [ ] Uploading a CSV with 500 rows creates scheduled messages across target platforms within 5 seconds.
  - [ ] Real-time updates reflect message state changes (`PENDING` $\rightarrow$ `SENT`) via WebSockets/SSE.

---

### EPIC-16: SaaS Monetization, Tier Quotas & Subscription Billing
- **Epic ID**: `EPIC-16`
- **Category / Domain**: Commercialization & Business Logic
- **Priority**: `P1`
- **Detailed Description & Business Value**:  
  Implement the commercial SaaS tier structure, subscription billing via Stripe, and hard quota enforcement (Free Tier: 15 msgs/mo; Pro Tier: $7.99–$9.99/mo; Business Tier: $29.99–$49.99/mo). Enables high-margin monetization ($>98\%$ gross margin) with automated upgrades.
- **Key Functional Specifications / Stories Included**:
  - Tier entitlements:
    - **Free Tier**: 15 messages/month, text-only, viral promotional footer watermark.
    - **Pro Tier**: Unlimited text, 500 active queue, images/voice notes, recurring crons, no branding.
    - **Business Tier**: Multi-platform, team shared inboxes, CSV upload, Google Sheets sync.
  - Stripe Checkout and Customer Portal integration with webhook listeners (`invoice.paid`, `customer.subscription.deleted`).
  - Quota interceptor middleware rejecting schedule requests when monthly quota is exhausted.
- **Acceptance Criteria**:
  - [ ] Free tier accounts are hard-capped at 15 dispatches per calendar month and append viral footer.
  - [ ] Completing Stripe checkout immediately upgrades account to Pro and lifts quota restrictions.
  - [ ] Subscription cancellation gracefully downgrades user at period end without deleting existing pending jobs.

---

### EPIC-17: Production Observability, Distributed Health Sweeper & Alerting
- **Epic ID**: `EPIC-17`
- **Category / Domain**: Observability & SRE Operations
- **Priority**: `P1`
- **Detailed Description & Business Value**:  
  Establish comprehensive production telemetry, metric collection, and automated failure recovery to ensure a $99.95\%$ delivery SLA. Detects latency spikes, feeder drift, socket drops, and provides automated out-of-band failure alerting.
- **Key Functional Specifications / Stories Included**:
  - Prometheus metric instrumentation:
    - `job_trigger_drift_ms` (Histogram measuring variance from scheduled time).
    - `feeder_poll_duration_ms` (Gauge tracking database poller latency).
    - `queue_size_active`, `queue_size_delayed` (BullMQ buffer depths).
    - `dispatches_total{platform, status}` (Counter).
  - Pre-built Grafana operational dashboard JSON configs.
  - Dead Letter Queue (DLQ) processor for exhausted jobs (`FAILED_PERMANENTLY`) with out-of-band notification to the sender.
  - Pino structured JSON logger with PII masking (redacts phone numbers and message content).
  - Kubernetes liveness and readiness health check endpoints (`/healthz`, `/readyz`).
- **Acceptance Criteria**:
  - [ ] Prometheus endpoint `/metrics` exports accurate drift histograms and queue metrics.
  - [ ] Grafana dashboard visualizes real-time throughput, drift $< 1.0\text{s}$, and error rates.
  - [ ] Stalled jobs failing 5 retries move to DLQ and trigger an immediate WhatsApp alert to the user.

---

### EPIC-18: Multi-Modal Media Storage Pipeline & Pre-Warming Cache
- **Epic ID**: `EPIC-18`
- **Category / Domain**: Media Pipeline & Storage Optimization
- **Priority**: `P1`
- **Detailed Description & Business Value**:  
  Handle multi-modal attachments (voice notes, images up to 5MB, PDF documents, videos up to 15MB) with minimal storage cost and zero dispatch delay. Implements a 24-hour auto-purge S3 lifecycle policy and pre-warms media into worker memory 30 seconds before dispatch for instantaneous transmission.
- **Key Functional Specifications / Stories Included**:
  - S3 / MinIO compatible object storage integration with SSE-KMS encryption.
  - Multi-modal upload pipeline for images (JPEG/PNG), voice/audio (OGG/MP3), documents (PDF), and short video (MP4 $\le 15\text{MB}$).
  - T-30s / T-5m look-ahead attachment RAM pre-warming: Downloads media to local worker buffer prior to execution time.
  - Automated 24-hour S3 lifecycle policy: Purges raw files 24 hours post-dispatch to keep storage costs negligible.
- **Acceptance Criteria**:
  - [ ] Media attachments up to 5MB dispatch with $< 1.0\text{s}$ lag due to RAM pre-warming.
  - [ ] Uploaded files automatically receive presigned URLs with 15-minute validity.
  - [ ] S3 lifecycle rules successfully purge media files 24 hours after execution.

---

## 4. Requirements Traceability Matrix (RTM)

This matrix maps every original requirement, rule, and objective to its corresponding Epic:

| Requirement / Objective | Description | Assigned Epic | Priority |
| :--- | :--- | :--- | :--- |
| **BO-01** | In-App Scheduling Capabilities | EPIC-07, EPIC-08 | P0 |
| **BO-02** | Zero Double-Sends ($0.0\%$) | EPIC-05 | P0 |
| **BO-03** | Personal Account Anti-Ban ($< 0.01\%$) | EPIC-10 | P0 |
| **BO-04** | Sub-Second Temporal Accuracy ($< 1.0\text{s}$) | EPIC-03 | P0 |
| **BO-05** | Sustainable Unit Economics ($< \$30/\text{mo}$) | EPIC-02, EPIC-03, EPIC-16, EPIC-18 | P0 / P1 |
| **BO-06** | Wall-Clock DST Invariance ($0.0\text{ min}$ drift) | EPIC-04 | P0 |
| **BR-01** | Meta 24h Window & Template Compliance | EPIC-11 | P1 |
| **BR-02** | Anti-Spam & Health Protection | EPIC-10 | P0 |
| **BR-03** | Data Privacy & Encryption at Rest | EPIC-06 | P0 |
| **BR-04** | Sender Authenticity (P2P Identity) | EPIC-09 | P0 |
| **BR-05** | Localized IANA Wall-Clock Invariance | EPIC-04 | P0 |
| **FR-AUTH-01** | User Auto-Provisioning | EPIC-02, EPIC-07 | P0 |
| **FR-AUTH-02** | Single-Phone 8-Char Pairing Code Flow | EPIC-09 | P0 |
| **FR-AUTH-03** | AES-256-GCM Signal Key Envelope Vault | EPIC-06 | P0 |
| **FR-AUTH-04** | Session Lifecycle & Circuit Breakers (401/403/515) | EPIC-09, EPIC-10 | P0 |
| **FR-WIZ-01** | Interactive FSM Initiation & 15m TTL | EPIC-07 | P0 |
| **FR-WIZ-02** | Recipient Resolution & vCard 3.0 Parsing | EPIC-07 | P0 |
| **FR-WIZ-03** | Multi-Modal Payload Capture | EPIC-07, EPIC-18 | P0 / P1 |
| **FR-WIZ-04** | Natural Language Temporal NLP (chrono-node) | EPIC-07 | P0 |
| **FR-WIZ-05** | Confirmation Preview & Interactive Buttons | EPIC-07 | P0 |
| **FR-CLI-01** | Fast-Path One-Line Schedule Command | EPIC-08 | P0 |
| **FR-CLI-02** | Recurring Fast-Path Schedule Command | EPIC-08 | P0 |
| **FR-CLI-03** | Interactive Queue Inspection (`/list`) | EPIC-08 | P0 |
| **FR-CLI-04** | Cancellation & BullMQ Memory Eviction (`/cancel`) | EPIC-08, EPIC-05 | P0 |
| **FR-CLI-05** | In-Place Job Editing (`/edit`) | EPIC-08 | P0 |
| **FR-CLI-06** | User Timezone Configuration (`/timezone`) | EPIC-08 | P0 |
| **FR-SCHED-01**| Two-Tier Look-Ahead Feeder Engine | EPIC-03 | P0 |
| **FR-SCHED-02**| Idempotency Key & Redis Mutex Lock | EPIC-05 | P0 |
| **FR-REC-01** | Single-Active-Row Recurrence Architecture | EPIC-04 | P0 |
| **FR-REC-02** | Wall-Clock DST Invariance & Disambiguation | EPIC-04 | P0 |
| **FR-REC-03** | Month-End Anchor Day & Reboot Fast-Forward | EPIC-04 | P0 |
| **FR-REL-01** | Exponential Backoff & Jittered Socket Retries | EPIC-05, EPIC-17 | P0 / P1 |
| **FR-REL-02** | Dead Letter Queue & Out-of-Band Alerts | EPIC-05, EPIC-17 | P0 / P1 |
| **FR-REL-03** | Dead-Man's Recovery Sweeper | EPIC-05 | P0 |
| **FR-META-01**| Multi-Modal Human Typing Emulation | EPIC-10 | P0 |
| **FR-META-02**| Inter-Message Serialization & Jitter Spacing | EPIC-10 | P0 |
| **FR-META-03**| 1-Click CTA Redirector (`wa.me`) | EPIC-11 | P1 |
| **FR-META-04**| 24h Customer Window Watchdog & Utility Template | EPIC-11 | P1 |
| **OMNI-01** | Pluggable Transport Adapter Architecture & SDK | EPIC-01 | P0 |
| **OMNI-02** | Polymorphic Multi-Account Session Store | EPIC-02 | P0 |
| **OMNI-03** | Viber Bot Adapter & Webhooks | EPIC-12 | P1 |
| **OMNI-04** | Discord Bot Adapter & Slash Commands | EPIC-12 | P1 |
| **OMNI-05** | Headless Signal E2EE Integration (`signal-cli`) | EPIC-13 | P1 |
| **OMNI-06** | Developer Adapter Scaffolding CLI & Test Kit | EPIC-01 | P0 |
| **OMNI-07** | Universal Web Dashboard & Cross-Platform Control | EPIC-15 | P1 |
| **OMNI-08** | SaaS Monetization, Tier Quotas & Stripe Billing | EPIC-16 | P1 |

---

## 5. Instructions for GitHub Kanban Backlog Population

A worker or GitHub automation script can ingest this specification directly. For each of the 18 Epics:
1. **GitHub Issue Title**: `[Epic] <Epic ID>: <Epic Title>` (e.g. `[Epic] EPIC-01: Enterprise Monorepo Boilerplate & Pluggable Adapter SDK`).
2. **Issue Labels**: `epic`, priority label (`priority: p0`, `priority: p1`, `priority: p2`), and domain label (e.g. `domain: core-engine`, `domain: whatsapp`, `domain: omnichannel`).
3. **Issue Body**: Use the formatted markdown section from Section 3 containing Description, Value, Included Stories, and Acceptance Criteria checklist.
4. **GitHub Projects (v2) Column**: Assign to the **Backlog** column of the Kanban board.
