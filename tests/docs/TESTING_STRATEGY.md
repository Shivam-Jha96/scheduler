# SchedulerBot — Master Testing, QA & Benchmarking Strategy (`Model C v4.4 HYBRID`)

> **Version**: `4.4.0` (Supersedes `Master_Testing_QA_Benchmarking_Blueprint v2.1`)  
> **Authoritative Alignment**: `SchedulerBot Implementation Plan & Milestones v2.0` (`2026-11-24`), `BRD-FRD-WAPP-SCHED-V2.0`, `Model C v4.4 HYBRID Final Specification`, `docs/contracts/mock_reconciliation_v4_4.md`  
> **Compliance Alignment**: ISO 27001 (Security), ISO 27701 (GDPR/DPDP Privacy & Crypto-Shredding), ISO 25010 (Reliability/Performance), ISO 42001 (AI/NLU Calibration & Governance), Meta WhatsApp Business Cloud API `v22.0` Policy

---

## 1. Strategic Shift from Old Blueprint (`v2.1`) to `Model C v4.4 HYBRID`

This strategy preserves the quantitative rigor of the earlier `v2.1` QA blueprint (Macro-F1, ECE calibration, Testcontainers, `ClockProvider`, `k6` load testing) while replacing all retired V1.2/V2.1 infrastructure assumptions:

| Domain | Retired (`v2.1` Old Draft) | Authoritative (`Model C v4.4 HYBRID`) |
| :--- | :--- | :--- |
| **State & Queuing** | `pg-boss`, Redis `SETNX` locks, BullMQ, 60s DB sweeper, 4-state `PENDING->QUEUED->PROCESSING->SENT` | **Pure PostgreSQL 16+ ACID**: 10-state `scheduled_message_status` FSM, optimistic CAS (`version`, `personal_send_confirmed_at IS NULL`), 30s worker leases, bounded 10s `pg_cron >= 1.5` Lease Reaper. Zero Redis/BullMQ/`pg-boss` in Phase 1. |
| **WhatsApp Transport** | Baileys companion socket / `v20.0` media stubs / typing jitter | **100% Official Meta Cloud API `v22.0`** + `$0.00` `https://wa.me/{{1}}` P2P deep links, 5 `en_US` `UTILITY` templates, plain-text UTF-8 `<= 500` chars only (`EPIC-12` R2 media permanently retired). |
| **Delivery Topology** | Single-stage bot send | **5-Stage Hybrid Lifecycle**: `T_create` -> `T-10m` (`hybrid_notify_alice_v1`) -> `T0` (`hybrid_dispatch_card_v1`) -> `T+3m` (`hybrid_escalation_v1`, atomic `escalated_at`) -> `T+10m` (`scheduled_relay_v1` ONLY if `auto_fallback = TRUE` AND `OPTED_IN` AND NOT globally opted out). |
| **Consent & Opt-Out** | Not explicitly gated in DB | **Hard SQL Consent Gate** (`recipient_consents`) + **`<= 5,000 ms` Two-Tier Opt-Out** (`UNSUBSCRIBE <Name>` RAM-only disambiguation with stateless `UNSUB_PAIR:<uuid>` + global bare `STOP`, explicitly excluding `Cancel`/`End`/`Quit`). |
| **Cryptography & Retention** | `tenant_keys` per-tenant DEK, 7d payload TTL | **Single-use 256-bit DEK per message** + Cloud KMS KEK, versioned `BYTEA` (`[1B ver | 12B IV | 16B tag | N]`), `App_DEK` (`APP_DEK_MAP`), **64-hex `HMAC-SHA256` phone blind index**, **zero name hashes**, `zeroizeBuffer()`, **4-Tier Retention** (`<= 24h` `E'\\x00'::bytea` + `wa_me_link = ''`, `90d` Option A purge/partition drop, `30d` logs, `2y` statutory consent proof). |
| **Mocking & Isolation** | WireMock-only stubs | **Isolated local Dockerized `MockAPI_Server`** (`X-Test-Run-Id` header + `POST /mock/reset` per run) enforcing all **8 Contract Deltas (`6.1`–`6.8`)**; external Modal URL reserved strictly for manual smoke checks. |

