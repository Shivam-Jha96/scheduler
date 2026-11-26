variable "aws_region" {
  type        = string
  description = "AWS deployment region. Ashburn (us-east-1) or Frankfurt (eu-central-1) for < 15ms Meta Graph API peering (FR-NET-04)."
  default     = "us-east-1"

  validation {
    condition     = contains(["us-east-1", "eu-central-1"], var.aws_region)
    error_message = "aws_region must be either 'us-east-1' (Ashburn Equinix) or 'eu-central-1' (Frankfurt DE-CIX) for sub-15ms Meta Graph API regional peering."
  }
}

variable "environment" {
  type        = string
  description = "Deployment environment (staging or production)."
  default     = "production"

  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "environment must be either 'staging' or 'production'."
  }
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the dedicated SchedulerBot VPC."
  default     = "10.44.0.0/16"
}

variable "availability_zones" {
  type        = list(string)
  description = "Availability zones for multi-AZ high availability deployment."
  default     = ["us-east-1a", "us-east-1b"]
}

variable "db_name" {
  type        = string
  description = "Database name for the Aurora PostgreSQL 16 cluster."
  default     = "scheduler_db"
}

variable "db_master_username" {
  type        = string
  description = "Master username for Aurora PostgreSQL."
  default     = "scheduler"
}

variable "acm_certificate_arn" {
  type        = string
  description = "ACM Certificate ARN for HTTPS ALB termination (optional in non-prod)."
  default     = ""
}

variable "api_image" {
  type        = string
  description = "Container image for the stateless Fastify API Gateway."
  default     = "schedulerbot/api-gateway:latest"
}

variable "worker_image" {
  type        = string
  description = "Container image for the delivery worker service."
  default     = "schedulerbot/delivery-worker:latest"
}

variable "log_retention_days" {
  type        = number
  description = "CloudWatch log retention in days. Strictly enforced to 30 days per Tier-3 BR-05 ephemeral model."
  default     = 30

  validation {
    condition     = var.log_retention_days == 30
    error_message = "log_retention_days must be strictly 30 per Tier-3 BR-05 ephemeral retention requirements."
  }
}
