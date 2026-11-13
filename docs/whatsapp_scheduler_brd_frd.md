# WhatsApp Message Scheduler Bot
## Business Requirements Document (BRD) & Functional Requirements Document (FRD)

---

# PART I: BUSINESS REQUIREMENTS DOCUMENT (BRD)
**Document Identifier:** BRD-WAPP-SCHED-V1.0  
**Status:** Approved for Implementation  
**Target:** In-WhatsApp Message Scheduler Chatbot  

## 1. Executive Summary & Vision
WhatsApp provides no native mechanism for users to schedule messages for future delivery. Existing third-party workarounds require external applications, drain phone battery, or break when devices sleep. 

The **WhatsApp Message Scheduler Bot** provides an in-chat conversational scheduling interface inside WhatsApp. Any user (**Alice**) can schedule messages for personal contacts or groups (**Bob**), achieving:
1. **100% Peer-to-Peer Authenticity**: Delivering from Alice's real phone number using companion device protocols.
2. **Zero-Double-Send Guarantee**: Cryptographic deduplication preventing relationship-damaging repeat dispatches.
3. **Wall-Clock Invariance**: True calendar-based recurrence that does not drift during Daylight Saving Time (DST).

## 2. Business Objectives & Success Criteria (SMART)
- **BO-01 (In-App Scheduling)**: Enable 100% of scheduling operations directly via WhatsApp chat.
- **BO-02 (Zero Double-Sends)**: Zero tolerance ($0.0\%$) for duplicate message deliveries.
- **BO-03 (Account Safety)**: Meta SIM-ban and account restriction rate $< 0.01\%$.
- **BO-04 (Dispatch Accuracy)**: Scheduled execution lag $< 1.0\text{ second}$ from target time.
- **BO-05 (Unit Economics)**: Operational infrastructure cost $< \$30.00 / \text{month}$ per 10,000 active scheduled messages.
- **BO-06 (Temporal Precision)**: $0.0\text{ minutes}$ drift across seasonal Daylight Saving Time transitions.

## 3. Core Business Rules (BR)
- **BR-01 (Meta Policy Compliance)**: For official Cloud API integration, messages sent after the 24-hour service window has closed must use pre-approved Meta Utility Templates.
- **BR-02 (Anti-Spam & Health)**: Prohibits unconsented mass broadcasts. Implements human-paced typing cadence (35–55 ms/char) to protect personal account standing.
- **BR-03 (Privacy & Encryption)**: All Signal cryptographic pre-keys and session tokens must be envelope-encrypted with AES-256-GCM at rest. Contact data must be purged upon user account deletion request.
- **BR-04 (Wall-Clock Invariance)**: Reminders are anchored strictly in the user's localized IANA timezone, ensuring local wall-clock stability.

## 4. Financial Viability & Unit Economics
- **1,000 msgs/month**: Cloud API Assistive Model (\$6.26/mo) vs. Baileys Companion Node (\$12.00/mo).
- **10,000 msgs/month**: Cloud API Assistive Model (\$27.60/mo) vs. Baileys Companion Node (\$28.00/mo).
- **100,000 msgs/month**: Cloud API Assistive Model (\$206.00–\$1,130.00/mo) vs. Baileys Companion Node (**\$160.00/mo — up to 85% cost savings at scale**).

---

# PART II: FUNCTIONAL REQUIREMENTS DOCUMENT (FRD)
**Document Identifier:** FRD-WAPP-SCHED-V1.0  
**Status:** Approved for Implementation  
**Target:** Engineering & QA Teams  

## 1. Functional Architecture & Module Breakdown

```
+─────────────────────────────────────────────────────────────────────────────────────────────+
|                                    FUNCTIONAL MODULES                                       |
+──────────────────────────┬──────────────────────────────────────────────────────────────────+
| Module Identifier        | Scope & Functional Focus                                         |
+──────────────────────────┼──────────────────────────────────────────────────────────────────+
| FR-AUTH (Authentication) | User auto-provisioning, single-phone 8-char pairing codes,       |
|                          | AES-256-GCM Signal key envelope encryption, disconnect handlers. |
+──────────────────────────┼──────────────────────────────────────────────────────────────────+
| FR-WIZ (Guided Wizard)   | 5-step interactive wizard (Recipient vCard, Media/Text payload,  |
|                          | Chrono NLP time, Recurrence selection, and Confirmation cards).  |
+──────────────────────────┼──────────────────────────────────────────────────────────────────+
| FR-CLI (Command Grammar) | Fast-path slash commands: `/schedule`, `/list`, `/cancel`,       |
|                          | `/edit`, `/timezone`, with synchronous BullMQ queue eviction.    |
+──────────────────────────┼──────────────────────────────────────────────────────────────────+
| FR-SCHED (Hybrid Queue)  | PostgreSQL 16 durable master ledger, 60s Look-Ahead Feeder,      |
|                          | 5-minute sliding BullMQ delayed queue buffer.                    |
+──────────────────────────┼──────────────────────────────────────────────────────────────────+
| FR-REC (Recurrence Math) | Single Active Row recurrence, wall-clock DST invariance,         |
|                          | month-end anchor day preservation, and reboot fast-forwarding.   |
+──────────────────────────┼──────────────────────────────────────────────────────────────────+
| FR-REL (Reliability)     | Deterministic 22-char `3EB0...` stanza IDs, Redis Redlock mutex, |
|                          | dead-man's-switch sweeper, per-sender typing cadence pacing.     |
+──────────────────────────┼──────────────────────────────────────────────────────────────────+
| FR-META (Cloud API Model)| 1-click `wa.me` CTA redirector, 24h customer service window      |
|                          | watchdog, and automated Utility Template fallback routing.       |
+──────────────────────────┴──────────────────────────────────────────────────────────────────+
```

