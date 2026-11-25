# Project: SchedulerBot — Model C v4.4 HYBRID

> **Authoritative Baseline**: `SchedulerBot Implementation Plan & Milestones v2.0` (`2026-11-24`), `BRD-FRD-WAPP-SCHED-V2.0`, `Model C v4.4 HYBRID Final Specification`

## Architecture (Phase 1 MVP)
- **Transport**: 100% official **Meta WhatsApp Business Cloud API `v22.0`** + zero-cost `https://wa.me` P2P deep links (Models C v4.4 HYBRID). Plain-text UTF-8 `<= 500` characters only.
- **State Machine & Queuing**: Pure **PostgreSQL 16+** (`pg` pool, 10-state `scheduled_message_status` FSM, optimistic CAS `version`, 30s worker leases, bounded 10s `pg_cron >= 1.5` Lease Reaper). Zero Redis, zero BullMQ, zero `pg-boss`, zero Prisma, zero Baileys in Phase 1.
- **Security & Privacy**: Single-use 256-bit DEKs wrapped via Cloud KMS KEK, versioned `BYTEA` AES-256-GCM ciphertexts, full 64-hex `HMAC-SHA256(PHONE_PEPPER, E164)` blind indexing, zero low-entropy name hashes, Pino nested wildcard PII redaction, and 4-Tier Retention (`<= 24h` shred `E'\\x00'::bytea` + `wa_me_link = ''`, `90d` metadata, `30d` logs, `2y` statutory consent proof).
- **Compliance**: Hard SQL-enforced `recipient_consents` gate, `< 5s` Two-Tier Opt-Out (`STOP` + `UNSUBSCRIBE <Name>`), 5 `en_US` `UTILITY` templates, WABA quality circuit breaker.

## Program Milestones (`M0`–`M7`)

| Milestone | Sprint Window | Phase | Scope & Mapped GitHub Issues |
| :--- | :--- | :--- | :--- |
| **`M0`** | `S0` (W1–W2) | Phase 1 Prep | V1.2 purge (`M0-T2`), MockAPI reconciliation ADR & isolation (`M0-T3`, `#16`), CI/CD (`M0-T4`), Docs sync (`M0-T5`), GitHub governance (`M0-T1`), Meta BM kickoff (`M0-T6`) |
| **`M1`** | `S1`–`S2` (W3–W6) | Phase 1 MVP | `EPIC-14` (`#14` Zero-Trust Edge), `EPIC-13` (`#13` KMS/Crypto/Pino/4-Tier), `[EPIC-04-DDL]` (PG 16+ 5+2 tables, 10-state FSM, `pg_cron`, linked to `#3`) |
| **`M2`** | `S3`–`S4` (W7–W10) | Phase 1 MVP | `EPIC-01` (`#1` Identity Bootstrap), `EPIC-07` (`#6` Meta Cloud API `v22.0` + 5 Utility Templates + Breaker), `EPIC-15` (`#15` Consent Gate, `<5s` Opt-Out, Quotas) |
| **`M3`** | `S5`–`S6` (W11–W14) | Phase 1 MVP | `EPIC-02` (`#12` NLU + Plain-Text Gate), `EPIC-03` (`#2` Phase-1 Keywords/Buttons), `EPIC-04` (`#3` 5-Stage Hybrid CAS Engine) |
| **`M4`** | `S7`–`S8` (W15–W18) | Phase 1 GA | `EPIC-06` (`#5` Zero-Double-Send SLOs, 13 Metrics, 4 Alerts, 5 Runbooks, `k6`/Chaos, 5% Canary -> GA) |
| **`S9`** | `S9` (W19–W20) | Hypercare | 14-day production stability buffer + `M5` Recurrence Retention & Meta Privacy ADR sign-off |
| **`M5`** | `S10`–`S11` (W21–W24) | Phase 2 | `EPIC-05` (`#4` Wall-Clock Recurrence), `[EPIC-03-P2]` (Slash Grammar, linked to `#2`) |
| **`M6`** | `S12`–`S13` (W25–W28) | Phase 2 | `EPIC-08` (`#7` Hexagonal SDK), `EPIC-09` (`#8` Viber & Discord Adapters) |
| **`M7`** | `S14`–`S16` (W29–W34) | Phase 2 GA | `EPIC-10` (`#9` Signal/LINE/iMessage), `EPIC-11` (`#10` Next.js Web Dashboard & Stripe SaaS) |

> **Retired Epic**: `EPIC-12` (`#11` — Multi-Modal Media / Cloudflare R2) is permanently closed (`NOT_PLANNED`) and blocked by CI (`scripts/check-v12-guardrails.mjs`).

## Key Contracts & Verification
- [docs/contracts/mock_reconciliation_v4_4.md](./docs/contracts/mock_reconciliation_v4_4.md) — Frozen 7 Appendix A.2 Errata & 8 MockAPI sub-deltas
- `.github/workflows/ci.yml` — Automated v1.2 guardrail, build, typecheck, and Vitest verification
