# FinOps Unit-Economics & Cost Model v4.4

**Document Version:** `4.4.0`  
**Milestone:** `M1: Zero-Trust Edge, Crypto Foundation & Production DDL`  
**Epic:** `EPIC-14 (#30)` / `FR-NET-03`, `BO-05`, `§4.4`  
**Status:** Canonical Reference

---

## 1. Executive Summary & Architectural Cost Drivers

SchedulerBot Model C v4.4 HYBRID replaces the legacy v4.2 pure Bot Relay architecture with an asymmetric **80/20 Hybrid delivery pipeline**:
1. **80% P2P Path (`wa.me` Deep-Link):** Senders execute immediate or scheduled outbound personal delivery directly over WhatsApp P2P. **Cost per message: `$0.00`** (zero Meta Cloud API utility fees).
2. **20% Bot Relay Fallback:** Automated fallback via Meta WhatsApp Cloud API v22.0 Utility Templates at **`$0.015/message`** (EU/US average blended rate).
3. **Zero Media Storage CapEx/OpEx (`$0.00`):** Total elimination of S3 and Cloudflare R2 object storage (`EPIC-12` retired). Messages are strictly text/E.164 envelopes encrypted in PostgreSQL 16 via AES-256-GCM (`BYTEA`) and AWS KMS.
4. **Zero WAN Ingress/Egress Tax:** Cloudflare Tunnel (`cloudflared`) on Lean VPS routes all inbound WhatsApp webhooks over outbound QUIC without public IPv4 addresses, NAT gateways, or ingress bandwidth fees.

---

## 2. Cryptographic Envelope Operation Economics

Every scheduled message follows the Model C v4.4 cryptographic lifecycle:
- **1x `kms:GenerateDataKey`** (256-bit AES DEK generation at schedule creation)
- **1x `kms:Decrypt`** (DEK decryption during lease worker execution / delivery)
- **1-3x `kms:Decrypt`** (Status verification, recipient opt-out verification, or retry lease recovery)

**Operational Modeling:**
- **Calls per Message:** Average `4.0x – 4.5x` AWS KMS API calls per scheduled message.
- **100,000 Messages/Month:**
  $$\text{KMS Calls} = 100{,}000 \times 4.2 = 420{,}000\text{ calls/month}$$
  $$\text{Free Tier} = 20{,}000\text{ calls/month}$$
  $$\text{Billable Calls} = 400{,}000\text{ calls/month} \times \frac{\$0.03}{10{,}000\text{ calls}} = \$1.20\text{/month}$$
  $$\text{KMS CMK Base} = 1\text{ key (alias/schedulerbot-dek)} \times \$1.00\text{/month} = \$1.00\text{/month}$$
  $$\text{Total KMS OpEx @ 100k msgs} = \$2.20\text{/month}$$

Top-of-the-hour burst allowance (:00 spikes) remains within AWS KMS regional default rate limits (10,000 requests/second in `eu-central-1` and `us-east-1`), requiring zero provisioned concurrency spend.

---

## 3. Volume Tier Unit-Economics Ledger

Comparison across three monthly delivery volumes:
- **Small Tier:** 10,000 messages / month
- **Mid Tier (Target M1):** 100,000 messages / month
- **Scale Tier:** 1,000,000 messages / month

### Unit-Economics Ledger Table

| Architecture Profile | 10,000 msgs/mo | 100,000 msgs/mo | 1,000,000 msgs/mo | Unit Cost @ 100k msgs |
| :--- | :--- | :--- | :--- | :--- |
| **Legacy Pure Bot Relay v4.2**<br>*(100% Bot Relay @ $0.015 + Redis/BullMQ/S3)* | **$400.00** | **$1,750.00** | **$15,250.00** | **$0.0175 / msg** |
| **Lean VPS Zero-Trust Profile**<br>*(Hetzner CPX21 + DO Managed PG16 + Cloudflare Tunnel)* | **$41.95 – $57.80** | **$365.00** | **$3,075.00** | **$0.00365 / msg** |
| **Enterprise AWS Profile**<br>*(ECS Fargate + Aurora PG16 + KMS + ALB/WAF + CloudWatch)* | **$210.12** | **$481.20** | **$3,192.00** | **$0.00481 / msg** |
| **Net Cost Savings (Lean VPS vs v4.2)** | **87.5%** | **79.1%** | **79.8%** | **-79.1%** |
| **Net Cost Savings (Enterprise vs v4.2)** | **47.5%** | **72.5%** | **79.1%** | **-72.5%** |

