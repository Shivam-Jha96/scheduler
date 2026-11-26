# SchedulerBot — Production Testing, QA & Verification Suite (`Model C v4.4 HYBRID`)

Authoritative testing strategy, final test design, reconciled production-grade datasets, executable Vitest suites, Grafana `k6` SLO load harnesses, and Prometheus `promtool` alert tests for **SchedulerBot Model C v4.4 HYBRID** (Phase 1 MVP & Phase 2 Omnichannel Roadmap).

---

## Directory Layout

```text
tests/
├── README.md                                   # This guide
├── m0-hygiene.test.ts                          # M0 baseline guardrails (FSM, Baileys purge, <=500 chars, config)
├── docs/
│   ├── TESTING_STRATEGY.md                     # Master Testing, QA & Benchmarking Strategy (v4.4)
│   └── FINAL_TEST_DESIGN.md                    # Complete Test Case Catalog across Phase 1, Phase 2 & Negative Security
├── datasets/
│   ├── README.md                               # Dataset schema & provenance guide
│   ├── mockapi_v4_4_canonical_payloads.json    # Reconciled v4.4 payloads (all 8 MockAPI deltas + Meta errors)
│   ├── nlu_golden_dataset.json                 # Production-grade NLU benchmark prompts (English + Hinglish + adversarial)
│   ├── temporal_dst_39_cases.json              # 39-case wall-clock DST, month-end, leap-year & reboot-misfire dataset
│   ├── fsm_transitions_and_chaos_matrix.json   # 10-state FSM valid/illegal transitions, CAS race & Lease Reaper matrix
│   └── security_privacy_and_optout_vectors.json# 64-hex HMAC, versioned BYTEA, 4-tier retention, Pino & opt-out vectors
├── suites/
│   ├── m1-iac-and-finops.spec.ts               # M1 IaC (Lean VPS, AWS Terraform, FinOps & verification scripts, 22 tests)
│   ├── fsm-and-cas-contracts.spec.ts           # 10-state FSM, CAS race & Erratum A.2 #7 bounded Lease Reaper checks
│   ├── mockapi-v4-4-contract.spec.ts           # 5 en_US Utility templates, https://wa.me/{{1}}, 8 deltas, HMAC/replay
│   ├── nlu-calibration-and-dataset.spec.ts     # Macro-F1 >= 0.92, ECE <= 0.05 evaluator, golden dataset & regex fast-path
│   ├── security-privacy-retention.spec.ts      # 64-hex blind index, BYTEA envelope, zeroizeBuffer, 4-tier shred, redaction
│   └── temporal-dst-39-cases.spec.ts           # All 39 DST/month-end/leap-year/travel/reboot-misfire verification cases
├── load-k6/
│   ├── webhook-ack-and-receipt-storm.js        # k6: 3x receipt storm + HMAC signature generator (ACK p99 <= 50ms)
│   └── optout-and-t0-slo-soak.js               # k6: T0 <= 1,000ms dispatch & <= 5,000ms STOP opt-out SLA soak
└── observability/
    ├── scheduler_alerts.yml                    # 4 canonical Prometheus/Alertmanager rules
    └── scheduler_alerts.test.yml               # `promtool test rules` unit test fixture
```

---

## Quickstart

```bash
# Run M0 v1.2/SQL guardrails
npm run lint:v12-guard

# Build all workspaces (required once before Vitest imports dist outputs)
npm run build

# Run all Vitest suites (M0 hygiene + all v4.4 contract, FSM, NLU, security & temporal suites)
npm run test:unit

# Run full workspace verification
npm test
```

### Optional Load & Alert Verification
```bash
# Validate Prometheus alert rules (requires promtool)
promtool check rules tests/observability/scheduler_alerts.yml
promtool test rules tests/observability/scheduler_alerts.test.yml

# Run k6 webhook receipt storm against local Fastify gateway / isolated MockAPI_Server
k6 run -e BASE_URL=http://localhost:3000 -e META_APP_SECRET=dev-meta-app-secret tests/load-k6/webhook-ack-and-receipt-storm.js
k6 run -e MOCK_BASE_URL=http://localhost:8080 -e TEST_RUN_ID=soak-$(date +%s) tests/load-k6/optout-and-t0-slo-soak.js
```
