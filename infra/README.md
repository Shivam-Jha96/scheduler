# Milestone M1 Infrastructure-as-Code (IaC) & Dual Hosting Scaffolding

**Milestone:** `M1: Zero-Trust Edge, Crypto Foundation & Production DDL`  
**Primary Epic:** `EPIC-14 (Issue #14) — Reconciled Network Ingress, Dual Hosting Profiles & Cost Modeling (FR-NET)`  
**Branch:** `feat/iac_setup`  
**Architecture Baseline:** Model C v4.4 HYBRID (`BRD-FRD-WAPP-SCHED-V2.0`, `HLD-SCHED-AUTONOMOUS-008-FINAL`, Program Implementation Plan v2.0 §3.14 & §4.4)

---

## 1. Directory Structure

```
infra/
├── lean-vps/                    # Lean VPS Zero-Trust Ingress Profile ($11.95–$27.80/mo Base)
│   ├── cloudflared/             # Zero-Trust Ingress over Outbound QUIC
│   │   ├── config.yml.template  # /webhooks/whatsapp & /health routing, :3000 forward, 404 catch-all
│   │   ├── cloudflared.service  # Hardened systemd unit (ProtectSystem=strict, PrivateTmp=yes)
│   │   └── setup-tunnel.sh      # Redundant tunnel deployment script (cloudflared-1, cloudflared-2)
│   ├── tailscale/               # Bastion-Free Administration via WireGuard CGNAT (100.x.y.z)
│   │   ├── setup-tailscale.sh   # Machine enrollment (--ssh, --advertise-tags=tag:scheduler-prod)
│   │   └── acl.json             # Tailscale ACL with Corporate SSO + WebAuthn FIDO2 MFA
│   ├── hardening/               # OS Hardening & Zero Public Ports (FR-NET-01, FR-NET-02)
│   │   ├── ufw-rules.sh         # UFW default deny incoming; allow 22 & 5432 strictly on tailscale0
│   │   └── sysctl-security.conf # Linux kernel hardening (SYN cookies, rp_filter, disable ICMP redirects)
│   ├── postgres/                # PostgreSQL 16 + pg_cron >= 1.5 + pgBackRest Provisioning
│   │   ├── postgresql.conf      # shared_preload_libraries='pg_cron', cron.database_name='scheduler_db'
│   │   ├── pgbackrest.conf      # Automated local backup stanza with AES-256-CBC and 0 S3/R2 OpEx
│   │   └── install-pg16-cron.sh # Automated PG 16 + pg_cron installer with advisory lock fallback
│   └── logging/                 # Tier-3 30-Day Ephemeral Retention (BR-05)
│       ├── promtail-config.yml  # Shipping logs to Loki with E.164 phone & wa.me link scrubbing
│       └── loki-config.yml      # Loki retention enforcer with retention_period: 720h (30 days)
│
├── terraform-aws/               # Enterprise AWS Terraform Profile ($180.00/mo Base)
│   ├── main.tf                  # AWS provider ~> 5.0, Terraform >= 1.6.0, default tags
│   ├── variables.tf             # Inputs (us-east-1/eu-central-1 region validation, 30d retention)
│   ├── outputs.tf               # Ingress URLs, KMS key ARN/alias, RDS endpoint, SG IDs
│   ├── vpc.tf                   # Multi-AZ VPC: 2x public (ALB), 2x private app (ECS), 2x isolated DB
│   ├── security_groups.tf       # ALB SG (443 only), ECS App SG (ALB only), RDS DB SG (ECS only)
│   ├── kms.tf                   # Customer Managed Key (alias/schedulerbot-dek) + key rotation
│   ├── alb.tf                   # Internet-facing ALB with TLS 1.3 & /webhooks/whatsapp routing
│   ├── waf.tf                   # Regional WAFv2 WebACL with rate limiting on /webhooks/whatsapp
│   ├── ecs.tf                   # ECS Fargate Cluster, Task Definitions (API & Worker), IAM roles
│   ├── rds_aurora.tf            # Aurora PostgreSQL 16 cluster with pg_cron parameter group
│   ├── ssm.tf                   # Bastion-free SSM Session Manager VPC endpoints & IAM profiles
│   └── cloudwatch.tf            # Log groups with strict retention_in_days = 30 (Tier-3 Ephemeral)
│
├── finops/                      # Cost Modeling & Drift Guardrails
│   ├── budget-alerts.tf         # AWS Budgets: $180 base & $481.20 100k tier (75%/90% alerts) + $0 S3/R2 check
│   ├── prometheus-finops.rules  # Recording rules & alert firing on >25% fallback drift over 24h
│   └── cost_model_v4_4.md       # Reconciled unit-economics ledger (72.5%–79.1% cost savings)
│
└── verification/                # Security & Performance Verification Scripts
    ├── verify-zero-ports.sh     # External nmap -Pn -p- audit asserting 0 open public WAN ports
    ├── probe-latency.sh         # Probing Anycast (<140ms) & Meta Graph API peering (<15ms)
    └── test-pg-cron-10s.sql     # PostgreSQL 16 sub-minute 10s cron & pg_try_advisory_lock fallback
```

---

## 2. Dual Hosting Profiles Overview

