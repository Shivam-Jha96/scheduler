# SchedulerBot — Model C v4.4 HYBRID Message Scheduler Platform

> **Architecture**: Model C v4.4 HYBRID (Pure PostgreSQL 16+ ACID State Machine + Meta WhatsApp Cloud API `v22.0` + `wa.me` P2P Deep Links)  
> **Monorepo**: Turborepo + npm workspaces + TypeScript `5.7.3`  
> **Status**: `M0` (Sprint 0) Hygiene, V1.2 Purge, Contract Reconciliation & CI Baseline Active

---

## Executive Summary

**SchedulerBot (Model C v4.4 HYBRID)** is a 100% official **Meta WhatsApp Business Cloud API `v22.0`** scheduling platform that combines zero-cost personal peer-to-peer delivery (`$0.00` via pre-generated `https://wa.me` deep links) with a pre-authorized, database-enforced consent-gated Bot Relay fallback (`scheduled_relay_v1`).

### Core Architectural Guarantees (Phase 1 MVP)
- **Zero Double-Sends (`0.000%` P0 SLO)**: Enforced via PostgreSQL 16+ atomic Compare-And-Swap (`personal_send_confirmed_at IS NULL`, optimistic `version`), 30-second worker leases, bounded 10-second `pg_cron` Lease Reaper, and Meta `biz_opaque_callback_data` (`idempotency_key`).
- **Pure PostgreSQL 16+ Runtime**: Zero Redis, zero BullMQ, zero `pg-boss`, and zero Redlock in Phase 1. All durable state, partial-index scheduling, and stateless multi-pod webhook/conversation buffers live in PostgreSQL 16+ (`pg`, `pg_cron >= 1.5`, `pgcrypto`, `uuid-ossp`).
- **Zero-Trust Privacy & Zero Name Hashes**: Single-use 256-bit DEKs wrapped by Cloud KMS KEK, versioned native `BYTEA` AES-256-GCM ciphertexts, full 64-hex `HMAC-SHA256(PHONE_PEPPER, E164)` phone blind indexes, zero low-entropy name hashes, Pino nested wildcard log redaction, and 4-Tier Data Retention (`<= 24h` payload crypto-shredding via `E'\\x00'::bytea` + `wa_me_link = ''`, `90d` metadata, `30d` logs, `2y` consent proof).
- **Hard Recipient Consent & `< 5s` Two-Tier Opt-Out**: Plain-text UTF-8 `<= 500` characters only (multimedia permanently retired in v4.4), SQL-gated `recipient_consents` and `recipient_global_opt_outs`, per-sender `UNSUBSCRIBE <Name>`, and mandatory bare `STOP`.

---

## Monorepo Layout

```text
scheduler/
├── package.json                       # Root Turborepo & npm workspaces scripts
├── turbo.json                         # Task pipeline (build, typecheck, test, clean)
├── .env.example                       # Model C v4.4 HYBRID environment template
├── .github/workflows/ci.yml           # CI: v1.2 guardrails, build, typecheck, tests
├── scripts/
│   └── check-v12-guardrails.mjs       # EP12-G2 / M0-T4 forbidden v1.2 dependency & SQL guard
├── tests/
│   └── m0-hygiene.test.ts             # Vitest baseline verification suite
│
├── apps/
│   ├── api-gateway/                   # Fastify v5 webhook ingress & REST API
│   ├── delivery-worker/               # PostgreSQL CAS lease dispatch worker pool
│   └── web-dashboard/                 # [Phase 2 / M7 / EPIC-11] Quarantined dashboard shell
│
├── adapters/
│   ├── whatsapp-cloud-api/            # [Phase 1] Official Meta Cloud API v22.0 adapter
│   ├── viber/                         # [Phase 2 / M6 / EPIC-09] Quarantined
│   ├── discord/                       # [Phase 2 / M6 / EPIC-09] Quarantined
│   ├── slack/                         # [Phase 2+ Backlog] Quarantined
│   ├── telegram/                      # [Phase 2+ Backlog] Quarantined
│   └── webhook/                       # [Phase 2+ Backlog] Quarantined
│
├── packages/
│   ├── types/                         # Canonical 10-state FSM & plain-text contracts
│   ├── adapter-sdk/                   # IChannelAdapter port & capabilities
│   ├── adapter-registry/              # Dynamic IoC adapter registry
│   ├── adapter-test-kit/              # Adapter contract test suite
│   ├── database/                      # PostgreSQL 16+ pg pool client & migrations
│   ├── crypto/                        # Cloud KMS envelope encryption & blind indexing
│   ├── temporal/                      # Timezone inference & Phase-2 recurrence math
│   ├── logger/                        # Pino structured logger & PII redactor
│   └── config/                        # Zod-validated v4.4 environment config
│
├── tools/
│   ├── create-adapter/                # Adapter scaffolding CLI (v4.4 plain-text defaults)
│   └── typescript-config/             # Shared tsconfig bases
│
├── docker/
│   ├── Dockerfile.postgres            # PostgreSQL 16 with pg_cron >= 1.5
│   ├── postgres/init/00-extensions.sql
│   └── docker-compose.yml             # Local PG 16 (+ optional --profile mock MockAPI_Server)
│
└── docs/
    ├── contracts/
    │   └── mock_reconciliation_v4_4.md # Frozen M0-T3 ADR (7 Errata + 8 MockAPI deltas)
    └── README.md                      # Historical & Master Documentation Portal
```

> **Retired V1.2 Artifacts**: `adapters/whatsapp-baileys`, `apps/scheduler-feeder`, `packages/queue`, Prisma (`@prisma/client`), Redis/BullMQ, `pg-boss`, and Cloudflare R2 media pipelines have been permanently removed per `BRD-FRD-WAPP-SCHED-V2.0` Appendix A.1.

---

## Quickstart & Verification

### 1. Prerequisites
- **Node.js**: `>= 20.0.0` (Node 22 LTS recommended)
- **npm**: `>= 10.0.0`
- **Docker**: Optional, for local PostgreSQL 16 + `pg_cron` (and optional `mockapi-server`)

### 2. Install, Verify & Build
```bash
cp .env.example .env
npm install
npm run lint:v12-guard
npm run build
npm run typecheck
npm test
```

### 3. Local Infrastructure (PostgreSQL 16 + `pg_cron`)
```bash
# Start PostgreSQL 16 with pg_cron, pgcrypto, uuid-ossp
docker compose -f docker/docker-compose.yml up -d

# Start PostgreSQL + isolated local MockAPI_Server (M0-T3)
docker compose -f docker/docker-compose.yml --profile mock up -d
```

---

## Reference Documentation
- [PROJECT.md](./PROJECT.md) — Program Milestones (`M0`–`M7`) and Epic-to-Issue mapping (`#1`–`#16`)
- [docs/contracts/mock_reconciliation_v4_4.md](./docs/contracts/mock_reconciliation_v4_4.md) — Frozen M0-T3 Errata & MockAPI Reconciliation ADR
- [docs/README.md](./docs/README.md) — Historical Documentation Portal