---

## 2. Quantitative Benchmarking Guidelines & 6 Production SLOs

### 2.1 Six Production Service Level Objectives (SLOs)

| # | SLO Metric | Target Threshold | Measurement Window | Severity | Verification Harness |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SLO-1** | `T0` Primary Card Dispatch Latency | `<= 1,000 ms` (`p95 <= 1,000 ms`) | Rolling 1 Hour | **P1** | `k6` load + `scheduler_t0_dispatch_latency_seconds` |
| **SLO-2** | Instant Two-Tier Opt-Out Execution Latency | `<= 5,000 ms` end-to-end (`< 25 ms` ACID DB cascade) | Rolling 15 Minutes | **P1** | `k6` + `/mock/simulate/opt-out` + `scheduler_opt_out_processing_duration_seconds` |
| **SLO-3** | Zero Double-Send Violations | **`0.000%` (Absolute Zero)** | Continuous / Permanent | **P0** | 1,000-iteration `[✅ I Sent It]` vs `T+10m` CAS race + `N=10` worker contention + `SIGKILL` chaos |
| **SLO-4** | Platform Uptime & API Availability | `>= 99.99%` | Calendar Month | **P1** | Multi-day soak + redundant pod/tunnel failover |
| **SLO-5** | Webhook Ingestion Fast-ACK Latency | `<= 50 ms` `p99` (`< 20 ms` internal `p95` target) | Rolling 5 Minutes | **P2** | `k6` 3x receipt storm (`tests/load-k6/webhook-ack-and-receipt-storm.js`) |
| **SLO-6** | Crypto-Shredding Execution SLA | `<= 24 hours` post-terminal state (`E'\\x00'::bytea` + `wa_me_link = ''`) | Daily Cron Execution | **P2** | Automated Tier-1 retention cron & immediate `SENT_VIA_BOT` shred test |

### 2.2 AI / NLU Quantitative Quality Gates (ISO 42001)

| Metric | Target SLA | Measurement & Routing Rule |
| :--- | :--- | :--- |
| **Macro-F1 Score** | `>= 0.92` across all 4 canonical intents (`SCHEDULE_RELAY`, `CANCEL_SCHEDULE`, `OPT_OUT`, `UNKNOWN`), with per-class `F1 >= 0.90` | Evaluated against `tests/datasets/nlu_golden_dataset.json` (English + Hinglish code-mixing + adversarial edge cases). Prevents high-frequency `SCHEDULE_RELAY` from masking rare-intent regressions. |
| **Expected Calibration Error (ECE)** | `<= 0.05` (10 equal-width confidence bins) | Drives confidence routing: `>= 0.90` auto-proceed; `[0.65, 0.89]` interactive confirmation card; `< 0.65` clarification prompt. |
| **Deterministic Regex Fast-Path Latency** | `< 50 ms` (`0` LLM calls) | Bare `STOP`, `START`, `YES`, `NAME <Preferred>`, `UNSUBSCRIBE <Name>`, and interactive button callbacks bypass the NLU engine completely and survive NLU `HTTP 503` outages. |
| **Zero-Retention NLU Privacy** | `0` training logs, volatile-RAM only over TLS 1.3 | Verified via outbound request payload inspection (no raw sender credentials/secrets leaked; DPA enforced). |

### 2.3 Observability & Alert Verification Gates (`EPIC-06`)
- **11 Canonical + 2 Auxiliary `scheduler_*` Prometheus Metrics** exposed on `GET /metrics`.
- **4 Alertmanager Rules** (`tests/observability/scheduler_alerts.yml`) validated on every CI run via `promtool check rules` and `promtool test rules tests/observability/scheduler_alerts.test.yml`:
  1. `WABAQualityDegradingTrend` (**P2**)
  2. `LeaseReaperHighChurn` (**P2**: `increase(scheduler_worker_lease_reclaimed_total[1h]) > 5`)
  3. `WABACircuitBreakerTripped` (**P1**)
  4. `DoubleSendAttemptBlocked` (**P1**)

---