| Capability | Lean VPS Zero-Trust Profile | Enterprise AWS Terraform Profile |
| :--- | :--- | :--- |
| **Target Workload** | Self-hosted, startup, or regional EU deployment | Highly compliant corporate enterprise deployment |
| **Compute Engine** | Hetzner CPX21/CPX31 or DigitalOcean Droplet | AWS ECS Fargate (`awsvpc`, stateless Fastify containers) |
| **Database** | PostgreSQL 16 + `pg_cron >= 1.5` on host / DO Managed | Amazon Aurora PostgreSQL 16.4 Serverless v2 / Multi-AZ |
| **Public Ingress** | Cloudflare Tunnel (`cloudflared`) over QUIC (**0 public ports**) | AWS ALB + AWS WAFv2 rate limiting (**0 public container IPs**) |
| **Administrative Access** | Tailscale WireGuard (`100.x.y.z`) + WebAuthn FIDO2 MFA | AWS Systems Manager (SSM) Session Manager VPC Endpoints |
| **Object Storage** | **$0.00** (Zero S3 / Zero Cloudflare R2; local encrypted backups) | **$0.00** (Zero S3 / Zero Cloudflare R2; Aurora automated snapshots) |
| **Monthly Fixed Base** | **$11.95 – $27.80 / month** | **$180.00 / month** |
| **100k msgs/mo Total** | **$341.95 – $357.00 / month** ($0.0036/msg) | **$481.20 / month** ($0.0048/msg) |

---

## 3. Quickstart & Verification Commands

### 3.1 CI Guardrail Check (Zero S3/R2, Zero Public 22/5432 Ports, Zero Baileys)
```bash
npm run lint:v12-guard
```

### 3.2 Automated Vitest IaC & FinOps Suite (22 Tests)
```bash
npx vitest run tests/suites/m1-iac-and-finops.spec.ts
```

### 3.3 Zero-Public-Port Ingress Probe
```bash
# In CI / Local Dry-Run Mode
bash infra/verification/verify-zero-ports.sh --dry-run

# In Production
bash infra/verification/verify-zero-ports.sh --target <PUBLIC_IP> --tailscale-ip 100.64.0.1
```

### 3.4 Latency & Meta Graph Peering Probe
```bash
# In CI / Local Dry-Run Mode
bash infra/verification/probe-latency.sh --dry-run

# In Production
bash infra/verification/probe-latency.sh --ingress-url https://schedulerbot.example.com/health
```

### 3.5 PostgreSQL 16 pg_cron & Bounded Lease Reaper Verification
```bash
psql -U scheduler -d scheduler_db -f infra/verification/test-pg-cron-10s.sql
```

---

## 4. Traceability & GitHub Program Mapping

| Epic / Story / Subtask | Issue | Scope | Implementation Files |
| :--- | :--- | :--- | :--- |
| **`EPIC-14`** | `#14` | Reconciled Network Ingress & Dual Hosting Profiles | Entire `infra/` directory |
| **`EP14-T2`** | `#19` | PostgreSQL 16 Schema, pg_cron Verification & Regional Peering | `infra/verification/test-pg-cron-10s.sql`, `probe-latency.sh` |
| **`EP14-T1a`** | `#20` | Lean VPS Zero-Trust Profile & OS Hardening | `infra/lean-vps/**` |
| ↳ `EP14-T1a.1` | `#23` | cloudflared Outbound QUIC Tunnel & Systemd Service | `infra/lean-vps/cloudflared/**` |
| ↳ `EP14-T1a.2` | `#24` | UFW Default-Deny, Kernel Sysctl & Tailscale FIDO2 ACLs | `infra/lean-vps/hardening/**`, `tailscale/**` |
| ↳ `EP14-T1a.3` | `#25` | Lean VPS PostgreSQL 16 + pg_cron >= 1.5 & pgBackRest | `infra/lean-vps/postgres/**` |
| **`EP14-T1b`** | `#21` | Enterprise AWS Profile Terraform Modules | `infra/terraform-aws/**` |
| ↳ `EP14-T1b.1` | `#26` | Multi-AZ VPC, Subnets & Strict Security Groups | `infra/terraform-aws/{vpc.tf,security_groups.tf}` |
| ↳ `EP14-T1b.2` | `#27` | RDS Aurora PG 16 Cluster & KMS Envelope Cryptography | `infra/terraform-aws/{rds_aurora.tf,kms.tf}` |
| ↳ `EP14-T1b.3` | `#28` | ALB (TLS 1.3), AWS WAFv2, ECS Fargate & SSM Endpoints | `infra/terraform-aws/{alb.tf,waf.tf,ecs.tf,ssm.tf}` |
| **`EP14-T3 / T4`**| `#22` | Observability, FinOps Cost Guardrails & Verification | `infra/finops/**`, `infra/verification/**` |
| ↳ `EP14-T3.1` | `#29` | Tier 3 30-Day Ephemeral Log Retention | `infra/terraform-aws/cloudwatch.tf`, `infra/lean-vps/logging/**` |
| ↳ `EP14-T4.1` | `#30` | AWS Budget Alerts ($180/$481.20) & Prometheus Rules | `infra/finops/{budget-alerts.tf,prometheus-finops.rules,cost_model_v4_4.md}` |
| ↳ `EP14-T4.2` | `#31` | Security Verification Scripts, CI Guardrails & Vitest | `infra/verification/**`, `scripts/check-v12-guardrails.mjs`, `tests/suites/m1-iac-and-finops.spec.ts` |
