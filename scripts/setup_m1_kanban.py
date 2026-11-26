#!/usr/bin/env python3
import json
import subprocess
import sys
import time

REPO = "Shivam-Jha96/scheduler"
PROJECT_ID = "PVT_kwHOATDjps4BrbmU"
STATUS_FIELD_ID = "PVTSSF_lAHOATDjps4BrbmUzhpuXfQ"
IN_PROGRESS_OPTION_ID = "364b06c4"
ASSIGNEE = "Shivam-Jha96"

MILESTONES = [
    {"title": "M0: Pre-Build Hygiene, V1.2 Purge & Errata Reconciliation", "description": "Pre-build hygiene, repository cleanup, v1.2 purge and errata reconciliation."},
    {"title": "M1: Zero-Trust Edge, Crypto Foundation & Production DDL", "description": "Zero-trust network ingress (Lean VPS + AWS), cryptographic foundation (single-use DEKs), and PostgreSQL 16 production DDL."},
    {"title": "M2: Meta WABA Integration, Identity Bootstrap & Compliance Gate", "description": "Meta WhatsApp Business Cloud API v22.0 integration, sender identity bootstrapping, and 3-state compliance gate."},
    {"title": "M3: NLU Schedule Creation, In-Chat Routing & Hybrid Engine", "description": "Volatile-RAM NLU parsing, deterministic in-chat keyword routing, and dual-track hybrid execution engine."},
    {"title": "M4: Reliability, Observability, E2E Certification & MVP Launch", "description": "Zero-double-send idempotency, Prometheus telemetry, synthetic E2E testing, and production MVP launch."},
    {"title": "M5: Phase-2 Wall-Clock Recurrence & Slash Grammar", "description": "Phase-2 wall-clock temporal recurrence math, fast-forward catchup, and slash command grammar."},
    {"title": "M6: Phase-2 Omnichannel Hexagonal SDK & Tier-1 Adapters", "description": "Phase-2 hexagonal unified transport abstraction and tier-1 adapters (Viber, Discord)."},
    {"title": "M7: Phase-2 Ecosystem Bridges, Web Control Plane & SaaS Billing", "description": "Phase-2 privacy bridges (Signal, LINE, iMessage), centralized web control plane, and enterprise SaaS billing."}
]

LABELS = [
    {"name": "area:infra", "color": "1d76db", "description": "Infrastructure, cloud profiles, networking and IaC"},
    {"name": "area:crypto", "color": "5319e7", "description": "KMS, envelope encryption, salts, and security keys"},
    {"name": "area:db", "color": "0052cc", "description": "PostgreSQL schema, migrations, pg_cron and database"},
    {"name": "area:observability", "color": "bfdadc", "description": "Telemetry, Prometheus, logging and alerting"},
    {"name": "priority:P0", "color": "b60205", "description": "Critical blocker for production MVP milestone"},
    {"name": "priority:P1", "color": "d93f0b", "description": "High priority milestone deliverable"},
    {"name": "phase-1", "color": "0e8a16", "description": "Phase 1 production MVP deliverable"},
    {"name": "phase-2", "color": "c2e0c6", "description": "Phase 2 extension deliverable"},
    {"name": "story", "color": "6f42c1", "description": "User story specification deliverable"},
    {"name": "subtask", "color": "d4c5f9", "description": "Granular implementation subtask deliverable"}
]

def run_cmd(cmd, input_text=None):
    res = subprocess.run(cmd, input=input_text, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Command failed ({res.returncode}): {' '.join(cmd)}\nStderr: {res.stderr}\nStdout: {res.stdout}")
    return res.stdout

def run_graphql(query, headers=None):
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    if headers:
        for h in headers:
            cmd.extend(["-H", h])
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"GraphQL failed: {res.stderr}\nOutput: {res.stdout}")
    data = json.loads(res.stdout)
    if "errors" in data:
        raise RuntimeError(f"GraphQL returned errors: {data['errors']}")
    return data

def get_issue_project_item_id(issue_node_id):
    query = f"""
    query {{
      node(id: "{issue_node_id}") {{
        ... on Issue {{
          projectItems(first: 10) {{
            nodes {{
              id
              project {{
                ... on ProjectV2 {{
                  id
                }}
              }}
            }}
          }}
        }}
      }}
    }}
    """
    data = run_graphql(query)
    for pnode in data.get("data", {}).get("node", {}).get("projectItems", {}).get("nodes", []):
        if pnode.get("project", {}).get("id") == PROJECT_ID:
            return pnode["id"]
    return None

def ensure_project_item_in_progress(issue_node_id):
    item_id = get_issue_project_item_id(issue_node_id)
    if not item_id:
        add_mut = f"""
        mutation {{
          addProjectV2ItemById(input: {{
            projectId: "{PROJECT_ID}",
            contentId: "{issue_node_id}"
          }}) {{
            item {{ id }}
          }}
        }}
        """
        try:
            res_add = run_graphql(add_mut)
            item_id = res_add["data"]["addProjectV2ItemById"]["item"]["id"]
        except Exception as e:
            # Maybe added automatically
            item_id = get_issue_project_item_id(issue_node_id)
            if not item_id:
                raise e

    # Update status to In Progress
    upd_status = f"""
    mutation {{
      updateProjectV2ItemFieldValue(input: {{
        projectId: "{PROJECT_ID}",
        itemId: "{item_id}",
        fieldId: "{STATUS_FIELD_ID}",
        value: {{ singleSelectOptionId: "{IN_PROGRESS_OPTION_ID}" }}
      }}) {{
        projectV2Item {{ id }}
      }}
    }}
    """
    run_graphql(upd_status)
    return item_id

