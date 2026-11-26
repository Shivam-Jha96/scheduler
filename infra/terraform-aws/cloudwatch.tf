# Tier 3 CloudWatch Log Retention (Strictly 30 Days per BR-05, EP14-T3)

resource "aws_cloudwatch_log_group" "api_gateway" {
  name              = "/schedulerbot/api-gateway"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.scheduler_dek.arn

  tags = {
    Name      = "schedulerbot-api-gateway-logs"
    Retention = "30-days"
    Tier      = "Tier-3-Ephemeral"
  }
}

resource "aws_cloudwatch_log_group" "delivery_worker" {
  name              = "/schedulerbot/delivery-worker"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.scheduler_dek.arn

  tags = {
    Name      = "schedulerbot-delivery-worker-logs"
    Retention = "30-days"
    Tier      = "Tier-3-Ephemeral"
  }
}

resource "aws_cloudwatch_log_group" "ssm_sessions" {
  name              = "/schedulerbot/ssm-sessions"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.scheduler_dek.arn

  tags = {
    Name      = "schedulerbot-ssm-sessions-logs"
    Retention = "30-days"
    Tier      = "Tier-3-Ephemeral"
  }
}
