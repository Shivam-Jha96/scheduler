# Production-Grade Test Datasets (`tests/datasets/`)

All fixtures in this directory are **100% synthetic** (using fictional E.164 test numbers and names — zero real PII) and strictly aligned to **Model C v4.4 HYBRID** (`Implementation Plan v2.0`, `BRD-FRD-WAPP-SCHED-V2.0`, and `docs/contracts/mock_reconciliation_v4_4.md`).

| File | Coverage | Consumed By |
| :--- | :--- | :--- |
| `mockapi_v4_4_canonical_payloads.json` | Reconciled payloads for all 8 MockAPI deltas (`6.1`–`6.8`), all 5 `en_US` `UTILITY` templates (`https://wa.me/{{1}}`), Meta error taxonomy (`130429`, `131051`, `131056`, `429`), KMS & simulation harness. | `tests/suites/mockapi-v4-4-contract.spec.ts`, `tests/load-k6/*` |
| `nlu_golden_dataset.json` | 80 curated NLU benchmark prompts across all 4 canonical intents (`SCHEDULE_RELAY`, `CANCEL_SCHEDULE`, `OPT_OUT`, `UNKNOWN`): English, Hinglish code-mixing, missing phone, `500`/`501` char boundaries, multimedia rejection, `Cancel`/`End`/`Quit` non-opt-out edge cases, ambiguous confidence bands, and prompt-injection tests. | `tests/suites/nlu-calibration-and-dataset.spec.ts` |
| `temporal_dst_39_cases.json` | Complete 39-case Phase-2 wall-clock recurrence dataset (`TC-TMP-01`..`39`): Spring-Forward gaps, Fall-Back ambiguity, Jan 31 -> Feb 28/29 -> Mar 31 -> Apr 30 month-end anchors, TZ travel invariance, half/quarter-hour offsets, and 4h/26h/7d reboot `MISFIRED` fast-forward. | `tests/suites/temporal-dst-39-cases.spec.ts` |
| `fsm_transitions_and_chaos_matrix.json` | 10-state `ScheduledMessageStatus` valid & illegal transitions, `N=10` CAS contention, `T+3m` `escalated_at` single-send, `T+10m` fallback matrix, `SIGKILL` bounded Lease Reaper progression (Erratum A.2 #7), and `429 Retry-After` lease release. | `tests/suites/fsm-and-cas-contracts.spec.ts` |
| `security_privacy_and_optout_vectors.json` | 64-hex `HMAC-SHA256` blind index vectors, versioned `BYTEA` AES-256-GCM frames, 4-tier retention shred rules (`E'\\x00'::bytea` + `wa_me_link = ''`), Pino nested redaction + E.164 scrubber vectors, Tier 1/Tier 2 opt-out & quota vectors. | `tests/suites/security-privacy-retention.spec.ts` |