## 3. Tooling Trade-Off Analysis

| Testing Domain | Chosen Tooling | Rejected Alternatives | Engineering Justification |
| :--- | :--- | :--- | :--- |
| **Unit, Contract & Integration Runner** | **Vitest** + **Testcontainers (PostgreSQL 16 + `pg_cron >= 1.5`)** | Jest + SQLite / In-Memory DB Mocks | SQLite/mocks cannot validate PostgreSQL `FOR UPDATE SKIP LOCKED`, partial indexes, `CHECK (retry_count <= max_retries)`, monthly range partitions, or `pg_cron` 10s reaper SQL. Vitest runs native ESM/TypeScript at high speed. |
| **Time & Recurrence Determinism** | **Injectable `ClockProvider` (`SystemClock` vs `VirtualClock`)** | Real-time sleeps or `libfaketime` | `libfaketime` breaks TLS certificate validation, KMS signing clocks, and container healthchecks. `VirtualClock` traverses 12 months of DST/month-end transitions and 5-stage Hybrid timers (`T-10m`, `T0`, `T+3m`, `T+10m`) in `< 50 ms`. |
| **Meta v22.0, NLU & KMS Mocking** | **Isolated Local Dockerized `MockAPI_Server`** (`X-Test-Run-Id` + `/mock/reset`) | Live Meta Sandbox in PR CI | Live Meta calls incur per-template cost (`$0.015/msg`), risk WABA quality penalties, and cannot deterministically inject HTTP `429 Retry-After`, `131051`, `131056`, or `RED` quality alerts during parallel CI. |
| **Load, Soak & Chaos Testing** | **Grafana k6** (JS/TS) | Apache JMeter / Locust | Reuses HMAC-SHA256 `X-Hub-Signature-256` payload signing natively at `1,000+ req/s` with minimal CPU overhead and built-in `p95`/`p99` threshold gates. |
| **Alert & Policy Guardrails** | **`scripts/check-v12-guardrails.mjs`** + **`promtool`** + **`nmap -Pn -p-`** | Manual PR checklists | Enforces binary CI blocking against retired V1.2 packages (`baileys`, `bullmq`, `pg-boss`, `redlock`, `client-s3`, `prisma`), invalid SQL casts, low-entropy name hashes, and broken alert expressions. |

---

## 4. Multi-Environment Verification Strategy

| Environment | Infrastructure | External Endpoint / Mock | Clock Mode | Gate Objective |
| :--- | :--- | :--- | :--- | :--- |
| **1. Local Dev** | `docker/docker-compose.yml` (PG 16 + `pg_cron` + `--profile mock` `mockapi-server`) | Local `MockAPI_Server` (`http://localhost:8080`) | `SystemClock` + `VirtualClock` unit tests | Rapid inner-loop dev, contract verification, zero cloud spend. |
| **2. CI Ephemeral (PR Gate)** | GitHub Actions (`ubuntu-latest`) + Testcontainers PG 16 + isolated `mockapi-server` | Isolated `MockAPI_Server` with per-run `X-Test-Run-Id` | Deterministic `VirtualClock` | 100% Guardrails, Build, Typecheck, Unit, Contract, NLU Golden Dataset, FSM/CAS & `promtool` in `< 90s`. |
| **3. Staging / Pre-Prod** | Mirror of Prod (AWS ECS/RDS or Lean VPS + `cloudflared` + Tailscale FIDO2) | Dedicated QA WABA Number + real test SIMs + Modal smoke target | Real UTC + controlled QA test schedules | Verify real Meta TLS handshakes, 5 approved `en_US` `UTILITY` templates, KMS wrap/unwrap, `nmap -Pn -p-` (`0` public ports), Meta App Review screencasts. |
| **4. Production (Canary -> GA)** | Hardened Prod (`5%` Canary `>= 48h` -> `100%` GA -> `S9` 14d Hypercare) | Verified Production WABA (`v22.0`) | NTP-synced UTC | `0` P0/P1 alerts, fallback `<= 25%`, `24h` live shred audit (`E'\\x00'::bytea` + `wa_me_link = ''`), continuous synthetic health checks. |