---

## 4. Itemized Monthly Cost Breakdown (100k Messages / Month)

### 4.1 Enterprise AWS Profile ($481.20 / month)

| Component | Specification | Unit Cost | Monthly Total |
| :--- | :--- | :--- | :--- |
| **Compute (ECS Fargate)** | 1x API task + 1x Worker task (0.5 vCPU, 1 GB RAM each) | $0.024/task-hr | $35.00 |
| **Database (RDS Aurora PG16)** | Aurora Serverless v2 (0.5 – 1.0 ACUs) or db.t4g.medium | Reserved/On-Demand | $85.00 |
| **Ingress & Security** | AWS ALB + AWS WAFv2 (WebACL + rate-limiting rules) | Fixed + LCU | $42.00 |
| **Key Management (KMS)** | 1 CMK + 420,000 envelope calls | $1.00 base + $1.20 ops | $2.20 |
| **Observability (CloudWatch)** | Tier 3 30-day ephemeral log retention (5 GB ingestion) | $0.50/GB | $2.50 |
| **Base Infrastructure Subtotal** | — | — | **$166.70** |
| **Contingency & VPC Endpoints** | SSM Session Manager, KMS private endpoints | Endpoints | **$14.50** |
| **Fixed Platform Base** | — | — | **$181.20** (Budget: $180.00) |
| **Meta WABA 20% Fallback** | 20,000 messages × $0.015/message | Variable | **$300.00** |
| **80% P2P `wa.me` Path** | 80,000 messages × $0.00 | $0.00 | **$0.00** |
| **Total Enterprise AWS Tier 100k** | — | — | **$481.20** |

### 4.2 Lean VPS Zero-Trust Profile ($365.00 / month)

| Component | Specification | Unit Cost | Monthly Total |
| :--- | :--- | :--- | :--- |
| **Compute (Lean VPS)** | Hetzner CPX21 (3 vCPU, 4 GB RAM, NVMe) or DO Droplet | Fixed | $14.50 |
| **Database (PostgreSQL 16)** | Local PG16 + pg_cron or DO Managed Database (1 vCPU, 2GB) | Fixed | $25.00 – $40.00 |
| **Zero-Trust Ingress** | Cloudflare Tunnel (`cloudflared`) over QUIC | Free Tier | $0.00 |
| **Zero-Trust Admin** | Tailscale WireGuard mesh + WebAuthn FIDO2 MFA | Free Tier (up to 3 users) | $0.00 |
| **Observability & Logging** | Promtail + Loki (30-day TTL local retention) | Open Source / Local disk | $0.00 |
| **KMS Envelope Ops** | Cloud KMS or Local Master DEK with HSM envelope | API / Local | $2.50 |
| **Local Base Subtotal** | — | — | **$41.95 – $57.00** |
| **Meta WABA 20% Fallback** | 20,000 messages × $0.015/message | Variable | **$300.00** |
| **80% P2P `wa.me` Path** | 80,000 messages × $0.00 | $0.00 | **$0.00** |
| **Total Lean VPS Tier 100k** | — | — | **$341.95 – $357.00** (~$365.00) |

---

## 5. FinOps Drift Guardrails & Alert Thresholds

1. **AWS Budgets (`infra/finops/budget-alerts.tf`):**
   - Base Budget: `$180.00/mo` with alerts at `75%` (`$135.00`) and `90%` (`$162.00`).
   - 100k Tier Budget: `$481.20/mo` with alerts at `75%` (`$360.90`) and `90%` (`$433.08`).
2. **Prometheus Alerting (`infra/finops/prometheus-finops.rules`):**
   - Rule `SchedulerBotFallbackRateDriftHigh`: triggers if rolling 24h fallback ratio $> 25\%$ (baseline $20\%$) for $15\text{m}$.
   - Triggers investigation runbook `docs/runbooks/FINOPS-01.md` for UX drop-off in `T0 wa.me` confirmation flow.
3. **Strict $0.00 Storage Assertion:**
   - Zero S3 buckets and zero Cloudflare R2 namespaces permitted.
   - Enforced via CI guardrail `scripts/check-v12-guardrails.mjs` and Terraform check blocks.
