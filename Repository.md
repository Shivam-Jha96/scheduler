# `repo.md` — SchedulerBot (`Model C v4.4 HYBRID`)

> **Repository**: `scheduler-monorepo` (Turborepo + npm workspaces + TypeScript `5.7.3` + Node.js `>= 20.0.0`, 22 LTS recommended)  
> **Authoritative Architecture**: **Model C v4.4 HYBRID** (`SchedulerBot Implementation Plan & Milestones v2.0`, `BRD-FRD-WAPP-SCHED-V2.0`, [docs/contracts/mock_reconciliation_v4_4.md](./docs/contracts/mock_reconciliation_v4_4.md))  
> **Current Program Phase**: `M0` Complete | `M1` IaC (`EPIC-14`, Stories `#19`–`#22`, Subtasks `#23`–`#31`) Implemented & Verified

---

## 1. What This Repository Is

**SchedulerBot (Model C v4.4 HYBRID)** is a **Meta WhatsApp Business Cloud API `v22.0`** message scheduling platform (with a Phase 2 omnichannel roadmap) that combines:
1. **Zero-Cost Personal P2P Delivery (`$0.00`)**: Pre-generated `https://wa.me/{E164}?text={Encoded}` deep links surfaced in interactive WhatsApp dispatch cards so the sender taps to send from their personal WhatsApp.
2. **Pre-Authorized Bot Relay Fallback (`scheduled_relay_v1`)**: Database-enforced, recipient-consent-gated official Meta Cloud API `v22.0` relay when the sender requests Bot Relay or does not confirm personal send within the escalation window.

---

## 2. Core Architectural Invariants (Phase 1 MVP)

All Phase 1 code, SQL, and tests **must** preserve these invariants:

- **Pure PostgreSQL 16+ Runtime (Zero Redis / Zero External Brokers)**:
  - Uses `pg` connection pooling, `pg_cron >= 1.5`, `pgcrypto`, and `uuid-ossp`.
  - **Zero** Redis, BullMQ, `pg-boss`, Redlock, or Prisma in Phase 1.
