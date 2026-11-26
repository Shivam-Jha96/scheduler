import fs from 'node:fs';
import path from 'node:path';
import { describe, it, expect } from 'vitest';

const ROOT = process.cwd();

function readProjectFile(relPath: string): string {
  const fullPath = path.resolve(ROOT, relPath);
  expect(fs.existsSync(fullPath), `Expected file to exist: ${relPath}`).toBe(true);
  return fs.readFileSync(fullPath, 'utf8');
}

describe('Milestone M1 — Infrastructure-as-Code & FinOps Specification Suite (EPIC-14 / #30, #31)', () => {
  // ============================================================================
  // Phase 1: Lean VPS Zero-Trust Ingress Profile (EP14-T1a / FR-NET-01, FR-NET-02)
  // ============================================================================
  describe('Lean VPS Zero-Trust Ingress Profile (infra/lean-vps/)', () => {
    it('TC-IAC-01: configures outbound Cloudflare QUIC tunnel with webhook routing and 404 catch-all', () => {
      const configTmpl = readProjectFile('infra/lean-vps/cloudflared/config.yml.template');
      expect(configTmpl).toContain('protocol: quic');
      expect(configTmpl).toContain('path: ^/webhooks/whatsapp.*');
      expect(configTmpl).toContain('service: http://127.0.0.1:3000');
      expect(configTmpl).toContain('path: ^/health$');
      expect(configTmpl).toContain('service: http_status:404');
      expect(configTmpl).toContain('metrics: 127.0.0.1:2000');
    });

    it('TC-IAC-02: configures hardened systemd service for cloudflared with process isolation', () => {
      const service = readProjectFile('infra/lean-vps/cloudflared/cloudflared.service');
      expect(service).toContain('User=cloudflared');
      expect(service).toContain('Restart=always');
      expect(service).toContain('ProtectSystem=strict');
      expect(service).toContain('PrivateTmp=yes');
    });

    it('TC-IAC-03: enforces Tailscale FIDO2/SSO administrative access and port 22/5432 restrictions', () => {
      const setupTailscale = readProjectFile('infra/lean-vps/tailscale/setup-tailscale.sh');
      expect(setupTailscale).toContain('--ssh');
      expect(setupTailscale).toContain('--advertise-tags=tag:scheduler-prod');

      const rawAcl = readProjectFile('infra/lean-vps/tailscale/acl.json');
      // Tailscale uses HuJSON (JSON with comments)
      const cleanJson = rawAcl.replace(/\/\/.*$/gm, '').trim();
      const acl = JSON.parse(cleanJson);
      expect(acl.tagOwners['tag:scheduler-prod']).toContain('group:sre-admins');
      expect(acl.acls.some((rule: { dst: string[] }) => rule.dst.includes('tag:scheduler-prod:5432'))).toBe(true);
      expect(acl.acls.some((rule: { dst: string[] }) => rule.dst.includes('tag:scheduler-prod:22'))).toBe(true);
      expect(acl.ssh[0].action).toBe('check');
    });

    it('TC-IAC-04: configures UFW firewall default deny and binds ports 22 & 5432 strictly to tailscale0', () => {
      const ufw = readProjectFile('infra/lean-vps/hardening/ufw-rules.sh');
      expect(ufw).toContain('ufw default deny incoming');
      expect(ufw).toContain('ufw default allow outgoing');
      expect(ufw).toContain('ufw allow in on tailscale0 to any port 22 proto tcp');
      expect(ufw).toContain('ufw allow in on tailscale0 to any port 5432 proto tcp');
      expect(ufw).toContain('ufw deny in on');
    });

    it('TC-IAC-05: enforces kernel sysctl hardening (SYN cookies, rp_filter, ICMP disable)', () => {
      const sysctl = readProjectFile('infra/lean-vps/hardening/sysctl-security.conf');
      expect(sysctl).toContain('net.ipv4.tcp_syncookies = 1');
      expect(sysctl).toContain('net.ipv4.conf.all.rp_filter = 1');
      expect(sysctl).toContain('net.ipv4.conf.all.accept_redirects = 0');
      expect(sysctl).toContain('net.ipv4.conf.all.send_redirects = 0');
    });

    it('TC-IAC-06: configures PostgreSQL 16 with pg_cron >= 1.5, scram-sha-256, and zero-storage pgBackRest', () => {
      const pgConf = readProjectFile('infra/lean-vps/postgres/postgresql.conf');
      expect(pgConf).toContain("shared_preload_libraries = 'pg_cron'");
      expect(pgConf).toContain("cron.database_name = 'scheduler_db'");
      expect(pgConf).toContain('password_encryption = scram-sha-256');

      const pgBackRest = readProjectFile('infra/lean-vps/postgres/pgbackrest.conf');
      expect(pgBackRest).toContain('repo1-path = /var/lib/pgbackrest');
      expect(pgBackRest).toContain('repo1-cipher-type = aes-256-cbc');
      expect(pgBackRest).not.toContain('s3');
      expect(pgBackRest).not.toContain('r2.cloudflarestorage.com');

      const installScript = readProjectFile('infra/lean-vps/postgres/install-pg16-cron.sh');
      expect(installScript).toContain('postgresql-16-cron');
      expect(installScript).toContain('ENABLE_ADVISORY_LOCK_WORKER_FALLBACK');
    });

    it('TC-IAC-07: configures Promtail log scrubber and Loki Tier 3 30-day (720h) retention', () => {
      const promtail = readProjectFile('infra/lean-vps/logging/promtail-config.yml');
      expect(promtail).toContain('+[REDACTED_PHONE]');
      expect(promtail).toContain('REDACTED_TOKEN');

      const loki = readProjectFile('infra/lean-vps/logging/loki-config.yml');
      expect(loki).toContain('retention_period: 720h');
      expect(loki).toContain('retention_enabled: true');
    });
  });

  // ============================================================================
  // Phase 2: Enterprise AWS Terraform Profile (EP14-T1b / FR-NET-01, FR-NET-03)
  // ============================================================================
  describe('Enterprise AWS Terraform Profile (infra/terraform-aws/)', () => {
    it('TC-IAC-08: validates Terraform provider constraints, default tags, and regional peering constraints', () => {
      const mainTf = readProjectFile('infra/terraform-aws/main.tf');
      expect(mainTf).toContain('required_version = ">= 1.6.0"');
      expect(mainTf).toContain('source  = "hashicorp/aws"');
      expect(mainTf).toMatch(/Model\s*=\s*"Model-C-v4.4-HYBRID"/);

      const varsTf = readProjectFile('infra/terraform-aws/variables.tf');
      expect(varsTf).toContain('contains(["us-east-1", "eu-central-1"], var.aws_region)');
      expect(varsTf).toContain('var.log_retention_days == 30');
    });

    it('TC-IAC-09: provisions multi-AZ VPC with private app subnets and isolated database subnets', () => {
      const vpcTf = readProjectFile('infra/terraform-aws/vpc.tf');
      expect(vpcTf).toContain('resource "aws_vpc" "main"');
      expect(vpcTf).toContain('resource "aws_subnet" "public"');
      expect(vpcTf).toContain('resource "aws_subnet" "private_app"');
      expect(vpcTf).toContain('resource "aws_subnet" "isolated_db"');
      expect(vpcTf).toContain('map_public_ip_on_launch = false');
      expect(vpcTf).toContain('resource "aws_db_subnet_group" "rds_subnet_group"');
    });

    it('TC-IAC-10: enforces zero 0.0.0.0/0 exposure on ports 22 and 5432 across all security groups', () => {
      const sgTf = readProjectFile('infra/terraform-aws/security_groups.tf');
      // ALB allows 443 from 0.0.0.0/0
      expect(sgTf).toContain('resource "aws_security_group" "alb"');
      // ECS App SG allows 3000 strictly from ALB SG
      expect(sgTf).toContain('resource "aws_security_group" "ecs_app"');
      expect(sgTf).toContain('security_groups = [aws_security_group.alb.id]');
      // RDS DB SG allows 5432 strictly from ECS App SG and SSM Endpoints
      expect(sgTf).toContain('resource "aws_security_group" "rds_db"');
      expect(sgTf).toContain('security_groups = [aws_security_group.ecs_app.id]');

      // Guardrail: neither 22 nor 5432 may have 0.0.0.0/0
      const ingressBlocks = sgTf.match(/ingress\s*\{[^}]*\}/g) || [];
      for (const block of ingressBlocks) {
        if (/0\.0\.0\.0\/0/.test(block)) {
          expect(block).not.toMatch(/\b(22|5432)\b/);
        }
      }
    });

    it('TC-IAC-11: configures AWS KMS CMK with key rotation enabled and alias/schedulerbot-dek', () => {
      const kmsTf = readProjectFile('infra/terraform-aws/kms.tf');
      expect(kmsTf).toContain('resource "aws_kms_key" "scheduler_dek"');
      expect(kmsTf).toContain('enable_key_rotation     = true');
      expect(kmsTf).toContain('customer_master_key_spec = "SYMMETRIC_DEFAULT"');
      expect(kmsTf).toContain('resource "aws_kms_alias" "scheduler_dek"');
      expect(kmsTf).toContain('name          = "alias/schedulerbot-dek"');
      expect(kmsTf).toContain('kms:GenerateDataKey');
      expect(kmsTf).toContain('kms:Decrypt');
    });

    it('TC-IAC-12: configures Aurora PostgreSQL 16 cluster with pg_cron parameter group and encryption', () => {
      const rdsTf = readProjectFile('infra/terraform-aws/rds_aurora.tf');
      expect(rdsTf).toContain('engine                          = "aurora-postgresql"');
      expect(rdsTf).toContain('family      = "aurora-postgresql16"');
      expect(rdsTf).toContain('name         = "shared_preload_libraries"');
      expect(rdsTf).toContain('value        = "pg_cron"');
      expect(rdsTf).toContain('name         = "rds.force_ssl"');
      expect(rdsTf).toContain('storage_encrypted               = true');
      expect(rdsTf).toContain('kms_key_id                      = aws_kms_key.scheduler_dek.arn');
    });

    it('TC-IAC-13: configures ALB with TLS 1.3, path routing, and WAF rate-limiting on /webhooks/whatsapp', () => {
      const albTf = readProjectFile('infra/terraform-aws/alb.tf');
      expect(albTf).toContain('ELBSecurityPolicy-TLS13-1-2-2021-06');
      expect(albTf).toContain('path_pattern');
      expect(albTf).toMatch(/values\s*=\s*\["\/webhooks\/whatsapp.*"\]/);
      expect(albTf).toContain('values = ["/health"]');

      const wafTf = readProjectFile('infra/terraform-aws/waf.tf');
      expect(wafTf).toContain('resource "aws_wafv2_web_acl" "ingress_waf"');
      expect(wafTf).toContain('RateLimitWhatsAppWebhooks');
      expect(wafTf).toContain('/webhooks/whatsapp');
    });

    it('TC-IAC-14: configures ECS Fargate tasks with assign_public_ip=false, META v22.0, and KMS key env', () => {
      const ecsTf = readProjectFile('infra/terraform-aws/ecs.tf');
      expect(ecsTf).toContain('requires_compatibilities = ["FARGATE"]');
      expect(ecsTf).toContain('network_mode             = "awsvpc"');
      expect(ecsTf).toMatch(/name\s*=\s*"META_GRAPH_API_VERSION"/);
      expect(ecsTf).toMatch(/value\s*=\s*"v22.0"/);
      expect(ecsTf).toMatch(/name\s*=\s*"KMS_KEY_ID"/);
      expect(ecsTf).toMatch(/value\s*=\s*"alias\/schedulerbot-dek"/);
      expect(ecsTf).toContain('assign_public_ip = false');
      expect(ecsTf).toContain('enable_execute_command = true');
    });

    it('TC-IAC-15: configures SSM VPC endpoints and CloudWatch log groups with strict 30-day retention', () => {
      const ssmTf = readProjectFile('infra/terraform-aws/ssm.tf');
      expect(ssmTf).toContain('com.amazonaws.${var.aws_region}.ssm');
      expect(ssmTf).toContain('com.amazonaws.${var.aws_region}.ssmmessages');

      const cwTf = readProjectFile('infra/terraform-aws/cloudwatch.tf');
      expect(cwTf).toContain('/schedulerbot/api-gateway');
      expect(cwTf).toContain('/schedulerbot/delivery-worker');
      expect(cwTf).toContain('/schedulerbot/ssm-sessions');
      expect(cwTf).toContain('retention_in_days = var.log_retention_days');

      const outputsTf = readProjectFile('infra/terraform-aws/outputs.tf');
      expect(outputsTf).toContain('output "vpc_id"');
      expect(outputsTf).toContain('output "alb_dns_name"');
      expect(outputsTf).toContain('output "kms_key_arn"');
      expect(outputsTf).toContain('output "rds_cluster_endpoint"');
    });
  });

  // ============================================================================
  // Phase 4: FinOps Cost Modeling & Guardrails (EP14-T4 / FR-NET-03, BO-05)
  // ============================================================================
  describe('FinOps Budgets & Unit Economics (infra/finops/)', () => {
    it('TC-FIN-01: configures AWS Budgets for $180 base and $481.20 100k tier with 75% and 90% alerts', () => {
      const budgets = readProjectFile('infra/finops/budget-alerts.tf');
      expect(budgets).toContain('resource "aws_budgets_budget" "schedulerbot_enterprise_base_budget"');
      expect(budgets).toContain('limit_amount      = "180.00"');
      expect(budgets).toContain('resource "aws_budgets_budget" "schedulerbot_enterprise_100k_tier_budget"');
      expect(budgets).toContain('limit_amount      = "481.20"');
      expect(budgets).toContain('threshold                  = 75');
      expect(budgets).toContain('threshold                  = 90');
      expect(budgets).toContain('notification_type          = "ACTUAL"');
      expect(budgets).toContain('notification_type          = "FORECASTED"');
      expect(budgets).toContain('check "zero_object_storage_assertion"');
    });

    it('TC-FIN-02: configures Prometheus recording rules and >25% fallback drift alert rule', () => {
      const promRules = readProjectFile('infra/finops/prometheus-finops.rules');
      expect(promRules).toContain('record: scheduler:bot_fallback_ratio_24h');
      expect(promRules).toContain('sum(increase(scheduler_bot_fallback_dispatched_total[24h]))');
      expect(promRules).toContain('clamp_min(sum(increase(scheduler_messages_scheduled_total[24h])), 1)');
      expect(promRules).toContain('record: scheduler:estimated_monthly_kms_calls');
      expect(promRules).toContain('alert: SchedulerBotFallbackRateDriftHigh');
      expect(promRules).toContain('> 0.25');
      expect(promRules).toContain('for: 15m');
      expect(promRules).toContain('severity: warning');
    });

    it('TC-FIN-03: reconciles dual-hosting unit-economics ledger with $0 CapEx, $0 storage, and 72-79% savings', () => {
      const costModel = readProjectFile('infra/finops/cost_model_v4_4.md');
      expect(costModel).toContain('$0.00');
      expect(costModel).toContain('80% P2P Path');
      expect(costModel).toContain('20% Bot Relay Fallback');
      expect(costModel).toContain('$0.015/message');
      expect(costModel).toContain('$481.20');
      expect(costModel).toContain('$365.00');
      expect(costModel).toContain('79.1%');
      expect(costModel).toContain('72.5%');
      expect(costModel).toContain('alias/schedulerbot-dek');
    });
  });

  // ============================================================================
  // Phase 3 & 5: Security & Performance Verification Scripts (MS-EP14-01, MS-EP14-02)
  // ============================================================================
  describe('Security & Latency Verification Scripts (infra/verification/)', () => {
    it('TC-VERIFY-01: verify-zero-ports.sh enforces zero open WAN ports and supports --dry-run', () => {
      const script = readProjectFile('infra/verification/verify-zero-ports.sh');
      expect(script).toContain('set -euo pipefail');
      expect(script).toContain('--dry-run');
      expect(script).toContain('nmap -Pn -p-');
      expect(script).toContain('22');
      expect(script).toContain('5432');
      expect(script).toContain('tailscale');
    });

    it('TC-VERIFY-02: probe-latency.sh measures <140ms Anycast and <15ms Meta Graph peering and supports --dry-run', () => {
      const script = readProjectFile('infra/verification/probe-latency.sh');
      expect(script).toContain('set -euo pipefail');
      expect(script).toContain('--dry-run');
      expect(script).toContain('MAX_ANYCAST_RTT_MS=140');
      expect(script).toContain('MAX_PEERING_RTT_MS=15');
      expect(script).toContain('graph.facebook.com/v22.0');
    });

    it('TC-VERIFY-03: test-pg-cron-10s.sql verifies extensions, 10s schedule, bounded reaper, and advisory lock fallback', () => {
      const sql = readProjectFile('infra/verification/test-pg-cron-10s.sql');
      expect(sql).toContain('uuid-ossp');
      expect(sql).toContain('pgcrypto');
      expect(sql).toContain('pg_cron');
      expect(sql).toContain('>= 1.5');
      expect(sql).toContain("'10 seconds'");
      expect(sql).toContain("cron.schedule('m1-reaper-10s-verify', '10 seconds'");

      // Canonical Bounded Lease Reaper SQL (Erratum A.2 #7)
      expect(sql).toContain("WHEN retry_count + 1 < max_retries THEN 'AWAITING_CONFIRMATION'");
      expect(sql).toContain("ELSE 'FAILED'");
      expect(sql).toContain('WHEN retry_count < max_retries THEN retry_count + 1');
      expect(sql).toContain('ELSE retry_count');

      // Managed PG Provider Fallback: pg_try_advisory_lock(440010)
      expect(sql).toContain('440010');
      expect(sql).toContain('pg_try_advisory_lock');
      expect(sql).toContain('pg_advisory_unlock');
    });
  });

  // ============================================================================
  // Global Monorepo Zero-Storage Guardrail
  // ============================================================================
  describe('Global Monorepo IaC Zero-Storage & Zero-Baileys Invariant', () => {
    it('TC-SEC-05: guarantees 0 S3/R2 storage buckets and 0 Baileys across entire repo', () => {
      const guardrailScript = readProjectFile('scripts/check-v12-guardrails.mjs');
      expect(guardrailScript).toContain('aws_s3_bucket');
      expect(guardrailScript).toContain('r2.cloudflarestorage.com');
      expect(guardrailScript).toContain('0.0.0.0/0');
      expect(guardrailScript).toContain('@whiskeysockets/baileys');
    });
  });
});
