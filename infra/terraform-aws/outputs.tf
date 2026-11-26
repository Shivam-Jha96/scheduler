# Outputs for Enterprise AWS Terraform Profile

output "vpc_id" {
  description = "The ID of the SchedulerBot VPC"
  value       = aws_vpc.main.id
}

output "alb_dns_name" {
  description = "Public DNS hostname of the Application Load Balancer"
  value       = aws_lb.ingress.dns_name
}

output "webhook_ingress_url" {
  description = "Canonical WhatsApp Webhook ingress URL endpoint"
  value       = "https://${aws_lb.ingress.dns_name}/webhooks/whatsapp"
}

output "kms_key_arn" {
  description = "ARN of the Customer Managed Key (CMK) for envelope encryption"
  value       = aws_kms_key.scheduler_dek.arn
}

output "kms_key_alias" {
  description = "Alias name for the Customer Managed Key"
  value       = aws_kms_alias.scheduler_dek.name
}

output "rds_cluster_endpoint" {
  description = "Aurora PostgreSQL 16 cluster writer endpoint"
  value       = aws_rds_cluster.postgres16.endpoint
}

output "cloudwatch_log_retention_days" {
  description = "Retention period for all CloudWatch log groups in days (strictly 30 days per BR-05)"
  value       = var.log_retention_days
}
