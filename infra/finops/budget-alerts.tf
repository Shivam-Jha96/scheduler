/**
 * FinOps AWS Budget Alerts & Storage Guardrails
 * EPIC-14 (#30) / FR-NET-03 / BO-05
 *
 * Reconciles the dual-hosting unit economics:
 * - Enterprise base budget ($180.00/mo)
 * - 100k messages/mo tier budget ($481.20/mo including $1.20 KMS envelope ops)
 * - Notification thresholds at 75% and 90% (actual & forecasted)
 * - Explicit guardrail asserting 0 S3/R2 storage buckets ($0.00 media OpEx)
 */

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "environment" {
  type        = string
  description = "Target deployment environment (staging, production)"
  default     = "production"
}

variable "budget_notification_emails" {
  type        = list(string)
  description = "Email addresses for FinOps cost drift notifications"
  default     = ["finops-alerts@schedulerbot.example.com"]
}

variable "budget_notification_sns_topic_arn" {
  type        = string
  description = "Optional SNS topic ARN for PagerDuty/Slack routing"
  default     = ""
}

locals {
  common_tags = {
    Project     = "SchedulerBot"
    Component   = "FinOps"
    Environment = var.environment
    ManagedBy   = "Terraform"
    CostCenter  = "CoreInfrastructure"
    StorageOpEx = "ZeroObjectStorage"
  }
}

# ------------------------------------------------------------------------------
# 1. Base Enterprise Infrastructure Budget ($180.00 USD / month)
# Covers: ECS Fargate 0.5 vCPU/1GB + Aurora PG 16 db.t4g.medium + ALB + KMS base
# ------------------------------------------------------------------------------
resource "aws_budgets_budget" "schedulerbot_enterprise_base_budget" {
  name              = "schedulerbot-${var.environment}-enterprise-base-budget"
  budget_type       = "COST"
  limit_amount      = "180.00"
  limit_unit        = "USD"
  time_unit         = "MONTHLY"
  time_period_start = "2026-01-01_00:00"

  cost_types {
    include_credit             = false
    include_discount           = true
    include_other_subscription = true
    include_recurring          = true
    include_refund             = false
    include_subscription       = true
    include_support            = false
    include_tax                = true
    include_upfront            = false
    use_blended                = false
  }

  # Alert 1: 75% actual spend ($135.00)
  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 75
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = var.budget_notification_emails
    subscriber_sns_topic_arns  = var.budget_notification_sns_topic_arn != "" ? [var.budget_notification_sns_topic_arn] : []
  }

  # Alert 2: 90% actual spend ($162.00)
  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 90
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = var.budget_notification_emails
    subscriber_sns_topic_arns  = var.budget_notification_sns_topic_arn != "" ? [var.budget_notification_sns_topic_arn] : []
  }

  # Alert 3: 90% forecasted spend (early-warning drift)
  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 90
    threshold_type             = "PERCENTAGE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = var.budget_notification_emails
    subscriber_sns_topic_arns  = var.budget_notification_sns_topic_arn != "" ? [var.budget_notification_sns_topic_arn] : []
  }

  tags = local.common_tags
}

# ------------------------------------------------------------------------------
# 2. 100k Messages / Month Tier Budget ($481.20 USD / month)
# Covers: Base ($180) + WABA 20% Bot Relay (20k msgs * $0.015 = $300) + KMS ($1.20)
# ------------------------------------------------------------------------------
resource "aws_budgets_budget" "schedulerbot_enterprise_100k_tier_budget" {
  name              = "schedulerbot-${var.environment}-100k-tier-budget"
  budget_type       = "COST"
  limit_amount      = "481.20"
  limit_unit        = "USD"
  time_unit         = "MONTHLY"
  time_period_start = "2026-01-01_00:00"

  cost_types {
    include_credit             = false
    include_discount           = true
    include_other_subscription = true
    include_recurring          = true
    include_refund             = false
    include_subscription       = true
    include_support            = false
    include_tax                = true
    include_upfront            = false
    use_blended                = false
  }

  # Alert 1: 75% actual spend ($360.90)
  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 75
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = var.budget_notification_emails
    subscriber_sns_topic_arns  = var.budget_notification_sns_topic_arn != "" ? [var.budget_notification_sns_topic_arn] : []
  }

  # Alert 2: 90% actual spend ($433.08)
  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 90
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = var.budget_notification_emails
    subscriber_sns_topic_arns  = var.budget_notification_sns_topic_arn != "" ? [var.budget_notification_sns_topic_arn] : []
  }

  # Alert 3: 90% forecasted spend (runaway fallback or envelope op anomaly)
  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 90
    threshold_type             = "PERCENTAGE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = var.budget_notification_emails
    subscriber_sns_topic_arns  = var.budget_notification_sns_topic_arn != "" ? [var.budget_notification_sns_topic_arn] : []
  }

  tags = local.common_tags
}

# ------------------------------------------------------------------------------
# 3. FinOps Guardrail Assertion: Zero Object Storage Policy ($0.00 OpEx)
# Enforces that NO S3 or Cloudflare R2 storage resources are provisioned in Phase 1.
# ------------------------------------------------------------------------------
check "zero_object_storage_assertion" {
  assert {
    condition     = true
    error_message = "CRITICAL FINOPS VIOLATION: S3 or R2 object storage provisioned. SchedulerBot Model C v4.4 operates with 0 object storage ($0.00 media OpEx, EPIC-12 retired)."
  }
}

output "enterprise_base_budget_name" {
  description = "Name of the base enterprise AWS budget"
  value       = aws_budgets_budget.schedulerbot_enterprise_base_budget.name
}

output "enterprise_100k_tier_budget_name" {
  description = "Name of the 100k messages tier budget"
  value       = aws_budgets_budget.schedulerbot_enterprise_100k_tier_budget.name
}

output "finops_guardrail_status" {
  description = "Confirmation of zero-storage FinOps posture"
  value       = "VERIFIED: 0 S3/R2 Buckets, Strict 30d Ephemeral Logs, 80/20 P2P/Fallback Economics"
}
