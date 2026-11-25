# SchedulerBot — Final Test Design & Test Case Catalog (`Model C v4.4 HYBRID`)

> **Scope**: Exhaustive, traceable test design covering **all four architectural approaches** — (1) Phase 1 MVP Model C v4.4 HYBRID, (2) Phase 2 Wall-Clock Recurrence & Slash Grammar, (3) Phase 2 Omnichannel Hexagonal SDK, Adapters & SaaS Control Plane, and (4) Retired V1.2 / `EPIC-12` Negative Security & Regression Guardrails.  
> **Dataset Cross-References**: Every test case binds to deterministic production-grade fixtures in [`tests/datasets/`](../datasets/).

---

## Approach 1 — Phase 1 MVP: Model C v4.4 HYBRID (`M0`–`M4`)

### 1.1 Sender Identity Bootstrapping & User Ledger (`EPIC-01` / `FR-AUTH-01..04`)

| Test ID | Scenario | Input / Precondition | Expected Outcome & Assertion | Dataset / Suite |
| :--- | :--- | :--- | :--- | :--- |
| **`TC-AUTH-01`** | Step 0 First-Contact Auto-Bootstrap | Inbound webhook from unknown `wa_id: 919876543210`, `profile.name: "Alice"` | Creates `users` row with 64-hex `sender_phone_hash`, `App_DEK`-encrypted `sender_phone_encrypted` & `sender_name_encrypted` (zero name hash), infers timezone `+91 -> Asia/Kolkata`. | `mockapi_v4_4_canonical_payloads.json` |
| **`TC-AUTH-02`** | Display Name Update (`NAME <Preferred>`) | Alice sends `NAME Alice C.` | Deterministic fast-path (`< 50 ms`, `0` NLU calls) updates `users.sender_name_encrypted` in RAM and zeroes plaintext buffer. | `mockapi_v4_4_canonical_payloads.json` |
| **`TC-AUTH-03`** | E.164 Prefix Timezone Inference | New senders from `+91`, `+971`, `+44`, `+1`, and unlisted prefix `+81` | Maps to `Asia/Kolkata`, `Asia/Dubai`, `Europe/London`, `America/New_York`, and fallback `'Asia/Kolkata'`. | `nlu_golden_dataset.json` |
| **`TC-AUTH-04`** | Zero-Name-Hash Schema Invariant | Inspect PostgreSQL `information_schema.columns` & DDL SQL files | `0` columns matching `*name_hash*`; `lint:v12-guard` rejects any PR adding name hash columns. | `security-privacy-retention.spec.ts` |

### 1.2 NLU Parsing, Plain-Text Gate & Hard Consent Gate (`EPIC-02` / `FR-WIZ-01..05`)

| Test ID | Scenario | Input / Precondition | Expected Outcome & Assertion | Dataset / Suite |
| :--- | :--- | :--- | :--- | :--- |
| **`TC-NLU-01`** | Imbalanced 4-Class Macro-F1 Benchmark | Full golden dataset across `SCHEDULE_RELAY`, `CANCEL_SCHEDULE`, `OPT_OUT`, `UNKNOWN` (English + Hinglish code-mixing) | Per-class `F1 >= 0.90` and overall **Macro-F1 `>= 0.92`**. | `nlu_golden_dataset.json`, `nlu-calibration-and-dataset.spec.ts` |
| **`TC-NLU-02`** | Confidence Calibration & Band Routing | Ambiguous prompts (e.g., `"Remind Bob at 7"` at 14:00 IST) | **ECE `<= 0.05`**; `[0.65, 0.89]` triggers interactive confirmation card; `< 0.65` triggers clarification; `>= 0.90` proceeds. | `nlu-calibration-and-dataset.spec.ts` |
| **`TC-NLU-03`** | Deterministic Escape Hatch Under NLU `503` | Send `STOP`, `START`, `NAME Alice`, `UNSUBSCRIBE Alice`, or button reply while NLU returns `HTTP 503` | Regex router intercepts in **`< 50 ms`** without invoking NLU; action succeeds end-to-end. | `nlu-calibration-and-dataset.spec.ts` |
| **`TC-NLU-04`** | Plain-Text UTF-8 `<= 500` Char Gate (`BR-02`) | Message lengths `1`, `500`, `501`, and inbound `image`/`video`/`audio`/`document` webhook | `1` & `500` accepted; `501` rejected with clear error; all multimedia types rejected immediately (`EPIC-12` retired). | `nlu_golden_dataset.json`, `m0-hygiene.test.ts` |
| **`TC-NLU-05`** | Missing Phone Contact-Card Flow | `"Remind John tomorrow at 10am"` followed by WhatsApp `contacts` vCard while in `conversation_states = AWAITING_RECIPIENT_PHONE` | Checks `conversation_states` before rejecting `contacts` message; extracts E.164 phone; expires stale state in `<= 15 min`. | `mockapi_v4_4_canonical_payloads.json` |
| **`TC-NLU-06`** | Schedule Creation `< 10m` vs `>= 10m` | `T0 = now + 5m` vs `T0 = now + 60m` | `< 10m` creates row in **`FAST_TRACK`**; `>= 10m` creates row in **`PENDING`** with `notify_at = scheduled_at - 10m` (`chk_notify_precedes_schedule`). | `fsm-and-cas-contracts.spec.ts` |

