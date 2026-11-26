terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project   = "SchedulerBot"
      Model     = "Model-C-v4.4-HYBRID"
      Milestone = "M1"
      Epic      = "EPIC-14"
      ManagedBy = "Terraform"
    }
  }
}