---

## 5. Program Milestone Test Gates (`M0`–`M7`)

| Gate | Sprint | Mandatory Test & Verification Exit Criteria |
| :--- | :--- | :--- |
| **`M0`** | `S0` | `lint:v12-guard` green; `clean`/`build`/`typecheck` green; Vitest `m0-hygiene` + all v4.4 contract/dataset suites green; 7 Errata & 8 MockAPI deltas frozen. |
| **`M1`** | `S1`–`S2` | `001_v4_4_core_schema.sql` & `002_pg_cron_reaper.sql` pass `EXPLAIN ANALYZE` (`< 0.1 ms` 64-hex blind index on 100k synthetic rows); versioned `BYTEA` KMS round-trip + `zeroizeBuffer()` + `APP_DEK_MAP` rotation; Pino nested wildcard + E.164 redaction 100%; 4-tier retention (`E'\\x00'::bytea` + `wa_me_link = ''`); external `nmap -Pn -p-` = `0` open ports (`infra/verification/verify-zero-ports.sh --dry-run`); Meta Graph peering `< 15 ms` & Anycast `< 140 ms` (`infra/verification/probe-latency.sh --dry-run`); sub-minute 10s cron & advisory lock fallback (`infra/verification/test-pg-cron-10s.sql`); `lint:v12-guard` infra scanner (`0` S3/R2 buckets, `0` public `22`/`5432` rules); 100% pass on `tests/suites/m1-iac-and-finops.spec.ts` (22 tests). |
| **`M2`** | `S3`–`S4` | `@fastify/raw-body` / `fastify-raw-body` HMAC `timingSafeEqual` + 300s replay guard + `< 20 ms` ACK; Step 0 `wa_id` bootstrap + `NAME`; 5 `en_US` `UTILITY` templates approved; `YELLOW`/`RED` circuit breaker; Hard Consent Gate + `< 5s` Two-Tier Opt-Out (`STOP`, `UNSUBSCRIBE <Name>`, `Cancel`/`End`/`Quit` excluded); atomic `5/24h`, `20/mo`, `content_sha256` quotas. |
| **`M3`** | `S5`–`S6` | Volatile-RAM NLU Macro-F1 `>= 0.92`, ECE `<= 0.05`, `< 50 ms` regex escape hatch; `<= 500` char plain-text gate; all 8 inbound callbacks + 2 URL buttons (`https://wa.me/{{1}}`); full 5-stage Hybrid lifecycle; `N=10` CAS race (`<= 1` lease); `T+3m` `escalated_at` single-send; `SIGKILL` `< 40s` lease recovery; `429 Retry-After` `next_retry_at` release; immediate `SENT_VIA_BOT` shred. |
| **`M4`** | `S7`–`S8` | 1,000-iteration `[✅ I Sent It]` vs `T+10m` race (`0.000%` double-send); `k6` SLO suite green; `promtool test rules` 100%; 5 runbooks (`SOP-01`..`05`) tabletop drill; `5%` Canary `>= 48h` (`0` P0/P1, fallback `<= 25%`) -> `100%` GA. |
| **`S9`** | `S9` | 14-day Hypercare (`0` P0/P1, live `24h` shred audit green) + signed **`M5` Recurrence Retention & Meta Privacy ADR**. |
| **`M5`** | `S10`–`S11` | **39-case Luxon DST / month-end / leap-year / reboot-misfire suite** (`0.0` min drift); per-occurrence reset (`idempotency_key = ${series_id}:${seq}`); Phase-2 slash commands (`/list`, `/schedule --repeat`, `/edit`, `/cancel`, `/timezone`). |
| **`M6`** | `S12`–`S13` | `IMessagingTransportAdapter` + `@scheduler/adapter-test-kit` 100% pass across `whatsapp-cloud-api`, `adapters/viber`, `adapters/discord`. |
| **`M7`** | `S14`–`S16` | `adapters/line`, `adapters/signal` (QR JSON-RPC), `adapters/imessage`; Next.js Web Dashboard, bulk CSV quota checks, SSE/WS live updates, Stripe SaaS webhooks. |