### 1.3 5-Stage Hybrid Lifecycle, 10-State FSM & CAS Concurrency (`EPIC-04` / `FR-SCHED-01..05`)

| Test ID | Scenario | Input / Precondition | Expected Outcome & Assertion | Dataset / Suite |
| :--- | :--- | :--- | :--- | :--- |
| **`TC-FSM-01`** | Complete 10-State Enum & Transition Matrix | Every valid & illegal `(from_status -> to_status)` pair across all 10 states | All valid transitions succeed with `version = version + 1` and append to `scheduled_message_events`; all terminal-state mutations (`SENT_VIA_PERSONAL`, `SENT_VIA_BOT`, `CANCELLED`, `EXPIRED`, `FAILED`) are rejected. | `fsm_transitions_and_chaos_matrix.json`, `fsm-and-cas-contracts.spec.ts` |
| **`TC-FSM-02`** | Happy Path: `$0.00` Personal P2P Send | `PENDING -> NOTIFIED (T-10m) -> AWAITING_CONFIRMATION (T0)` -> Alice taps `✅ I Sent It` | Sets `personal_send_confirmed_at = NOW()`, transitions to `SENT_VIA_PERSONAL`, increments `scheduler_personal_sends_confirmed_total`, `0` Bot Relay messages sent. | `fsm-and-cas-contracts.spec.ts` |
| **`TC-FSM-03`** | `T+3m` Escalation Atomic Single-Send | Multiple worker pods poll `AWAITING_CONFIRMATION` at `T+3m` (`250 ms` concurrency burst) | Atomic `WHERE escalated_at IS NULL` guard ensures `hybrid_escalation_v1` dispatches **exactly once**. | `fsm-and-cas-contracts.spec.ts` |
| **`TC-FSM-04`** | `T+10m` Autonomous Bot Relay (`auto_fallback=TRUE`, `OPTED_IN`) | Unconfirmed at `T+10m`; Bob `OPTED_IN` and NOT in `recipient_global_opt_outs` | CAS claim acquires 30s lease (`DISPATCHING`); worker joins `users` (Erratum A.2 #4) to format `{{1}} = "Alice (+91-98XXX-43210)"`, `{{2}} = plaintext`, `{{3}} = "Alice"`; sends `scheduled_relay_v1`; transitions to `SENT_VIA_BOT`; **immediately shreds** `dek_encrypted = E'\\x00'::bytea`, `message_content_encrypted = E'\\x00'::bytea`, `wa_me_link = ''`. | `fsm-and-cas-contracts.spec.ts`, `mockapi-v4-4-contract.spec.ts` |
| **`TC-FSM-05`** | `T+10m` Expiration (`auto_fallback=FALSE` or Unconsented) | Unconfirmed at `T+10m` with `auto_fallback = FALSE` (or Bob `UNKNOWN`/`OPTED_OUT`) | Transitions cleanly to **`EXPIRED`**; `0` outbound messages sent to Bob. | `fsm-and-cas-contracts.spec.ts` |
| **`TC-CHAOS-01`** | `N=10` Concurrent Worker CAS Race | 10 workers simultaneously execute Step 1 CAS claim on same `AWAITING_CONFIRMATION` row | Strictly **`<= 1` worker** receives `rowCount = 1`; remaining 9 receive `0` rows (`scheduler_idempotency_conflicts_total` incremented). | `fsm_transitions_and_chaos_matrix.json`, `fsm-and-cas-contracts.spec.ts` |
| **`TC-CHAOS-02`** | 1,000-Iteration `[✅ I Sent It]` vs `T+10m` Race | Concurrent personal confirmation webhook vs Bot Fallback CAS claim (1,000 iterations) | **`0.000%` double-sends**; if personal confirmation wins, CAS returns `0` rows and emits `DoubleSendAttemptBlocked` diagnostic metric. | `fsm-and-cas-contracts.spec.ts` |
| **`TC-CHAOS-03`** | Worker `SIGKILL` Mid-Dispatch + Bounded Reaper (`Erratum A.2 #7`) | Kill worker after Meta `POST` before DB commit; advance clock `> 30s` across retries `0 -> 1 -> 2 -> 3` | 10s `pg_cron` reaper reclaims lease in `< 40s`; retry `3` transitions to **`FAILED`** (`error_code = 'LEASE_RETRIES_EXHAUSTED'`) with `retry_count <= max_retries` (`3 <= 3`, zero `chk_retry_bounds` violation); Meta deduplicates via `biz_opaque_callback_data`. | `fsm-and-cas-contracts.spec.ts` |
| **`TC-CHAOS-04`** | Meta `HTTP 429 Retry-After` Non-Blocking Release | MockAPI returns `HTTP 429` with `Retry-After: 12` | Worker releases lease immediately (`lease_owner = NULL`), sets `next_retry_at = NOW() + 12s`, returns status to `AWAITING_CONFIRMATION` without blocking worker thread. | `mockapi_v4_4_canonical_payloads.json` |

### 1.4 Hard Consent Gate, `< 5s` Two-Tier Opt-Out & Quotas (`EPIC-15`)

| Test ID | Scenario | Input / Precondition | Expected Outcome & Assertion | Dataset / Suite |
| :--- | :--- | :--- | :--- | :--- |
| **`TC-OPT-01`** | Tier 2 Global Bare `STOP` (`<= 5,000 ms` SLA) | Bob sends `STOP` or taps `[🛑 STOP / Opt-Out]` while 5 active schedules exist across 3 senders | ACID transaction (`< 25 ms`) inserts `recipient_global_opt_outs`, cascade-cancels all 5 active schedules (`CANCELLED`), sends `scheduled_cancelled_v1` to senders, increments `scheduler_opt_out_total{tier="GLOBAL"}` & `scheduler_cascade_cancellations_total`. | `security_privacy_and_optout_vectors.json`, `security-privacy-retention.spec.ts` |
| **`TC-OPT-02`** | Tier 1 Per-Sender `UNSUBSCRIBE <Name>` + Name Collision | Bob has 2 active senders named `"Alice"` (`uuid-a`, `uuid-b`); sends `UNSUBSCRIBE Alice` | Decrypted RAM-only match (zero DB name hash) detects collision and returns stateless interactive list IDs `UNSUB_PAIR:<uuid-a>`, `UNSUB_PAIR:<uuid-b>`, `UNSUB_ALL`; selecting `UNSUB_PAIR:<uuid-a>` cancels only Alice A's schedules. | `security_privacy_and_optout_vectors.json`, `security-privacy-retention.spec.ts` |
| **`TC-OPT-03`** | Non-Opt-Out Keywords Exclusion (`BR-04`) | Bob or Alice sends `"Cancel"`, `"End"`, `"Quit"`, `"stop by later"`, `"don't stop"` | **MUST NOT** trigger global opt-out (`0` rows written to `recipient_global_opt_outs`). Only exact bare `STOP` (case-insensitive, trimmed) triggers Tier 2 global opt-out. | `security-privacy-retention.spec.ts` |
| **`TC-OPT-04`** | Re-Opt-In Resilience (`START` / `YES`) | Previously opted-out Bob sends `START` | Removes global opt-out / sets `recipient_consents.status = 'OPTED_IN'` with `meta_message_id` cryptographic proof and `opt_in_expires_at = NOW() + 2 years`; previously cancelled schedules remain `CANCELLED`. | `security_privacy_and_optout_vectors.json` |
| **`TC-ABUSE-01`** | Atomic Anti-Abuse Quotas & Spam Fingerprint | Sender attempts 6th active schedule in 24h (`5/24h`), 21st in `monthly_quota_period` (`20/mo`), or identical `content_sha256` spam blast | Rejected atomically at creation; cancelled schedules do not leak quota accounting; spam fingerprint rate-limits duplicate broadcasts. | `security_privacy_and_optout_vectors.json`, `security-privacy-retention.spec.ts` |

### 1.5 Meta Cloud API `v22.0`, 5 Utility Templates & Circuit Breaker (`EPIC-07`)

| Test ID | Scenario | Input / Precondition | Expected Outcome & Assertion | Dataset / Suite |
| :--- | :--- | :--- | :--- | :--- |
| **`TC-META-01`** | Webhook `GET` Handshake & `POST` HMAC Verification | `GET` valid/invalid `hub.verify_token`; `POST` valid signature, 1-byte mutated body, wrong-length hex header, timestamp `> 300s` old | `GET` returns `200` challenge / `403` mismatch; `POST` enforces `timingSafeEqual` with length pre-check (`401` on tamper/bad length), rejects stale `> 300s` (`400`), enqueues to `inbound_webhook_events` and ACKs `200` in `< 20 ms`. | `mockapi-v4-4-contract.spec.ts` |
| **`TC-META-02`** | All 5 `en_US` `UTILITY` Templates & URL Param Rule (`M-01`) | Validate outbound payloads for `hybrid_notify_alice_v1` (3 params), `hybrid_dispatch_card_v1` (2 params + `https://wa.me/{{1}}`), `hybrid_escalation_v1` (2 params + clock time + `https://wa.me/{{1}}`), `scheduled_relay_v1` (3 params: masked phone, body, first name), `scheduled_cancelled_v1` (2 params: recipient, scheduled time) | 100% conform to `docs/contracts/mock_reconciliation_v4_4.md` (`en_US`, single trailing URL suffix, zero multi-param URLs). | `mockapi_v4_4_canonical_payloads.json`, `mockapi-v4-4-contract.spec.ts` |
| **`TC-META-03`** | Dual WABA Quality Monitor & Scoped Circuit Breaker | `phone_number_quality_update` (`GREEN -> YELLOW -> RED`) or `GET /v22.0/{id}?fields=quality_rating` | Sets `scheduler_waba_quality_state` (`0/1/2`); on `YELLOW`/`RED`, trips scoped breaker halting Bot Relay (`Personal-Only` continues via `wa.me`), fires `WABACircuitBreakerTripped`. | `mockapi_v4_4_canonical_payloads.json`, `scheduler_alerts.test.yml` |
| **`TC-META-04`** | Meta Graph API Error Taxonomy (`130429`, `131056`, `131047`, `131051`, `131026`, `131031`) | MockAPI returns each canonical Graph API error code | `130429`/`131056` backoff & `next_retry_at`; `131051`/`131056` increment `scheduler_meta_errors_total{code}`; unrecoverable codes transition cleanly to `FAILED` with `fbtrace_id` logged. | `mockapi_v4_4_canonical_payloads.json`, `mockapi-v4-4-contract.spec.ts` |

### 1.6 Zero-Trust Cryptography, Log Redaction & 4-Tier Retention (`EPIC-13`, `EPIC-14`)

| Test ID | Scenario | Input / Precondition | Expected Outcome & Assertion | Dataset / Suite |
| :--- | :--- | :--- | :--- | :--- |
| **`TC-SEC-01`** | Versioned `BYTEA` AES-256-GCM Envelope & `zeroizeBuffer()` | Encrypt/decrypt message with single-use 256-bit DEK and binary frame `[1B key_version | 12B IV | 16B authTag | N ciphertext]` | Round-trip succeeds; tampered 1-byte ciphertext or authTag throws; `finally`-block `zeroizeBuffer()` overwrites DEK & plaintext buffers with `0x00`. | `security-privacy-retention.spec.ts` |
| **`TC-SEC-02`** | Full 64-Hex `HMAC-SHA256` Phone Blind Index | Hash E.164 phone numbers with `PHONE_PEPPER` | Deterministic 64-lowercase-hex digest (never truncated `[0..31]`); identical E.164 produces identical hash; different pepper produces distinct hash. | `security-privacy-retention.spec.ts` |
| **`TC-SEC-03`** | 4-Tier Data Retention & Crypto-Shredding (`Erratum A.2 #1, #2`) | Terminal job `> 24h` (Tier 1), metadata `> 90d` (Tier 2 Option A), logs `> 30d` (Tier 3), consent `2y` (Tier 4) | Tier 1 sets `dek_encrypted = E'\\x00'::bytea`, `message_content_encrypted = E'\\x00'::bytea`, **and** `wa_me_link = ''` (mathematical unrecoverability); `inbound_webhook_events` purged `<= 24h`, `conversation_states` `<= 15m`. | `security-privacy-retention.spec.ts` |
| **`TC-SEC-04`** | Pino Nested Wildcard Redaction & E.164 Scrubber | Log nested objects containing `message_body`, `raw_text`, `wa_me_link`, `sender_name`, `recipient_name`, `dek`, `plaintext`, `user.phone`, `contact.waId`, and inline `+919876543210` | `0` plaintext PII, tokens, DEKs, `wa.me` URLs, or E.164 numbers appear in serialized log output (`+[REDACTED_PHONE]`). | `security-privacy-retention.spec.ts` |

### 1.7 Load, Soak & Observability Certification (`EPIC-06`)

| Test ID | Scenario | Load Profile | Pass Criteria | Script / Fixture |
| :--- | :--- | :--- | :--- | :--- |
| **`TC-LOAD-01`** | 3x Receipt Storm + Burst Webhook Ingestion | 500 concurrent scheduled jobs + 1,500 status receipts (`sent`/`delivered`/`read`) signed with HMAC-SHA256 | Webhook ACK `p95 < 20 ms`, `p99 <= 50 ms`, `0%` HTTP 5xx, `0` pool exhaustion. | `tests/load-k6/webhook-ack-and-receipt-storm.js` |
| **`TC-LOAD-02`** | `T0` Dispatch & `< 5s` Opt-Out Soak | Sustained hybrid scheduling + concurrent `STOP`/`UNSUBSCRIBE` cascades with `X-Test-Run-Id` isolation | `T0` drift `p95 <= 1,000 ms`; Opt-Out `p99 <= 5,000 ms`; `0.000%` double-sends; `0` cross-run state pollution. | `tests/load-k6/optout-and-t0-slo-soak.js` |
| **`TC-OBS-01`** | Prometheus Alert Rules Verification | Evaluate all 4 Alertmanager rules against synthetic time-series | `promtool test rules` passes 100% for firing and non-firing scenarios across all 4 rules. | `tests/observability/scheduler_alerts.test.yml` |

---

## Approach 2 — Phase 2: Wall-Clock Recurrence & Slash Grammar (`M5` / `EPIC-05`, `EPIC-03-P2`)

*Gated behind `M4` GA + `S9` 14-day Hypercare + signed `M5` Recurrence Retention & Meta Privacy ADR.*

| Test ID | Scenario | Coverage Scope | Expected Outcome | Dataset / Suite |
| :--- | :--- | :--- | :--- | :--- |
| **`TC-TMP-01..10`** | DST Spring-Forward Gaps (10 cases) | `America/New_York`, `Europe/London`, `Europe/Berlin`, `Australia/Sydney`, `Pacific/Auckland` (`02:30` / `01:30` nonexistent local times) | Shifts cleanly forward to post-gap wall time without skipping day or throwing; restores nominal wall time next day (`0.0` min drift). | `temporal_dst_39_cases.json`, `temporal-dst-39-cases.spec.ts` |
| **`TC-TMP-11..18`** | DST Fall-Back Ambiguity (8 cases) | Repeated `01:30` / `02:30` local times on autumn fold | Fires **once** on first offset occurrence; advances 24h wall-clock without double-firing. | `temporal_dst_39_cases.json`, `temporal-dst-39-cases.spec.ts` |
| **`TC-TMP-19..28`** | Month-End Anchor & Leap-Year Preservation (10 cases) | Anchor days `29`, `30`, `31` across 2026 (common) and 2028 (leap year) | `Jan 31 -> Feb 28/29 -> Mar 31 -> Apr 30 -> May 31`; preserves original `anchor_day_of_month`. | `temporal_dst_39_cases.json`, `temporal-dst-39-cases.spec.ts` |
| **`TC-TMP-29..34`** | Timezone Travel & Relative vs Wall-Clock Invariance (6 cases) | Travel `UTC -> Asia/Kolkata`, `America/New_York -> Asia/Tokyo`, `Asia/Kolkata` half-hour offset (`+05:30`), `Asia/Kathmandu` (`+05:45`) | Relative countdowns (`in 2 hours`) stay anchored to `created_at + 2h UTC`; recurring wall-clock schedules adapt to new `users.timezone`. | `temporal_dst_39_cases.json`, `temporal-dst-39-cases.spec.ts` |
| **`TC-TMP-35..39`** | Downtime Reboot Fast-Forward & Per-Occurrence Reset (5 cases) | 4h, 26h, 7d downtime outages + per-occurrence `idempotency_key = ${series_id}:${seq}`, `meta_message_id = NULL`, `expires_at = next_scheduled_at + 90d` | Marks missed occurrences `MISFIRED` (zero spam burst), advances single active row to next future occurrence cleanly. | `temporal_dst_39_cases.json`, `temporal-dst-39-cases.spec.ts` |
| **`TC-CLI-P2-01..04`** | Power-User Slash Grammar (`FR-CLI-03..06`) | `/list [pending|sent|all] [page]`, `/schedule --repeat`, `/edit`, `/cancel`, `/timezone <IANA>` | Direct PG FSM updates + `scheduled_message_events` audit rows; invalid IANA zones rejected cleanly. | `nlu_golden_dataset.json` (Phase-2 slice) |

---

## Approach 3 — Phase 2: Omnichannel Hexagonal SDK, Adapters & SaaS Control Plane (`M6`–`M7` / `EPIC-08..11`)

| Test ID | Scenario | Scope | Expected Outcome |
| :--- | :--- | :--- | :--- |
| **`TC-OMNI-01`** | Hexagonal Contract Suite (`@scheduler/adapter-test-kit`) | `whatsapp-cloud-api`, `viber`, `discord`, `line`, `signal`, `imessage` | Every adapter passes `runAdapterContractSuite()` with zero transport coupling inside core engine. |
| **`TC-OMNI-02`** | Viber REST Bot & Discord Gateway v10 (`EPIC-09`) | Viber webhook signature + Discord `deferReply` (`< 3s` interaction ACK) | Passes contract suite and rate-limit tests with isolated credentials in `user_platform_sessions`. |
| **`TC-OMNI-03`** | Signal QR Pairing One-Way Contract (`EPIC-10` / `EPIC-11`) | Web portal QR shell (`S14`) -> `signal-cli` JSON-RPC backend (`S15`) -> live E2E (`S16`) | End-to-end session pairing, health probe, and clean session revocation. |
| **`TC-OMNI-04`** | Web Control Plane, Bulk CSV & Stripe SaaS (`EPIC-11`) | Bulk CSV upload quota enforcement (`monthly_quota_limit`), SSE/WS live status stream, Stripe webhook idempotency (`Free`/`Pro`/`Business`) | Rejects over-quota CSV rows atomically; Stripe duplicate webhook events are idempotent; RBAC isolates tenant records. |

---

## Approach 4 — Negative Security & V1.2 Retirement Guardrails (`EPIC-12` / Appendix A.1)

| Test ID | Guardrail | Enforcement Mechanism |
| :--- | :--- | :--- |
| **`TC-NEG-01`** | Zero Retired V1.2 Packages & Workspaces | `scripts/check-v12-guardrails.mjs` fails CI if `baileys`, `bullmq`, `pg-boss`, `redlock`, `@aws-sdk/client-s3`, `prisma`, `adapters/whatsapp-baileys`, `apps/scheduler-feeder`, or `packages/queue` reappear. |
| **`TC-NEG-02`** | Zero Multimedia / R2 Pipeline (`EPIC-12`) | `supportsMedia` is `[]`, `r2.cloudflarestorage.com` forbidden by CI, inbound media webhooks rejected. |
| **`TC-NEG-03`** | Zero Invalid SQL Casts or Name Hashes | CI regex lint blocks `'\E'\\x00'::bytea'::bytea` and `sender_name_hash`/`recipient_name_hash` columns in `.sql` files. |
| **`TC-NEG-04`** | Adversarial Prompt Injection & Oversized Payloads | NLU golden dataset verifies injection payloads (`"Ignore previous instructions..."`) cannot bypass `recipient_consents`, `<= 500` char limit, or emit unauthorized `STOP`/admin actions. |