- **Zero Double-Sends (`0.000%` P0 SLO)**:
  - Enforced via PostgreSQL 16+ atomic Compare-And-Swap (`personal_send_confirmed_at IS NULL`, optimistic `version`), 30-second worker leases, bounded 10-second `pg_cron` Lease Reaper (Erratum A.2 #7), and Meta `biz_opaque_callback_data` (`idempotency_key`).
- **10-State Finite State Machine (`ScheduledMessageStatus`, Erratum A.2 #3)**:
  - Canonical states: `PENDING`, `NOTIFIED`, `FAST_TRACK`, `AWAITING_CONFIRMATION`, `DISPATCHING`, `SENT_VIA_PERSONAL`, `SENT_VIA_BOT`, `FAILED`, `CANCELLED`, `EXPIRED`.
  - Dispatch modes: `HYBRID | PERSONAL_ONLY | BOT_ONLY`.
- **Plain-Text Only (`<= 500` UTF-8 Characters)**:
  - `MAX_PLAINTEXT_MESSAGE_LENGTH = 500` (`BR-02`). Multimedia pipelines (Cloudflare R2, `@aws-sdk/client-s3`, `EPIC-12`) are **permanently retired**.
- **Zero-Trust Privacy & 4-Tier Retention (Errata A.2 #1, #2, #4)**:
  - Single-use 256-bit DEKs wrapped by Cloud KMS KEK (`KMS_KEY_ID=alias/schedulerbot-dek`), versioned `BYTEA` AES-256-GCM ciphertexts (`IV` 12 bytes + authTag).
  - Full 64-hex `HMAC-SHA256(PHONE_PEPPER, E164)` blind indexes for phone lookups. **Zero** low-entropy name hash columns (`sender_name_hash`, `recipient_name_hash` are banned by CI).
  - Pino/structured logger PII redaction on sensitive keys (`password`, `secret`, `token`, `text`, `payload`, `auth`, `credentials`).
  - **4-Tier Retention**: Tier 1 `<= 24h` payload crypto-shred (`E'\\x00'::bytea` + `wa_me_link = ''`), Tier 2 `90d` metadata purge, Tier 3 `30d` logs, Tier 4 `2y` statutory consent proof.
- **Hard Recipient Consent & `< 5s` Two-Tier Opt-Out**:
  - SQL-gated `recipient_consents` and `recipient_global_opt_outs`.
  - Supports per-sender `UNSUBSCRIBE <Name>` and mandatory bare `STOP`, tracked via `scheduler_opt_out_total{tier="GLOBAL|PER_SENDER"}` (Erratum A.2 #5).
- **Official Transport Only**:
  - Phase 1 registers **only** `whatsapp-cloud-api` (`@scheduler/adapter-whatsapp-cloud-api`, 80 mps / 4,800 rpm ceiling, `recommendedJitterMs: 0`).
  - `@whiskeysockets/baileys` and anti-ban typing/jitter heuristics are permanently retired.

---

## 3. Monorepo Layout

```text
scheduler/
├── package.json                         # Root Turborepo & npm workspaces scripts
├── turbo.json                           # Pipeline: build (^build), typecheck (^build), test (build), dev, clean
├── tsconfig.base.json                   # Strict ES2022 / NodeNext composite TypeScript base
├── .env.example                         # Model C v4.4 HYBRID environment template
├── .github/workflows/ci.yml             # CI on master: v1.2 guardrails -> build -> typecheck -> test
│
├── infra/                               # Milestone M1 Infrastructure-as-Code (EPIC-14)
│   ├── README.md                        # IaC Architecture & Verification Guide
│   ├── lean-vps/                        # Lean VPS Zero-Trust Ingress Profile ($11.95–$27.80/mo)
│   │   ├── cloudflared/                 # Outbound QUIC tunnel (0 public WAN ports)
│   │   ├── tailscale/                   # Bastion-free admin via WireGuard 100.x.y.z + FIDO2
│   │   ├── hardening/                   # UFW default-deny & Linux sysctl hardening
│   │   ├── postgres/                    # PostgreSQL 16 + pg_cron >= 1.5 + local pgBackRest
│   │   └── logging/                     # Promtail + Loki (Tier-3 30-day / 720h retention)
│   ├── terraform-aws/                   # Enterprise AWS Terraform Profile ($180.00/mo)
│   │   ├── main.tf, variables.tf, outputs.tf
│   │   ├── vpc.tf, security_groups.tf   # Multi-AZ VPC with isolated DB subnets
│   │   ├── kms.tf                       # Envelope CMK (alias/schedulerbot-dek) + key rotation
│   │   ├── rds_aurora.tf                # Aurora PG 16 with pg_cron parameter group
│   │   ├── alb.tf, waf.tf               # TLS 1.3 ALB + WAFv2 rate limiting on /webhooks/whatsapp
│   │   ├── ecs.tf, ssm.tf               # Private Fargate tasks + SSM Session Manager
│   │   └── cloudwatch.tf                # Tier-3 30-day log groups
│   ├── finops/                          # Cost Modeling & Drift Governance
│   │   ├── budget-alerts.tf             # AWS Budgets ($180 base, $481.20 100k tier @ 75%/90%)
│   │   ├── prometheus-finops.rules      # >25% fallback drift alert over 24h & KMS metrics
│   │   └── cost_model_v4_4.md           # Reconciled unit-economics ledger (72.5%–79.1% savings)
│   └── verification/                    # Security & Performance Verification Scripts
│       ├── verify-zero-ports.sh         # nmap -Pn -p- audit asserting 0 open public WAN ports
│       ├── probe-latency.sh             # Anycast (<140ms) & Meta Graph peering (<15ms)
│       └── test-pg-cron-10s.sql         # PostgreSQL 16 sub-minute 10s cron & advisory lock fallback
│
├── tests/
│   ├── suites/                          # Executable Vitest specifications
│   │   ├── m1-iac-and-finops.spec.ts    # M1 IaC & FinOps validation suite (22 tests)
│   │   ├── fsm-and-cas-contracts.spec.ts
│   │   ├── mockapi-v4-4-contract.spec.ts
│   │   ├── nlu-calibration-and-dataset.spec.ts
│   │   ├── security-privacy-retention.spec.ts
│   │   └── temporal-dst-39-cases.spec.ts
│   ├── datasets/                        # Deterministic test vectors & golden dataset
│   ├── load-k6/                         # Grafana k6 webhook & opt-out soak scripts
│   └── observability/                   # Prometheus alert rules & promtool test fixtures
│
├── apps/
│   ├── api-gateway/                     # @scheduler/api-gateway — Fastify v5 ingress (/health, /api/webhooks/:channelId, /api/schedules)
│   ├── delivery-worker/                 # @scheduler/delivery-worker — CAS lease dispatch processor & Phase 1 adapter registry
│   └── web-dashboard/                   # @scheduler/web-dashboard — [Phase 2 / M7 / EPIC-11] Quarantined dashboard shell
│
├── adapters/
│   ├── whatsapp-cloud-api/              # [Phase 1 Active] Official Meta Cloud API v22.0 adapter
│   ├── discord/                         # [Phase 2 / M6 / EPIC-09] Quarantined
│   ├── viber/                           # [Phase 2 / M6 / EPIC-09] Quarantined
│   ├── slack/                           # [Phase 2+ Backlog] Quarantined
│   ├── telegram/                        # [Phase 2+ Backlog] Quarantined
│   └── webhook/                         # [Phase 2+ Backlog] Quarantined
│
├── packages/
│   ├── types/                           # @scheduler/types — Canonical 10-state FSM, ChannelType, job/receipt contracts
│   ├── adapter-sdk/                     # @scheduler/adapter-sdk — IChannelAdapter port & ChannelCapabilities
│   ├── adapter-registry/                # @scheduler/adapter-registry — Singleton IoC AdapterRegistry
│   ├── adapter-test-kit/                # @scheduler/adapter-test-kit — Reusable adapter contract test suite
│   ├── database/                        # @scheduler/database — PostgreSQL 16+ pg Pool wrapper (DatabaseService)
│   ├── crypto/                          # @scheduler/crypto — AES-256-GCM EnvelopeEncryption & SHA-256 idempotency keygen
│   ├── temporal/                        # @scheduler/temporal — TemporalEngine (IANA timezone & Phase-2 recurrence math)
│   ├── logger/                          # @scheduler/logger — Structured JSON Logger with PII key redaction
│   └── config/                          # @scheduler/config — Zod-validated AppConfig (envSchema, loadConfig)
│
├── tools/
│   ├── create-adapter/                  # CLI scaffolder for new @scheduler/adapter-* workspaces (v4.4 plain-text defaults)
│   └── typescript-config/               # @scheduler/typescript-config — Shared base.json & node.json tsconfigs
│
├── docker/
│   ├── Dockerfile.postgres              # postgres:16-bookworm + postgresql-16-cron
│   ├── Dockerfile.base                  # Base image definition
│   ├── postgres/init/00-extensions.sql  # Enables uuid-ossp, pgcrypto, pg_cron
│   └── docker-compose.yml               # Local PG 16 + optional `--profile mock` MockAPI_Server (:8080)
│
├── scripts/
│   ├── check-v12-guardrails.mjs         # M0-T4 / EP12-G2 CI guardrail scanner
│   └── ...                              # Doc builders (HTML/PDF) & GitHub Projects/Epics automation scripts
│
├── tests/
│   ├── m0-hygiene.test.ts               # M0 baseline guardrail unit tests
│   ├── docs/                            # TESTING_STRATEGY.md, FINAL_TEST_DESIGN.md
│   ├── datasets/                        # Canonical v4.4 JSON fixtures (MockAPI, NLU golden, 39 DST, FSM/chaos, security)
│   ├── suites/                          # Vitest specs (FSM/CAS, MockAPI v4.4, NLU, security/retention, 39 DST cases)
│   ├── load-k6/                         # k6 soak & receipt-storm scripts
│   └── observability/                   # Prometheus alert rules (scheduler_alerts.yml) & promtool test fixtures
│
└── docs/
    ├── contracts/mock_reconciliation_v4_4.md  # Frozen M0-T3 ADR (7 Errata + 8 MockAPI deltas)
    ├── README.md                              # Historical & Master Documentation Portal (note pre-v4.4 warning)
    ├── diagrams/ & diagram_cache/             # Architecture PNG diagrams
    ├── downloaded_docs/ & rendered_html/      # Reference specs & HTML renders
    └── *.md, *.html, *.pdf                    # HLD, BRD/FRD, Infrastructure, Scale-Out, and Teams REA specs
```

---

## 4. Commands & Verification

### Root Workspace Commands (`package.json`)
```bash
# 1. Install dependencies
npm install

# 2. Run M0-T4 / EP12-G2 forbidden v1.2 & SQL guardrail check
npm run lint:v12-guard

# 3. Build all Turborepo workspaces (required before Vitest imports dist/ outputs)
npm run build

# 4. Typecheck all workspaces
npm run typecheck

# 5. Run all Vitest unit/contract tests (root + workspace tests)
npm test
# Or run root Vitest suites only:
npm run test:unit

# 6. Scaffold a new channel adapter under adapters/<slug>
npm run create:adapter -- --name <channel-slug> --display "Display Name"

# 7. Clean build artifacts
npm run clean
```

### Local Docker Infrastructure
```bash
# Start PostgreSQL 16 with pg_cron, pgcrypto, uuid-ossp on localhost:5432
docker compose -f docker/docker-compose.yml up -d

# Start PostgreSQL 16 + isolated local MockAPI_Server on localhost:8080 (M0-T3)
docker compose -f docker/docker-compose.yml --profile mock up -d
```

### Optional Load & Observability Checks
```bash
# Validate Prometheus alert rules
promtool check rules tests/observability/scheduler_alerts.yml
promtool test rules tests/observability/scheduler_alerts.test.yml

# Run k6 load tests against local gateway / MockAPI_Server
k6 run -e BASE_URL=http://localhost:3000 -e META_APP_SECRET=dev-meta-app-secret tests/load-k6/webhook-ack-and-receipt-storm.js
k6 run -e MOCK_BASE_URL=http://localhost:8080 -e TEST_RUN_ID=soak-$(date +%s) tests/load-k6/optout-and-t0-slo-soak.js
```

---

## 5. CI/CD & Automated Guardrails

GitHub Actions (`.github/workflows/ci.yml`) runs on every push/PR to `master` using Node.js 22 LTS:
1. `npm ci`
2. `npm run lint:v12-guard` (`scripts/check-v12-guardrails.mjs`)
3. `npm run build`
4. `npm run typecheck`
5. `npm test`

### What `scripts/check-v12-guardrails.mjs` Enforces
Do **not** reintroduce any of the following—CI will fail immediately (`21 package.json, 50 code/SQL, & 25 infra files scanned`):
- **Banned npm dependencies**: `@whiskeysockets/baileys`, `bullmq`, `pg-boss`, `redlock`, `@aws-sdk/client-s3`, `@prisma/client`, `prisma`.
- **Banned retired directories**: `adapters/whatsapp-baileys`, `apps/scheduler-feeder`, `packages/queue`, `packages/database/prisma`.
- **Banned clean scripts**: POSIX-only `rm -rf` in `package.json` `clean` scripts (use Node `fs.rmSync` for Windows/cross-platform compatibility).
- **Banned code/SQL patterns** (outside `tests/`, `docs/`, `conversations/`):
  - `r2.cloudflarestorage.com`
  - `@whiskeysockets/baileys` or `@scheduler/adapter-whatsapp-baileys`
  - Invalid duplicated SQL cast `'\E'\\x00'::bytea'::bytea` (must be `E'\\x00'::bytea`)
  - Low-entropy name hash SQL columns `sender_name_hash` or `recipient_name_hash`
- **Milestone M1 IaC & FinOps Guardrails** (`infra/**`):
  - Zero `aws_s3_bucket` or `r2.cloudflarestorage.com` definitions in Phase 1 IaC ($0.00 media OpEx)
  - Zero Terraform security groups opening port 22 or 5432 to `0.0.0.0/0` (FR-NET-01, FR-NET-02)

---

## 6. Environment Configuration

Validated at runtime by `loadConfig()` in `packages/config/src/config.ts` (Zod schema). Key variables in `.env.example`:

| Group | Variables | Notes |
| :--- | :--- | :--- |
| **Runtime** | `NODE_ENV`, `LOG_LEVEL`, `PORT` (`3000`), `HOST` (`0.0.0.0`) | Standard Fastify/Logger settings |
| **Database** | `DATABASE_URL` | `postgresql://scheduler:scheduler_secret@localhost:5432/scheduler_db` |
| **KMS & Crypto** | `KMS_KEY_ID`, `KMS_ENDPOINT_URL`, `PHONE_PEPPER`, `APP_DEK_CIPHERTEXT`, `APP_DEK_MAP` | `PHONE_PEPPER` >= 32 chars (64-hex in prod); `KMS_ENDPOINT_URL` points to MockAPI in local/CI |
| **Meta Cloud API** | `META_GRAPH_API_BASE_URL`, `META_GRAPH_API_VERSION` (`v22.0`), `META_APP_SECRET`, `META_VERIFY_TOKEN`, `WABA_PHONE_NUMBER_ID`, `META_SYSTEM_USER_TOKEN` | Official Meta Graph API `v22.0` credentials |
| **NLU & Mock** | `NLU_ENDPOINT_URL`, `MOCK_API_BASE_URL` | Local/CI defaults to `http://localhost:8080` |

---

## 7. Key Contracts & Frozen Decisions

### `IChannelAdapter` (`packages/adapter-sdk`)
Every channel adapter implements:
- `channelId`, `displayName`, `capabilities` (`supportsMedia: []`, `maxPayloadLength: 500`, `rateLimit.recommendedJitterMs: 0` in Phase 1)
- `initialize(accountConfig)`, `shutdown(accountId)`, `checkHealth(accountId)`
- `validateRecipient(accountId, recipientId)`, `sendMessage(job)`, optional `handleWebhook(payload, headers)`

### Frozen MockAPI & Errata Contract (`docs/contracts/mock_reconciliation_v4_4.md`)
- **5 `en_US` `UTILITY` templates** (updated from `en`):
  - `hybrid_dispatch_card_v1`: 2 body params + single trailing URL button `https://wa.me/{{1}}` + `✅ I Sent It` quick reply
  - `hybrid_notify_alice_v1`: 3 body params + `✏️ Edit Message` & `❌ Cancel Schedule` quick replies
  - `hybrid_escalation_v1`: 2 body params + single trailing URL button `https://wa.me/{{1}}` + `🤖 Send via Bot Now` & `✅ Already Sent` quick replies
  - `scheduled_cancelled_v1`: 2 body params (`{{1}}` Recipient, `{{2}}` scheduled time)
  - `scheduled_relay_v1`: Consent-gated Bot Relay fallback template
- **NLU (`POST /v1/parse-schedule`)**: Request `{ raw_text, timezone }`; response intent enum `["SCHEDULE_RELAY", "CANCEL_SCHEDULE", "OPT_OUT", "UNKNOWN"]` + `validation.{is_valid, missing_fields, errors}`.
- **KMS Mock (`/kms/*`)**: Canonical fields `plaintext`, `ciphertext_blob`, `key_id` (`alias/schedulerbot-dek`).
- **Test Isolation**: Concurrent CI / `k6` runs isolate state via `X-Test-Run-Id` header and `POST /mock/reset`.

---

## 8. Program Milestones (`M0`–`M7`)

- **`M0` (S0, W1–W2) — Phase 1 Prep**: V1.2 purge, MockAPI reconciliation ADR, CI/CD guardrails, docs sync, Meta BM kickoff.
- **`M1` (S1–S2, W3–W6) — Phase 1 MVP**: `EPIC-14` Zero-Trust Edge, `EPIC-13` KMS/Crypto/Pino/4-Tier Retention, `EPIC-04-DDL` PG 16+ schema + 10-state FSM + `pg_cron`.
- **`M2` (S3–S4, W7–W10) — Phase 1 MVP**: `EPIC-01` Identity Bootstrap, `EPIC-07` Meta Cloud API `v22.0` + 5 Utility Templates + Circuit Breaker, `EPIC-15` Consent Gate, `<5s` Opt-Out & Quotas.
- **`M3` (S5–S6, W11–W14) — Phase 1 MVP**: `EPIC-02` NLU + Plain-Text Gate, `EPIC-03` Phase-1 Keywords/Buttons, `EPIC-04` 5-Stage Hybrid CAS Engine.
- **`M4` (S7–S8, W15–W18) — Phase 1 GA**: `EPIC-06` Zero-Double-Send SLOs, 13 Metrics, 4 Alerts, 5 Runbooks, `k6`/Chaos, 5% Canary -> GA.
- **`M5`–`M7` (S10–S16, W21–W34) — Phase 2**: Wall-Clock Recurrence (`EPIC-05`), Slash Grammar, Hexagonal SDK (`EPIC-08`), Viber/Discord/Signal/LINE/iMessage (`EPIC-09`, `EPIC-10`), Next.js Web Dashboard & Stripe SaaS (`EPIC-11`).
- **Retired**: `EPIC-12` (Multi-Modal Media / Cloudflare R2) is permanently `NOT_PLANNED`.
