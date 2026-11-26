# Customer Managed Key (CMK) for Envelope Encryption (EPIC-13, EPIC-14)

data "aws_caller_identity" "current" {}

resource "aws_kms_key" "scheduler_dek" {
  description             = "Customer Managed Key (CMK) for SchedulerBot Envelope Encryption"
  key_usage               = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  enable_key_rotation     = true
  deletion_window_in_days = 30

  policy = jsonencode({
    Version = "2012-10-17"
    Id      = "schedulerbot-kms-policy"
    Statement = [
      {
        Sid    = "EnableRootPermissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "AllowECSTasksEnvelopeCrypto"
        Effect = "Allow"
        Principal = {
          AWS = [
            aws_iam_role.ecs_task_role.arn,
            aws_iam_role.ecs_execution_role.arn
          ]
        }
        Action = [
          "kms:GenerateDataKey",
          "kms:Decrypt",
          "kms:Encrypt",
          "kms:DescribeKey"
        ]
        Resource = "*"
      },
      {
        Sid    = "AllowCloudWatchLogsEncryption"
        Effect = "Allow"
        Principal = {
          Service = "logs.${var.aws_region}.amazonaws.com"
        }
        Action = [
          "kms:Encrypt*",
          "kms:Decrypt*",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:Describe*"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Name = "schedulerbot-dek-cmk"
  }
}

resource "aws_kms_alias" "scheduler_dek" {
  name          = "alias/schedulerbot-dek"
  target_key_id = aws_kms_key.scheduler_dek.key_id
}