## 2. Key Functional Specifications

### 2.1 FR-AUTH: Single-Phone Pairing Code Flow
To ensure smartphone users chatting with the bot do not need a second device to scan a QR code, the bot implements WhatsApp's native 8-character pairing code mechanism:
1. User issues `/link` in chat.
2. Bot invokes `await sock.requestPairingCode(userPhoneNumber)`.
3. Bot replies with the formatted code (e.g., `K9X4-M2P7`).
4. User taps the native WhatsApp push notification *"Enter code to link new device"* to pair.

### 2.2 FR-WIZ: 5-Step Guided Wizard State Machine
1. **Step 1 (Recipient)**: Ingests vCard contact cards, E.164 phone numbers, or saved aliases. Performs pre-flight membership verification on `@g.us` group chats.
2. **Step 2 (Payload)**: Buffers text or streams multimodal media (images, audio notes, documents, video) to S3, pre-warming media for instantaneous delivery.
3. **Step 3 (Timing)**: Resolves natural language expressions (e.g. *"tomorrow at 9:30am"*) using `chrono-node` in the user's IANA timezone; enforces minimum $+60\text{s}$ future threshold.
4. **Step 4 (Recurrence)**: Selects Once, Daily, Weekdays, Weekly, or Monthly.
5. **Step 5 (Confirmation)**: Displays structured preview card with `[✅ Confirm]`, `[✏️ Edit]`, and `[❌ Cancel]` interactive buttons.

### 2.3 FR-SCHED: Two-Tier Hybrid Scheduling
- **Tier 1 (PostgreSQL Master)**: Stores all future jobs. Partial B-tree index on `(next_run_at_utc ASC) WHERE status IN ('PENDING', 'QUEUED')` keeps scans under $< 0.2\text{ ms}$.
- **Tier 2 (BullMQ Delayed Buffer)**: 60-second Look-Ahead Feeder stages jobs firing within the next 5 minutes using `FOR UPDATE SKIP LOCKED`. Delayed workers fire with sub-second accuracy.

### 2.4 FR-REC: Wall-Clock Recurrence & Month-End Anchor Day
- **DST Invariance**: Converts UTC to user local time via Luxon, increments by calendar days/weeks, and converts back to UTC.
- **Anchor Day Invariance**: Preserves original anchor day (e.g. 31st). When stepping through February (snapped to Feb 28/29), automatically restores execution to March 31, April 30, and May 31.
- **Reboot Fast-Forwarding**: After extended server outages, overdue recurring jobs step forward past `NOW()` to prevent bursts of historical spam.

### 2.5 FR-REL: Zero-Double-Send Guarantee
- **22-Char WhatsApp Stanza ID**: Derived as `WA_MSG_ID = "3EB0" + SHA256(job_uid + ":" + next_run_utc_iso).slice(0, 18).toUpperCase()`. WhatsApp servers automatically drop duplicate socket retries.
- **Dead-Man's-Switch Sweeper**: Background sweeper runs every 2 minutes, recovering `PROCESSING` jobs older than 5 minutes and stalled `QUEUED` jobs whose scheduled time is $> 3\text{ minutes}$ in the past.

---

## 3. Requirements Traceability Matrix (RTM)

| Business Objective (BRD) | Functional Requirement (FRD) | Verification Strategy |
| :--- | :--- | :--- |
| **BO-01: In-App Scheduling** | FR-WIZ-01 to FR-WIZ-06, FR-CLI-01 | E2E Wizard & CLI Cypress / Vitest suites |
| **BO-02: Zero Double-Sends** | FR-REL-01, FR-REL-02, FR-SCHED-04 | Chaos monkey worker `SIGKILL` test during socket ACK |
| **BO-03: Anti-Ban Protection** | FR-AUTH-04, FR-REL-03 | Pacing telemetry audit & 500-message burst pacing run |
| **BO-04: Sub-Second Timing** | FR-SCHED-02, FR-SCHED-03 | Prometheus latency histograms (`job_trigger_drift_ms`) |
| **BO-05: Unit Economics** | FR-META-02, FR-SCHED-01 | S3 24h lifecycle cleanup & Utility Template routing check |
| **BO-06: DST Invariance** | FR-REC-02, FR-REC-03 | 39-test timezone test suite (Spring/Fall DST transitions) |