def link_sub_issue(parent_node_id, child_node_id):
    subissue_mut = f"""
    mutation {{
      addSubIssue(input: {{
        issueId: "{parent_node_id}",
        subIssueId: "{child_node_id}"
      }}) {{
        issue {{ id number }}
        subIssue {{ id number }}
      }}
    }}
    """
    try:
        run_graphql(subissue_mut, headers=["GraphQL-Features: sub_issues"])
    except Exception as e:
        if "duplicate" in str(e).lower() or "only have one parent" in str(e).lower():
            print(f"Child {child_node_id} already linked to parent {parent_node_id}.")
        else:
            raise e

def get_existing_issues_by_title():
    # Fetch issues
    out = run_cmd(["gh", "issue", "list", "--repo", REPO, "--limit", "100", "--json", "number,title,id,url"])
    items = json.loads(out)
    return {item["title"]: item for item in items}

def main():
    print("=== Step 1: Manage Milestones ===")
    out = run_cmd(["gh", "api", f"repos/{REPO}/milestones?state=all"])
    existing_milestones = {m["title"]: m for m in json.loads(out)}
    milestone_map = {}

    for m in MILESTONES:
        title = m["title"]
        if title in existing_milestones:
            print(f"Milestone exists: {title} (number {existing_milestones[title]['number']})")
            milestone_map[title] = existing_milestones[title]
        else:
            print(f"Creating milestone: {title}")
            create_payload = json.dumps({"title": title, "description": m["description"], "state": "open"})
            created = json.loads(run_cmd(["gh", "api", f"repos/{REPO}/milestones", "--input", "-"], input_text=create_payload))
            print(f"Created milestone #{created['number']}: {title}")
            milestone_map[title] = created
    
    m1_title = "M1: Zero-Trust Edge, Crypto Foundation & Production DDL"
    m1_number = milestone_map[m1_title]["number"]
    print(f"M1 Milestone Title: {m1_title} (Number: {m1_number})")

    print("\n=== Step 2: Ensure Labels Exist ===")
    out_labels = run_cmd(["gh", "label", "list", "--repo", REPO, "--limit", "100"])
    existing_labels = set()
    for line in out_labels.strip().splitlines():
        if line:
            parts = line.split("\t")
            existing_labels.add(parts[0])

    for lbl in LABELS:
        name = lbl["name"]
        if name in existing_labels:
            print(f"Label exists: {name}")
        else:
            print(f"Creating label: {name}")
            run_cmd(["gh", "label", "create", name, "--repo", REPO, "--color", lbl["color"], "--description", lbl["description"]])

    print("\n=== Step 3: Fetch Parent Epic Node IDs ===")
    query_epics = """
    query {
      repository(owner: "Shivam-Jha96", name: "scheduler") {
        issue14: issue(number: 14) { id number title milestone { number } assignees(first: 5) { nodes { login } } }
        issue13: issue(number: 13) { id number title milestone { number } }
        issue3: issue(number: 3) { id number title }
      }
    }
    """
    epics_data = run_graphql(query_epics)["data"]["repository"]
    epic14 = epics_data["issue14"]
    epic13 = epics_data["issue13"]
    epic3 = epics_data["issue3"]

    print(f"Epic 14 ID: {epic14['id']}")
    print(f"Epic 13 ID: {epic13['id']}")
    print(f"Epic 3 ID: {epic3['id']}")

    print("\n=== Step 4: Update Epics #14 and #13 ===")
    print("Updating Epic #14...")
    run_cmd(["gh", "issue", "edit", "14", "--repo", REPO, "--milestone", m1_title, "--add-assignee", ASSIGNEE])
    print("Updating Epic #13...")
    run_cmd(["gh", "issue", "edit", "13", "--repo", REPO, "--milestone", m1_title])

    epic14_item_id = ensure_project_item_in_progress(epic14["id"])
    print(f"Epic #14 (item {epic14_item_id}) status set to In Progress.")

    print("\n=== Step 5: Define Stories and Subtasks ===")

    items_to_create = [
        # Story 1 (Tracking Story under Epic #3 & mapped to Epic #14)
        {
            "key": "STORY-1",
            "type": "story",
            "parent_epic": 3,
            "parent_epic_node_id": epic3["id"],
            "parent_epic_ref": "#3 [EPIC-04] & #14 [EPIC-14]",
            "title": "[EPIC-04-DDL] [STORY] PG 16+ Schema, 10-State FSM, pg_cron >= 1.5 Verification & Regional Peering (EP14-T2)",
            "labels": ["phase-1", "area:db", "area:infra", "priority:P0", "story"],
            "body": """## 🎯 Objective & Scope
Implement and verify the production PostgreSQL 16 database foundation, 10-State Schedule Lifecycle FSM DDL, sub-minute `pg_cron >= 1.5` execution verification, CAS lease queuing, and regional edge peering (`< 15 ms` Meta Graph API RTT in Frankfurt `eu-central-1` / Ashburn `us-east-1`).

## 📋 Requirements Traceability
- **Parent Epics:** Maps directly to **Epic #3 (`[EPIC-04]` 5-Stage Hybrid Lifecycle, 10-State FSM & CAS Lease Queuing)** and fulfills **Epic #14 (`[EPIC-14]` EP14-T2 Database & Regional Peering Verification)**.
- **Authoritative Specifications:**
  - `BRD-FRD-WAPP-SCHED-V2.0` (Model C v4.4 HYBRID, Sec. 4 & 4.2)
  - `HLD-SCHED-AUTONOMOUS-008-FINAL` (Model C v4.4 HYBRID, Sec. 8.4)
  - `m1_iac_implementation_plan.md` (§3 & §4 Phase 3)
- **Functional Requirements:** `FR-SCHED-01`, `FR-SCHED-02`, `FR-NET-04`, `BO-08`, `BO-09`.

## 🛠️ Scope of Deliverables
1. **PostgreSQL 16 Extensions & Schema:** Enable `uuid-ossp`, `pgcrypto`, `pg_cron` (in `shared_preload_libraries`). Establish core tables: `users`, `recipient_consents`, `recipient_global_opt_outs`, `schedules`, `schedule_audit_log`, `message_templates`, `waba_health_telemetry`.
2. **10-State FSM Lifecycle Implementation:**
   - Enforce enum state transitions: `PENDING` -> `FAST_TRACK` -> `DISPATCH_DUE` -> `PROCESSING` -> `COMPLETED` / `BOT_FALLBACK` / `FAILED` / `CANCELLED` / `DEAD_LETTER`.
   - Implement CAS concurrency lease locking (`lease_owner`, `lease_expires_at`, `version`) to eliminate double-sends.
3. **Sub-Minute `pg_cron >= 1.5` Verification (`test-pg-cron-10s.sql`):**
   - Validate 10-second cron resolution syntax on PostgreSQL 16.
   - Implement contingency verification asserting application worker advisory lock (`pg_try_advisory_lock`) fallback if managed database enforces `>= 1m` interval limits.
4. **Regional Peering Verification (`probe-latency.sh`):**
   - Measure TCP/TLS handshake latency to Meta Graph API (`graph.facebook.com`), verifying `< 15 ms` RTT when hosted in Frankfurt (`eu-central-1`) or Ashburn (`us-east-1`).

## ✅ Acceptance Criteria
- [ ] Schema DDL with 10-state FSM and CAS lease queuing compiles cleanly on PG 16.
- [ ] `infra/verification/test-pg-cron-10s.sql` executes and verifies 10s cron scheduling resolution and advisory lock fallback.
- [ ] `infra/verification/probe-latency.sh` confirms regional peering target (`< 15 ms` Meta Graph API RTT).
- [ ] Full traceability linked to Epic #3 and Epic #14.
"""
        },
        # Story 2 (Lean VPS Profile under Epic #14)
        {
            "key": "STORY-2",
            "type": "story",
            "parent_epic": 14,
            "parent_epic_node_id": epic14["id"],
            "parent_epic_ref": "#14 [EPIC-14]",
            "title": "[STORY] [EP14-T1a] Implement Lean VPS Zero-Trust Ingress Profile IaC & OS Hardening (FR-NET-01, FR-NET-02)",
            "labels": ["phase-1", "area:infra", "priority:P0", "story"],
            "body": """## 🎯 Objective & Scope
Implement the production Lean VPS Zero-Trust Ingress Profile IaC scaffolding, OS hardening, zero-public-port firewall rules, Cloudflare QUIC outbound tunnels, and Tailscale WireGuard administration for SchedulerBot Model C v4.4.

## 📋 Requirements Traceability
- **Parent Epic:** **Epic #14 (`[EPIC-14]` Reconciled Network Ingress, Dual Hosting Profiles & Cost Modeling)**
- **Authoritative Specifications:**
  - `BRD-FRD-WAPP-SCHED-V2.0` (Model C v4.4 HYBRID, Sec. 4.2 Lean VPS Profile)
  - `HLD-SCHED-AUTONOMOUS-008-FINAL` (Model C v4.4 HYBRID, Sec. 8.4)
  - `m1_iac_implementation_plan.md` (§3 Layout & §4 Phase 1)
- **Functional Requirements:** `FR-NET-01` (Zero Public WAN Ports), `FR-NET-02` (Bastion-Free Admin Access), `FR-NET-03` ($11.95–$27.80/mo Cost Target), `BO-05`, `BO-08`.

## 🛠️ Scope of Deliverables under `infra/lean-vps/`
1. **Cloudflare Tunnel (`infra/lean-vps/cloudflared/`):**
   - Redundant outbound QUIC tunnel routing `/webhooks/whatsapp` and `/health` to local Fastify application.
   - Dual systemd service templates with auto-restart and zero inbound WAN ports.
2. **OS Hardening & Firewall (`infra/lean-vps/hardening/`):**
   - UFW default-deny incoming rule with 0 WAN ports open.
   - Kernel sysctl hardening (TCP SYN cookies, ICMP redirects disabled, rp_filter).
3. **Tailscale WireGuard Administration (`infra/lean-vps/tailscale/`):**
   - Bastion-free admin access binding SSH (22) and PostgreSQL (5432) strictly to `tailscale0` (`100.x.y.z`) with FIDO2 MFA ACLs.
4. **PostgreSQL 16 & pgBackRest Installer (`infra/lean-vps/postgres/`):**
   - Automated setup of PG 16 with `pg_cron >= 1.5` and pgBackRest daily local/cold storage backups ($0 S3/R2 CapEx).

## 🔗 Subtasks
- Subtask 1: `[SUBTASK] [EP14-T1a.1] Configure cloudflared Outbound QUIC Tunnel & Redundant Systemd Service`
- Subtask 2: `[SUBTASK] [EP14-T1a.2] Implement UFW Default-Deny Firewall, Kernel Sysctl Hardening & Tailscale FIDO2 ACLs`
- Subtask 3: `[SUBTASK] [EP14-T1a.3] Author Lean VPS PostgreSQL 16 + pg_cron >= 1.5 & pgBackRest Provisioning Scripts`

## ✅ Acceptance Criteria
- [ ] All configuration files and shell scripts pass shellcheck and syntax validation.
- [ ] `verify-zero-ports.sh` external `nmap -Pn -p-` audit confirms `0` open inbound WAN ports.
- [ ] SSH and PG access verified strictly via Tailscale WireGuard interface.
"""
        },
        # Story 3 (Enterprise AWS Profile under Epic #14)
        {
            "key": "STORY-3",
            "type": "story",
            "parent_epic": 14,
            "parent_epic_node_id": epic14["id"],
            "parent_epic_ref": "#14 [EPIC-14]",
            "title": "[STORY] [EP14-T1b] Implement Enterprise AWS Terraform Profile (VPC, ECS Fargate, Aurora PG16, KMS, ALB/WAF, SSM)",
            "labels": ["phase-1", "area:infra", "priority:P0", "story"],
            "body": """## 🎯 Objective & Scope
Implement the production-ready Enterprise AWS Profile Terraform modules for SchedulerBot Model C v4.4, providing a highly-available, multi-AZ private VPC, ECS Fargate compute, Aurora PostgreSQL 16 cluster, KMS Customer Managed Key, Application Load Balancer with WAFv2 rate-limiting, and bastion-free AWS SSM Session Manager access.

## 📋 Requirements Traceability
- **Parent Epic:** **Epic #14 (`[EPIC-14]` Reconciled Network Ingress, Dual Hosting Profiles & Cost Modeling)**
- **Authoritative Specifications:**
  - `BRD-FRD-WAPP-SCHED-V2.0` (Model C v4.4 HYBRID, Sec. 4.2 Enterprise AWS Profile)
  - `HLD-SCHED-AUTONOMOUS-008-FINAL` (Model C v4.4 HYBRID, Sec. 8.4)
  - `m1_iac_implementation_plan.md` (§3 Layout & §4 Phase 2)
- **Functional Requirements:** `FR-NET-01`, `FR-NET-02`, `FR-NET-03` ($180.00/mo Base AWS Profile), `FR-SEC-01` (KMS CMK), `BO-05`, `BO-08`.

## 🛠️ Scope of Deliverables under `infra/terraform-aws/`
1. `main.tf`, `variables.tf`, `outputs.tf`: Modular Terraform architecture with pinned AWS provider (`~> 5.0`).
2. `vpc.tf` & `security_groups.tf`: Multi-AZ VPC (2 AZs), 2x Public subnets (ALB only), 2x Private app subnets (ECS tasks), 2x Isolated DB subnets (RDS Aurora). Security group chain ensuring zero public access to ECS or Aurora.
3. `kms.tf`: Customer Managed Key (`alias/schedulerbot-dek`) with automatic key rotation and strict IAM policy granting `kms:GenerateDataKey` and `kms:Decrypt` exclusively to ECS task execution roles.
4. `rds_aurora.tf`: Aurora PostgreSQL 16 cluster with `db.t4g.medium` / Serverless v2 and parameter group enabling `shared_preload_libraries='pg_cron'`.
5. `alb.tf` & `waf.tf`: Internet-facing ALB with HTTPS ACM termination, AWS WAFv2 WebACL with rate-limiting on `/webhooks/whatsapp`.
6. `ecs.tf` & `ssm.tf`: ECS Fargate cluster and task definitions (API & Worker), least-privilege IAM roles, and AWS Systems Manager VPC endpoints for bastion-free access.

## 🔗 Subtasks
- Subtask 1: `[SUBTASK] [EP14-T1b.1] Author Terraform AWS Multi-AZ Private VPC, Isolated Subnets & Zero-Public-DB Security Groups`
- Subtask 2: `[SUBTASK] [EP14-T1b.2] Author Terraform RDS Aurora PG 16 (pg_cron >= 1.5) & Cloud KMS CMK (alias/schedulerbot-dek)`
- Subtask 3: `[SUBTASK] [EP14-T1b.3] Author Terraform ALB, WAFv2 Rate-Limiting, ECS Fargate Services & Bastion-Free SSM Endpoints`

## ✅ Acceptance Criteria
- [ ] `terraform validate` and `terraform fmt -check` pass cleanly in CI.
- [ ] Aurora parameter group enables `pg_cron`, `pgcrypto`, `uuid-ossp`.
- [ ] KMS policy restricts envelope key operations to ECS task roles.
- [ ] Zero public IPv4 assigned to ECS containers and database instances.
"""
        },
        # Story 4 (Observability, FinOps, Retention & Verification under Epic #14)
        {
            "key": "STORY-4",
            "type": "story",
            "parent_epic": 14,
            "parent_epic_node_id": epic14["id"],
            "parent_epic_ref": "#14 [EPIC-14]",
            "title": "[STORY] [EP14-T3/T4] Implement Tier-3 30-Day Log Retention, FinOps Budget Alerts & Zero-Port Verification Suite",
            "labels": ["phase-1", "area:observability", "area:infra", "priority:P0", "story"],
            "body": """## 🎯 Objective & Scope
Implement Tier-3 30-day strict ephemeral log retention policies, FinOps cost guardrails and alerting, unit-economics modeling ($0 CapEx, zero S3/R2 storage), and the automated security and performance verification suite.

## 📋 Requirements Traceability
- **Parent Epic:** **Epic #14 (`[EPIC-14]` Reconciled Network Ingress, Dual Hosting Profiles & Cost Modeling)**
- **Authoritative Specifications:**
  - `BRD-FRD-WAPP-SCHED-V2.0` (Model C v4.4 HYBRID, Sec. 4 & 4.2)
  - `HLD-SCHED-AUTONOMOUS-008-FINAL` (Model C v4.4 HYBRID, Sec. 8.4)
  - `m1_iac_implementation_plan.md` (§3 Layout & §4 Phases 4 & 5)
- **Functional Requirements:** `BR-05` (Tier 3 30-Day Ephemeral Retention), `FR-NET-03` / `BO-05` (FinOps Guardrails), `FR-NET-04` (Latency & Peering Probes), `BO-08`, `BO-09`.

## 🛠️ Scope of Deliverables
1. **Tier-3 30-Day Ephemeral Log Retention:**
   - `infra/terraform-aws/cloudwatch.tf`: CloudWatch log groups configured with strict `retention_in_days = 30`.
   - `infra/lean-vps/logging/`: Promtail and Loki configuration enforcing `table_hash_cache: 30d` TTL and automatic purge.
2. **FinOps Cost Modeling & Alerts (`infra/finops/`):**
   - `budget-alerts.tf`: AWS Budgets alerting at 75% and 90% of monthly tier thresholds ($180 / $480).
   - `prometheus-finops.rules`: Alerting rule firing if 24h rolling Bot Relay fallback exceeds 25%.
   - `cost_model_v4_4.md`: Complete unit-economics breakdown asserting $0 CapEx and zero object storage.
3. **Automated Verification Suite (`infra/verification/`):**
   - `verify-zero-ports.sh`: Automated external `nmap -Pn -p-` scanning asserting 0 open WAN ports.
   - `probe-latency.sh`: Synthetic latency probe validating `< 140 ms` Anycast RTT and `< 15 ms` Meta Graph API regional peering.
   - `test-pg-cron-10s.sql`: Sub-minute 10-second `pg_cron` execution validation and advisory lock fallback check.

## 🔗 Subtasks
- Subtask 1: `[SUBTASK] [EP14-T3.1] Configure Tier-3 30-Day Ephemeral Log Retention for AWS CloudWatch & Grafana Loki`
- Subtask 2: `[SUBTASK] [EP14-T4.1] Configure FinOps AWS Budget Alerts (75%/90%), Prometheus >25% Fallback Rule & Unit-Economics Model`
- Subtask 3: `[SUBTASK] [EP14-T4.2] Build Zero-Port nmap Audit, Anycast/Meta Latency Probes & M1 IaC Automated Test Suite`

## ✅ Acceptance Criteria
- [ ] CloudWatch and Loki configurations strictly enforce 30-day retention.
- [ ] AWS budget alerts and Prometheus fallback rate rule configured and verified.
- [ ] Zero S3 or R2 bucket creation verified across all Terraform and Lean VPS manifests.
- [ ] Security audit script `verify-zero-ports.sh` and latency probe script `probe-latency.sh` execute successfully.
"""
        }
    ]

    # Map subtasks to their parent stories
    subtasks_to_create = [
        # Subtasks under Story 2
        {
            "parent_story_key": "STORY-2",
            "title": "[SUBTASK] [EP14-T1a.1] Configure cloudflared Outbound QUIC Tunnel & Redundant Systemd Service",
            "labels": ["phase-1", "area:infra", "priority:P0", "subtask"],
            "body": """## 🎯 Subtask Objective
Deliver the Cloudflare outbound QUIC tunnel configuration and redundant systemd supervision for the Lean VPS Zero-Trust Ingress Profile.

## 📋 Traceability
- **Parent Story:** `[STORY] [EP14-T1a] Implement Lean VPS Zero-Trust Ingress Profile IaC & OS Hardening`
- **Parent Epic:** `#14 [EPIC-14]`
- **Requirement:** `FR-NET-01`, `BO-08`

## 🛠️ Scope of Deliverables
- `infra/lean-vps/cloudflared/config.yml.template`: Ingress routing `/webhooks/whatsapp` to `:3000/webhooks/whatsapp`, `/health` to `:3000/health`, catch-all 404.
- `infra/lean-vps/cloudflared/cloudflared.service`: Systemd service unit with auto-restart, health checks, and redundant tunnel binding.
- `infra/lean-vps/cloudflared/setup-tunnel.sh`: Automated tunnel deployment and credential bootstrapping script.

## ✅ Acceptance Criteria
- [ ] Cloudflare tunnel configuration routes WhatsApp webhooks over outbound QUIC tunnel.
- [ ] Systemd service ensures automatic recovery and zero inbound public WAN ports.
"""
        },
        {
            "parent_story_key": "STORY-2",
            "title": "[SUBTASK] [EP14-T1a.2] Implement UFW Default-Deny Firewall, Kernel Sysctl Hardening & Tailscale FIDO2 ACLs",
            "labels": ["phase-1", "area:infra", "priority:P0", "subtask"],
            "body": """## 🎯 Subtask Objective
Implement UFW default-deny firewall rules, Linux kernel security hardening, and Tailscale WireGuard administration with WebAuthn/FIDO2 MFA for the Lean VPS profile.

## 📋 Traceability
- **Parent Story:** `[STORY] [EP14-T1a] Implement Lean VPS Zero-Trust Ingress Profile IaC & OS Hardening`
- **Parent Epic:** `#14 [EPIC-14]`
- **Requirement:** `FR-NET-01`, `FR-NET-02`, `BO-08`

## 🛠️ Scope of Deliverables
- `infra/lean-vps/hardening/ufw-rules.sh`: Default-deny incoming, allow tailscale0, zero public WAN ports.
- `infra/lean-vps/hardening/sysctl-security.conf`: TCP SYN cookies, ICMP redirect disabling, rp_filter source validation.
- `infra/lean-vps/tailscale/setup-tailscale.sh`: Non-interactive Tailscale enrollment with SSH enabled on `tailscale0`.
- `infra/lean-vps/tailscale/acl.json`: Tailscale ACL policy restricting ports 22 and 5432 strictly to authenticated admin tags with FIDO2 MFA.

## ✅ Acceptance Criteria
- [ ] UFW blocks all incoming traffic on WAN interfaces (`eth0`).
- [ ] Ports 22 (SSH) and 5432 (PostgreSQL) accessible strictly via Tailscale `100.x.y.z`.
"""
        },
        {
            "parent_story_key": "STORY-2",
            "title": "[SUBTASK] [EP14-T1a.3] Author Lean VPS PostgreSQL 16 + pg_cron >= 1.5 & pgBackRest Provisioning Scripts",
            "labels": ["phase-1", "area:db", "area:infra", "priority:P0", "subtask"],
            "body": """## 🎯 Subtask Objective
Deliver automated installation, configuration, and backup scripting for PostgreSQL 16 with `pg_cron >= 1.5` and pgBackRest on Debian/Ubuntu Lean VPS.

## 📋 Traceability
- **Parent Story:** `[STORY] [EP14-T1a] Implement Lean VPS Zero-Trust Ingress Profile IaC & OS Hardening`
- **Parent Epic:** `#14 [EPIC-14]`
- **Requirement:** `FR-NET-03`, `FR-SCHED-01`, `BO-05`

## 🛠️ Scope of Deliverables
- `infra/lean-vps/postgres/install-pg16-cron.sh`: Installs official PGDG PG 16 and `postgresql-16-cron`.
- `infra/lean-vps/postgres/postgresql.conf`: Configures `shared_preload_libraries = 'pg_cron'` and `cron.database_name = 'scheduler_db'`.
- `infra/lean-vps/postgres/pgbackrest.conf`: Automated daily cold/local storage backups achieving $0 S3/R2 spend.

## ✅ Acceptance Criteria
- [ ] Script successfully provisions PG 16 with `pg_cron` loaded into shared libraries.
- [ ] pgBackRest configured for local/cold retention with zero external object storage spend.
"""
        },
        # Subtasks under Story 3
        {
            "parent_story_key": "STORY-3",
            "title": "[SUBTASK] [EP14-T1b.1] Author Terraform AWS Multi-AZ Private VPC, Isolated Subnets & Zero-Public-DB Security Groups",
            "labels": ["phase-1", "area:infra", "priority:P0", "subtask"],
            "body": """## 🎯 Subtask Objective
Author Terraform modules for AWS Multi-AZ VPC networking, subnet isolation, and strict security group ingress/egress boundaries.

## 📋 Traceability
- **Parent Story:** `[STORY] [EP14-T1b] Implement Enterprise AWS Terraform Profile (VPC, ECS Fargate, Aurora PG16, KMS, ALB/WAF, SSM)`
- **Parent Epic:** `#14 [EPIC-14]`
- **Requirement:** `FR-NET-01`, `FR-NET-03`, `BO-08`

## 🛠️ Scope of Deliverables
- `infra/terraform-aws/vpc.tf`: Multi-AZ VPC across 2 Availability Zones; 2x public subnets (ALB only), 2x private app subnets (ECS tasks), 2x isolated DB subnets (Aurora).
- `infra/terraform-aws/security_groups.tf`: Layered security group chain: ALB accepts HTTPS (443); ECS tasks accept only from ALB SG; Aurora accepts 5432 only from ECS task SG. Zero public egress/ingress on DB.

## ✅ Acceptance Criteria
- [ ] Isolated subnets have zero route table entries to Internet Gateway.
- [ ] Security group rules strictly isolate Aurora PG to application container access.
"""
        },
        {
            "parent_story_key": "STORY-3",
            "title": "[SUBTASK] [EP14-T1b.2] Author Terraform RDS Aurora PG 16 (pg_cron >= 1.5) & Cloud KMS CMK (alias/schedulerbot-dek)",
            "labels": ["phase-1", "area:db", "area:crypto", "area:infra", "priority:P0", "subtask"],
            "body": """## 🎯 Subtask Objective
Author Terraform modules for RDS Aurora PostgreSQL 16 with custom `pg_cron` parameter groups, and AWS Cloud KMS Customer Managed Key for envelope encryption.

## 📋 Traceability
- **Parent Story:** `[STORY] [EP14-T1b] Implement Enterprise AWS Terraform Profile (VPC, ECS Fargate, Aurora PG16, KMS, ALB/WAF, SSM)`
- **Parent Epic:** `#14 [EPIC-14]`
- **Requirement:** `FR-SEC-01`, `FR-SCHED-01`, `BO-05`

## 🛠️ Scope of Deliverables
- `infra/terraform-aws/rds_aurora.tf`: Aurora PostgreSQL 16 cluster with `db.t4g.medium` or Serverless v2; parameter group enabling `shared_preload_libraries = 'pg_cron'` and extensions (`uuid-ossp`, `pgcrypto`).
- `infra/terraform-aws/kms.tf`: AWS KMS CMK (`alias/schedulerbot-dek`) with annual key rotation and IAM key policy restricting `kms:GenerateDataKey` and `kms:Decrypt` to ECS task roles.

## ✅ Acceptance Criteria
- [ ] Parameter group configures `pg_cron` and required cryptographic extensions.
- [ ] KMS key policy enforces least-privilege cryptographic access.
"""
        },
        {
            "parent_story_key": "STORY-3",
            "title": "[SUBTASK] [EP14-T1b.3] Author Terraform ALB, WAFv2 Rate-Limiting, ECS Fargate Services & Bastion-Free SSM Endpoints",
            "labels": ["phase-1", "area:infra", "priority:P0", "subtask"],
            "body": """## 🎯 Subtask Objective
Author Terraform modules for internet-facing ALB, AWS WAFv2 rate-limiting, ECS Fargate API/Worker task definitions, and AWS Systems Manager VPC endpoints.

## 📋 Traceability
- **Parent Story:** `[STORY] [EP14-T1b] Implement Enterprise AWS Terraform Profile (VPC, ECS Fargate, Aurora PG16, KMS, ALB/WAF, SSM)`
- **Parent Epic:** `#14 [EPIC-14]`
- **Requirement:** `FR-NET-01`, `FR-NET-02`, `BO-08`

## 🛠️ Scope of Deliverables
- `infra/terraform-aws/alb.tf`: Internet-facing ALB with HTTPS listener and target groups for Fastify service.
- `infra/terraform-aws/waf.tf`: WAFv2 WebACL with AWS managed rule groups and URI rate-limiting on `/webhooks/whatsapp`.
- `infra/terraform-aws/ecs.tf`: ECS Fargate cluster, task definitions (Fastify API and worker), IAM task execution roles.
- `infra/terraform-aws/ssm.tf`: AWS SSM Session Manager VPC endpoints allowing console access without bastion hosts or open SSH ports.

## ✅ Acceptance Criteria
- [ ] ALB and WAF protect ingress and rate-limit webhook abuse.
- [ ] ECS tasks run in private subnets with no public IPs.
- [ ] Bastion-free admin access established via AWS SSM endpoints.
"""
        },
        # Subtasks under Story 4
        {
            "parent_story_key": "STORY-4",
            "title": "[SUBTASK] [EP14-T3.1] Configure Tier-3 30-Day Ephemeral Log Retention for AWS CloudWatch & Grafana Loki",
            "labels": ["phase-1", "area:observability", "area:infra", "priority:P0", "subtask"],
            "body": """## 🎯 Subtask Objective
Configure strict Tier-3 30-day ephemeral log retention rules in AWS CloudWatch Log Groups and Grafana Loki configurations.

## 📋 Traceability
- **Parent Story:** `[STORY] [EP14-T3/T4] Implement Tier-3 30-Day Log Retention, FinOps Budget Alerts & Zero-Port Verification Suite`
- **Parent Epic:** `#14 [EPIC-14]`
- **Requirement:** `BR-05`, `BO-04`

## 🛠️ Scope of Deliverables
- `infra/terraform-aws/cloudwatch.tf`: CloudWatch log groups for ECS API and Worker services with `retention_in_days = 30`.
- `infra/lean-vps/logging/promtail-config.yml`: Log shipper capturing container stdout/stderr.
- `infra/lean-vps/logging/loki-config.yml`: Loki configuration enforcing `table_hash_cache: 30d` TTL and automatic table pruning.

## ✅ Acceptance Criteria
- [ ] 30-day strict retention verified in both AWS CloudWatch and Grafana Loki configs.
- [ ] Zero unencrypted PII retained beyond 30 days.
"""
        },
        {
            "parent_story_key": "STORY-4",
            "title": "[SUBTASK] [EP14-T4.1] Configure FinOps AWS Budget Alerts (75%/90%), Prometheus >25% Fallback Rule & Unit-Economics Model",
            "labels": ["phase-1", "area:observability", "area:infra", "priority:P0", "subtask"],
            "body": """## 🎯 Subtask Objective
Deliver FinOps budget alerting, Prometheus fallback rate anomaly alerts, and the Model C v4.4 unit-economics ledger.

## 📋 Traceability
- **Parent Story:** `[STORY] [EP14-T3/T4] Implement Tier-3 30-Day Log Retention, FinOps Budget Alerts & Zero-Port Verification Suite`
- **Parent Epic:** `#14 [EPIC-14]`
- **Requirement:** `FR-NET-03`, `BO-05`

## 🛠️ Scope of Deliverables
- `infra/finops/budget-alerts.tf`: AWS Budgets alerts triggered at 75% and 90% of tier spend ($180.00 / $480.00/mo).
- `infra/finops/prometheus-finops.rules`: Prometheus alert firing if 24-hour fallback rate exceeds 25% (`scheduler_bot_fallback_dispatched_total / scheduler_messages_scheduled_total > 0.25`).
- `infra/finops/cost_model_v4_4.md`: Reconciled unit economics documenting $0 CapEx, zero S3/R2 storage spend, and fallback cost modeling.

## ✅ Acceptance Criteria
- [ ] AWS budget alerts defined with SNS notification actions.
- [ ] Prometheus fallback alerting rule passes `promtool check rules`.
- [ ] Cost model formally documents $0 CapEx and zero object storage constraints.
"""
        },
        {
            "parent_story_key": "STORY-4",
            "title": "[SUBTASK] [EP14-T4.2] Build Zero-Port nmap Audit, Anycast/Meta Latency Probes & M1 IaC Automated Test Suite",
            "labels": ["phase-1", "area:infra", "priority:P0", "subtask"],
            "body": """## 🎯 Subtask Objective
Build the automated security audit and performance verification scripts for the M1 IaC deliverable suite and integrate them into CI workflows.

## 📋 Traceability
- **Parent Story:** `[STORY] [EP14-T3/T4] Implement Tier-3 30-Day Log Retention, FinOps Budget Alerts & Zero-Port Verification Suite`
- **Parent Epic:** `#14 [EPIC-14]`
- **Requirement:** `FR-NET-01`, `FR-NET-04`, `BO-08`, `BO-09`

## 🛠️ Scope of Deliverables
- `infra/verification/verify-zero-ports.sh`: Automated external `nmap -Pn -p-` port scan asserting `0` open inbound WAN ports.
- `infra/verification/probe-latency.sh`: Synthetic latency probe validating `< 140 ms` Anycast RTT and `< 15 ms` Meta Graph API regional peering.
- `infra/verification/test-pg-cron-10s.sql`: Sub-minute 10s `pg_cron` scheduling test and advisory lock fallback verification.
- `.github/workflows/ci.yml`: Integration of Terraform linting (`fmt -check`, `validate`) and shell script validation.

## ✅ Acceptance Criteria
- [ ] External port scan script asserts zero open inbound ports.
- [ ] Synthetic probe script measures Anycast RTT and Meta Graph API regional peering latency.
- [ ] pg_cron SQL script validates 10-second cron scheduling.
"""
        }
    ]

    print("\n=== Step 6: Create or Reconcile Stories and Subtasks ===")
    existing_issues = get_existing_issues_by_title()
    created_items = {}

    # 6.1 Stories
    for s in items_to_create:
        title = s["title"]
        if title in existing_issues:
            issue_number = existing_issues[title]["number"]
            issue_node_id = existing_issues[title]["id"]
            print(f"Story already exists as #{issue_number}: {title}")
        else:
            print(f"Creating Story: {title}...")
            cmd = [
                "gh", "issue", "create",
                "--repo", REPO,
                "--title", s["title"],
                "--body", s["body"],
                "--assignee", ASSIGNEE,
                "--milestone", m1_title
            ]
            for l in s["labels"]:
                cmd.extend(["--label", l])
            
            issue_url = run_cmd(cmd).strip()
            issue_number = int(issue_url.split("/")[-1])
            print(f"Created Issue #{issue_number}: {issue_url}")

            node_query = f"""
            query {{
              repository(owner: "Shivam-Jha96", name: "scheduler") {{
                issue(number: {issue_number}) {{
                  id
                }}
              }}
            }}
            """
            issue_node_id = run_graphql(node_query)["data"]["repository"]["issue"]["id"]

        # Link as sub-issue
        parent_id = s["parent_epic_node_id"]
        link_sub_issue(parent_id, issue_node_id)

        # Ensure on project and In Progress
        item_id = ensure_project_item_in_progress(issue_node_id)
        print(f"Story #{issue_number} (Item {item_id}) status: In Progress.")

        created_items[s["key"]] = {
            "type": "story",
            "number": issue_number,
            "node_id": issue_node_id,
            "item_id": item_id,
            "title": s["title"],
            "parent_epic": s["parent_epic_ref"],
            "parent_epic_node_id": parent_id,
            "assignee": ASSIGNEE,
            "milestone": m1_title,
            "status": "In Progress"
        }
        time.sleep(1)

    # 6.2 Subtasks
    for st in subtasks_to_create:
        parent_story = created_items[st["parent_story_key"]]
        parent_story_node_id = parent_story["node_id"]
        parent_story_number = parent_story["number"]
        title = st["title"]

        if title in existing_issues:
            issue_number = existing_issues[title]["number"]
            issue_node_id = existing_issues[title]["id"]
            print(f"Subtask already exists as #{issue_number}: {title}")
        else:
            print(f"\nCreating Subtask: {title} under Story #{parent_story_number}...")
            cmd = [
                "gh", "issue", "create",
                "--repo", REPO,
                "--title", st["title"],
                "--body", st["body"],
                "--assignee", ASSIGNEE,
                "--milestone", m1_title
            ]
            for l in st["labels"]:
                cmd.extend(["--label", l])
            
            issue_url = run_cmd(cmd).strip()
            issue_number = int(issue_url.split("/")[-1])
            print(f"Created Subtask Issue #{issue_number}: {issue_url}")

            node_query = f"""
            query {{
              repository(owner: "Shivam-Jha96", name: "scheduler") {{
                issue(number: {issue_number}) {{
                  id
                }}
              }}
            }}
            """
            issue_node_id = run_graphql(node_query)["data"]["repository"]["issue"]["id"]

        # Link as sub-issue of parent story
        link_sub_issue(parent_story_node_id, issue_node_id)

        # Ensure on project and In Progress
        item_id = ensure_project_item_in_progress(issue_node_id)
        print(f"Subtask #{issue_number} (Item {item_id}) status: In Progress.")

        subtask_key = f"{st['parent_story_key']}_SUBTASK_{issue_number}"
        created_items[subtask_key] = {
            "type": "subtask",
            "number": issue_number,
            "node_id": issue_node_id,
            "item_id": item_id,
            "title": st["title"],
            "parent_story": f"#{parent_story_number} {parent_story['title']}",
            "parent_story_node_id": parent_story_node_id,
            "assignee": ASSIGNEE,
            "milestone": m1_title,
            "status": "In Progress"
        }
        time.sleep(1)

    # 6.3 Write Manifest
    manifest = {
        "metadata": {
            "repository": REPO,
            "project_id": PROJECT_ID,
            "milestone_m1_number": m1_number,
            "milestone_m1_title": m1_title,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "assignee": ASSIGNEE,
            "target_status": "In Progress"
        },
        "milestones": {title: m["number"] for title, m in milestone_map.items()},
        "epics": {
            "EPIC-14": {
                "number": 14,
                "node_id": epic14["id"],
                "item_id": epic14_item_id,
                "title": epic14["title"],
                "milestone": m1_title,
                "assignee": ASSIGNEE,
                "status": "In Progress"
            },
            "EPIC-13": {
                "number": 13,
                "node_id": epic13["id"],
                "title": epic13["title"],
                "milestone": m1_title
            },
            "EPIC-04": {
                "number": 3,
                "node_id": epic3["id"],
                "title": epic3["title"]
            }
        },
        "created_items": created_items
    }

    manifest_path = "scripts/m1_iac_kanban_items.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest successfully written to {manifest_path}!")

if __name__ == "__main__":
    main()
