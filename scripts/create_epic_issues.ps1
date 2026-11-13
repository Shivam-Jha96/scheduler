# scripts/create_epic_issues.ps1
# Creates all 12 BRD/FRD Epics as GitHub Issues in Shivam-Jha96/scheduler

$repo = "Shivam-Jha96/scheduler"

$epics = @(
  @{
    title = "[EPIC-01] Authentication & Companion Device Pairing (FR-AUTH)"
    body = @"
## 🎯 Objective
Establish robust multi-device peer-to-peer session management using `@whiskeysockets/baileys` Noise_XX protocol with seamless single-phone pairing code flows.

## 💼 Business Value
Enables personal 1-to-1 message scheduling without requiring corporate Meta WABA accounts or expensive third-party BSPs. Maintains sender authenticity so recipients see Alice's personal phone number and avatar.

## 📋 Requirements Traceability
- **BRD Business Objectives**: BO-01 (In-App Scheduling), BO-03 (Account Safety & Anti-Ban)
- **Business Rules**: BR-03 (Data Privacy & Encryption at Rest), BR-04 (Sender Authenticity)
- **Functional Requirements**:
  - `FR-AUTH-01`: Auto-Provisioning on first inbound message
  - `FR-AUTH-02`: Single-phone 8-character pairing code flow (`sock.requestPairingCode`)
  - `FR-AUTH-03`: AES-256-GCM Signal pre-key envelope encryption vault
  - `FR-AUTH-04`: Session lifecycle & circuit breakers (Code 401 unlinked, 403 banned, 515 restart backoff)

## 🛠️ Acceptance Criteria
- [ ] Single-phone 8-character pairing code flow (`/link` -> `requestPairingCode`) functions cleanly without a secondary screen.
- [ ] Session credentials and Signal pre-keys are envelope-encrypted with AES-256-GCM using KMS keys before persistence.
- [ ] Automatic reconnect with exponential backoff on transient socket drops (code 515).
- [ ] Circuit breakers freeze session and alert user immediately on 401 unlinked or 403 banned errors.
- [ ] Multi-device session remains valid across weeks as long as primary phone is active on WhatsApp every 14 days.
"@
  },
  @{
    title = "[EPIC-02] In-Chat Conversational Guided Wizard (FR-WIZ)"
    body = @"
## 🎯 Objective
Implement an interactive 5-step conversational wizard within WhatsApp chats powered by an in-memory Redis finite state machine (FSM).

## 💼 Business Value
Eliminates external app dependencies, allowing everyday users to schedule reminders in under 30 seconds directly inside WhatsApp without learning complex commands.

## 📋 Requirements Traceability
- **BRD Business Objectives**: BO-01 (In-App Scheduling), BO-04 (Dispatch Accuracy), BO-06 (Temporal Precision)
- **Functional Requirements**:
  - `FR-WIZ-01`: In-memory draft state machine with 15-minute inactivity TTL
  - `FR-WIZ-02`: Recipient resolution (vCard 3.0, E.164 phone numbers, aliases, group permissions)
  - `FR-WIZ-03`: Multi-modal payload capture (text up to 4,096 chars, images, audio/voice, documents, videos)
  - `FR-WIZ-04`: Natural language temporal parsing via `chrono-node` with user timezone anchor
  - `FR-WIZ-05`: Confirmation preview card with interactive buttons (Confirm, Edit, Cancel)

## 🛠️ Acceptance Criteria
- [ ] Inactive wizard sessions automatically expire after 15 minutes with memory reclaimed.
- [ ] Parser accepts vCard 3.0 contact cards, raw E.164 phone numbers, and saved contact aliases.
- [ ] Natural language expressions ("tomorrow at 9:30am") resolved relative to user's localized IANA timezone.
- [ ] Confirmation card renders with interactive `[✅ Confirm]`, `[✏️ Edit]`, and `[❌ Cancel]` buttons.
- [ ] Tapping `[✏️ Edit]` allows stepping back to any previous field without losing other entered data.
"@
  },
  @{
    title = "[EPIC-03] Command Grammar & Fast-Path Slash Interface (FR-CLI)"
    body = @"
## 🎯 Objective
Build a high-throughput, atomic command grammar interface for power users, automated systems, and quick scheduling.

## 💼 Business Value
Reduces interaction friction from 5 conversational turns to 1 atomic command turn for repeated power users and business operators.

## 📋 Requirements Traceability
- **BRD Business Objectives**: BO-01 (In-App Scheduling)
- **Functional Requirements**:
  - `FR-CLI-01`: Fast-Path `/schedule <target> <time> | <message>` for one-off dispatches
  - `FR-CLI-02`: Recurring CLI `/schedule --repeat <rule> <target> <time> | <message>`
  - `FR-CLI-03`: Queue inspection `/list [pending|sent|all] [page]`
  - `FR-CLI-04`: Cancellation & BullMQ eviction `/cancel <job_uid>`
  - `FR-CLI-05`: In-place editing `/edit <job_uid> <field> <new_val>`
  - `FR-CLI-06`: Timezone configuration `/timezone <IANA_zone>`

## 🛠️ Acceptance Criteria
- [ ] `/schedule <target> <time> | <message>` schedules atomically in a single message turn.
- [ ] `/list` cleanly paginates and displays active jobs with localized timestamps and status badges (`🟡 PENDING`, `🟢 SENT`, `🔴 FAILED`).
- [ ] `/cancel <job_uid>` updates database to `CANCELLED` and evicts in-flight job from BullMQ.
- [ ] In-place edit `/edit` updates database parameters and reschedules in-flight jobs.
- [ ] Syntax errors provide clear correction examples and parameter hints.
"@
  },
  @{
    title = "[EPIC-04] Two-Tier Hybrid Scheduling Engine (FR-SCHED)"
    body = @"
## 🎯 Objective
Implement the distributed Two-Tier Hybrid Scheduling architecture combining PostgreSQL 16 durable storage with BullMQ/Redis sliding-window delay queues.

## 💼 Business Value
Solves database connection exhaustion and polling latency while preventing millions of long-term jobs from exhausting expensive Redis RAM. Delivers sub-second dispatch precision (< 1.0s variance).

## 📋 Requirements Traceability
- **BRD Business Objectives**: BO-04 (Sub-Second Accuracy < 1.0s drift), BO-05 (Sustainable Unit Economics < $30/mo)
- **Functional Requirements**:
  - `FR-SCHED-01`: 60s Look-Ahead Feeder querying PostgreSQL using `FOR UPDATE SKIP LOCKED` for jobs due in next 5 minutes
  - `FR-SCHED-02`: BullMQ Redis delayed queue buffer with millisecond countdown timers
  - `FR-SCHED-03`: Distributed worker pool consuming triggers and invoking target channel adapters

## 🛠️ Acceptance Criteria
- [ ] 60-second cron feeder queries PostgreSQL using `FOR UPDATE SKIP LOCKED` for jobs due in next 5 minutes.
- [ ] Redis memory usage for 10,000 pending jobs remains below 250 KB (only 5-minute sliding window buffered).
- [ ] Horizontal feeder scaling produces zero race conditions or duplicate claims across nodes.
- [ ] Poller execution time remains < 0.5ms under 100,000 synthetic rows using partial B-tree index.
- [ ] Jobs scheduled 30 days in advance execute within ±1000 ms of target timestamp.
"@
  },
  @{
    title = "[EPIC-05] Temporal Mathematics & Wall-Clock Recurrence (FR-REC)"
    body = @"
## 🎯 Objective
Build a mathematically robust recurrence calculation engine using Luxon guaranteeing local wall-clock invariance across seasonal Daylight Saving Time shifts and month-end boundary conditions.

## 💼 Business Value
Eliminates reminder drift (BO-06, BR-05). Users scheduled for 9:00 AM local time receive messages at exactly 9:00 AM regardless of 23h spring-forward or 25h fall-back transitions.

## 📋 Requirements Traceability
- **BRD Business Objectives**: BO-06 (Temporal Precision & DST Invariance: 0.0 min drift)
- **Business Rules**: BR-05 (Wall-Clock Invariance anchored to user IANA timezone)
- **Functional Requirements**:
  - `FR-REC-01`: Single-Active-Row recurrence state machine (updating existing row in-place)
  - `FR-REC-02`: Calendar-day Luxon DST arithmetic (UTC -> Local -> Calendar Add -> UTC)
  - `FR-REC-03`: Month-End Anchor Day preservation (Jan 31 -> Feb 28 -> Mar 31)
  - `FR-REC-04`: Server reboot fast-forwarding / misfire handling past `NOW()`

## 🛠️ Acceptance Criteria
- [ ] Single active row updated in-place upon execution to avoid runaway row duplication.
- [ ] Month-end anchor day (Jan 31 -> Feb 28/29 -> Mar 31 -> Apr 30) preserved without day drift.
- [ ] DST transition test suite passes 100% across New York, London, Sydney, and UTC.
- [ ] Extended server downtime of 4 hours fast-forwards overdue recurring jobs past `NOW()` and marks skipped runs as `MISFIRED`.
"@
  },
  @{
    title = "[EPIC-06] Reliability, Deduplication & Anti-Ban Telemetry (FR-REL)"
    body = @"
## 🎯 Objective
Enforce an end-to-end zero-double-send guarantee (0.0% tolerance) and human-like behavioral telemetry to protect accounts from algorithmic bans.

## 💼 Business Value
Eliminates relationship damage caused by duplicate message blasts (BO-02) and maintains personal account restriction rate < 0.01% (BO-03).

## 📋 Requirements Traceability
- **BRD Business Objectives**: BO-02 (Zero Double-Sends: 0.0%), BO-03 (Account Safety: < 0.01% ban rate)
- **Business Rules**: BR-02 (Anti-Spam & Health Protection)
- **Functional Requirements**:
  - `FR-REL-01`: Exponential backoff with jitter (2s, 4s, 8s, 16s, 32s + 500ms)
  - `FR-REL-02`: Dead Letter Queue (DLQ) & out-of-band user alerts
  - `FR-REL-03`: Dead-Man's-Switch background recovery sweeper (runs every 2m for jobs > 5m in PROCESSING)
  - `FR-META-01`: Human typing emulation (`composing` state 35–55 ms/char, clamped 1.5s–4.0s)
  - `FR-META-02`: Inter-message serialization & jitter spacing (3–6s known contacts, 8–15s new contacts)

## 🛠️ Acceptance Criteria
- [ ] Deterministic 22-char stanza ID (`"3EB0" + SHA256(...)`) enforces WhatsApp socket deduplication.
- [ ] Distributed Redis mutex (`SET lock:job:{id} NX EX 600`) acquired prior to transport dispatch.
- [ ] Outbound messages emit human-paced `composing` presence before text transmission.
- [ ] Dead-Man's Sweeper automatically recovers orphaned `PROCESSING` jobs older than 5 minutes.
- [ ] Zero duplicate messages dispatched during chaos testing with worker `SIGKILL`.
"@
  },
  @{
    title = "[EPIC-07] Cloud API Enterprise Model & Template Routing (FR-META)"
    body = @"
## 🎯 Objective
Implement official WhatsApp Business Cloud API integration supporting both 24-hour service window messaging and automated Meta Utility Template fallback.

## 💼 Business Value
Provides an enterprise-grade, zero-ban-risk channel for corporate entities, high-volume transactional notifications, and automated template dispatches.

## 📋 Requirements Traceability
- **BRD Business Objectives**: BO-01 (In-App Scheduling), BO-05 (Sustainable Unit Economics)
- **Business Rules**: BR-01 (Meta Policy & 24h Customer Service Window Compliance)
- **Functional Requirements**:
  - `FR-META-03`: 1-Click CTA redirector service (`https://sched.app/r/{job_uid}` -> `whatsapp://send?phone={phone}&text={msg}`)
  - `FR-META-04`: 24-Hour customer window watchdog (`NOW() - last_inbound >= 24h`)
  - Automated Utility Template fallback routing (`scheduled_reminder_cta_v1`)
  - Webhook receiver with `X-Hub-Signature-256` HMAC-SHA256 verification

## 🛠️ Acceptance Criteria
- [ ] Inbound webhooks process and acknowledge Meta with HTTP 200 OK within < 200ms.
- [ ] 1-Click CTA service (`https://sched.app/r/{job_uid}`) 302-redirects to pre-filled WhatsApp chat in 1 tap.
- [ ] Watchdog detects elapsed 24-hour window and automatically routes notification via approved Utility Template.
- [ ] Messages attempted outside the 24h window deliver cleanly without triggering Error 131047.
"@
  },
  @{
    title = "[EPIC-08] Unified Transport Abstraction Layer (IMessagingTransportAdapter)"
    body = @"
## 🎯 Objective
Establish the decoupled hexagonal transport adapter architecture isolating core scheduling logic from third-party chat protocols.

## 💼 Business Value
Allows independent teams to author, test, and maintain channel adapters (WhatsApp, Discord, Viber, Signal, etc.) without risking core scheduler regressions.

## 📋 Requirements Traceability
- **Omnichannel Requirements**:
  - `OMNI-01`: Transport-Agnostic Core (`IMessagingTransportAdapter` contract)
  - `OMNI-02`: Polymorphic multi-account session store (`user_platform_sessions`)
  - `OMNI-06`: Developer Extensibility SDK (`@scheduler/adapter-sdk`, `@scheduler/adapter-test-kit`, scaffolding CLI)
- **Packages**:
  - `packages/adapter-sdk`
  - `packages/adapter-registry`
  - `packages/adapter-test-kit`
  - `tools/create-adapter`

## 🛠️ Acceptance Criteria
- [ ] Standardized `IChannelAdapter` contract implemented by all adapter packages.
- [ ] Inversion of Control `AdapterRegistry` resolves channel adapters dynamically at runtime.
- [ ] Running `npm run create:adapter -- --name <channel>` generates fully compliant boilerplate.
- [ ] `@scheduler/adapter-test-kit` validates contract compliance across all adapters.
- [ ] Core scheduling modules have zero direct compile-time dependencies on specific transport libraries.
"@
  },
  @{
    title = "[EPIC-09] High-Volume Compliant Adapters (Viber & Discord)"
    body = @"
## 🎯 Objective
Build official, policy-compliant channel adapters for Discord (Gateway v10) and Viber (REST Bot API).

## 💼 Business Value
Expands market reach to 1.1B Viber users and 200M Discord MAUs with zero account ban risks through official developer bot APIs.

## 📋 Requirements Traceability
- **Omnichannel Scale-Out Requirements**:
  - `OMNI-03`: Official Viber REST Bot API adapter with 1-to-1 reminders and interactive carousels
  - `OMNI-04`: Official Discord Bot API (`discord.js`, Gateway v10) with native slash commands
- **Workspaces**:
  - `adapters/discord`
  - `adapters/viber`

## 🛠️ Acceptance Criteria
- [ ] Discord bot supports native `/schedule` slash commands with interactive time pickers.
- [ ] Discord dispatches scheduled messages to channels, threads, and direct messages.
- [ ] Viber bot handles inbound webhooks and delivers 1-to-1 reminders with rich keyboard carousels.
- [ ] Both adapters achieve 100% pass rate in `@scheduler/adapter-test-kit` contract verification.
"@
  },
  @{
    title = "[EPIC-10] Privacy & Ecosystem Bridges (Signal, LINE, iMessage)"
    body = @"
## 🎯 Objective
Implement privacy-first and regional messaging adapters including containerized `signal-cli`, official LINE Messaging API, and macOS AppleScript/BlueBubbles iMessage bridge.

## 💼 Business Value
Captures privacy-conscious users (50M Signal MAUs), regional dominance in Japan/Taiwan/Thailand (LINE), and North American prosumers (iMessage blue-bubbles).

## 📋 Requirements Traceability
- **Omnichannel Scale-Out Requirements**:
  - `OMNI-05`: Headless Signal E2EE integration (`signal-cli` JSON-RPC secondary linked device)
  - `EPIC-13`: Privacy ecosystem expansion for Signal
  - `EPIC-14`: Regional & prosumer bridges for LINE & iMessage
- **Adapters**:
  - `adapters/signal`
  - `adapters/line`
  - `adapters/imessage`

## 🛠️ Acceptance Criteria
- [ ] Headless `signal-cli` secondary linked device sends E2EE cloud-queued messages while sender phone is offline.
- [ ] User pairs Signal account via linked device QR code in web dashboard.
- [ ] LINE adapter delivers scheduled flex message cards through official Messaging API.
- [ ] iMessage bridge relays scheduled text to recipient phone numbers via connected macOS host.
"@
  },
  @{
    title = "[EPIC-11] Centralized Control Plane & Web Management Dashboard"
    body = @"
## 🎯 Objective
Deliver a modern Next.js responsive web application for multi-channel account management, visual calendar queue inspection, and bulk scheduling.

## 💼 Business Value
Empowers business operators, marketing teams, and prosumers to manage cross-platform dispatches with calendar overviews and bulk CSV imports.

## 📋 Requirements Traceability
- **Omnichannel Requirements**:
  - `OMNI-07`: Universal Web Management Portal
  - `OMNI-08`: SaaS Monetization, Tier Quotas & Stripe Subscription Billing
  - `EPIC-15`: Universal Web Dashboard & Cross-Platform Control Plane
- **Applications**:
  - `apps/web-dashboard`
  - `apps/api-gateway`

## 🛠️ Acceptance Criteria
- [ ] Web portal displays real-time connection status across linked WhatsApp, Signal, Discord, and Viber accounts.
- [ ] Interactive calendar view visualizes upcoming dispatches with search and filter capabilities.
- [ ] Bulk CSV upload schedules hundreds of dispatches across target channels in seconds.
- [ ] Real-time job status updates stream to browser via WebSockets / Server-Sent Events.
- [ ] Tier quota middleware enforces message caps based on subscription tier (Free, Pro, Business).
"@
  },
  @{
    title = "[EPIC-12] Multi-Modal Media Storage & Pre-Warming Cache Engine"
    body = @"
## 🎯 Objective
Architect a high-speed, cost-optimized multi-modal media attachment pipeline supporting voice notes, images, PDFs, and videos with RAM pre-warming.

## 💼 Business Value
Keeps operational cloud storage costs negligible via 24-hour auto-purge lifecycles while ensuring instantaneous transmission without network fetch lag.

## 📋 Requirements Traceability
- **BRD Business Objectives**: BO-05 (Sustainable Unit Economics: < $30/mo)
- **Functional Requirements**:
  - `FR-WIZ-03`: Multi-Modal Payload Capture (images, voice, PDF, video)
  - `EPIC-18`: Multi-Modal Media Storage Pipeline & Pre-Warming Cache
- **Storage Infrastructure**:
  - S3 / MinIO compatible object storage with SSE-KMS encryption
  - T-30s / T-5m memory pre-warming cache in delivery workers

## 🛠️ Acceptance Criteria
- [ ] Multi-modal upload pipeline securely ingests images, voice notes, PDFs, and video up to 15MB.
- [ ] T-30s Look-Ahead pre-warms media into worker memory buffer prior to execution time.
- [ ] Media attachments up to 5MB dispatch with < 1.0s variance from target timestamp.
- [ ] Uploaded files automatically receive presigned URLs with 15-minute validity.
- [ ] Automated S3 lifecycle rules permanently purge media files 24 hours post-dispatch.
"@
  }
)

Write-Host "Creating 12 Epic Issues on $repo..."
$issueUrls = @()

foreach ($epic in $epics) {
    Write-Host "Creating issue: $($epic.title)..."
    $url = gh issue create -R $repo --title "$($epic.title)" --body "$($epic.body)" --label "epic,brd"
    Write-Host "  -> Created: $url"
    $issueUrls += @{
        title = $epic.title
        url = $url
    }
}

$issueUrls | ConvertTo-Json -Depth 3 | Out-File -FilePath "scripts/created_issues.json" -Encoding utf8
Write-Host "Successfully created all 12 Epic issues!"
