# Bastion-Free Administrative Access via AWS Systems Manager Session Manager (FR-NET-02)

# VPC Interface Endpoints for SSM, SSMMessages, EC2Messages, and KMS in Private App Subnets
resource "aws_vpc_endpoint" "ssm" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.ssm"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private_app[*].id
  security_group_ids  = [aws_security_group.ssm_endpoints.id]
  private_dns_enabled = true

  tags = {
    Name = "schedulerbot-ssm-endpoint"
  }
}

resource "aws_vpc_endpoint" "ssmmessages" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.ssmmessages"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private_app[*].id
  security_group_ids  = [aws_security_group.ssm_endpoints.id]
  private_dns_enabled = true

  tags = {
    Name = "schedulerbot-ssmmessages-endpoint"
  }
}

resource "aws_vpc_endpoint" "ec2messages" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.ec2messages"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private_app[*].id
  security_group_ids  = [aws_security_group.ssm_endpoints.id]
  private_dns_enabled = true

  tags = {
    Name = "schedulerbot-ec2messages-endpoint"
  }
}

resource "aws_vpc_endpoint" "kms" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.kms"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private_app[*].id
  security_group_ids  = [aws_security_group.ssm_endpoints.id]
  private_dns_enabled = true

  tags = {
    Name = "schedulerbot-kms-endpoint"
  }
}

# SSM Document configuring Session Manager preferences (KMS encrypted and CloudWatch logged)
resource "aws_ssm_document" "session_preferences" {
  name          = "SSM-SessionManagerRunShell"
  document_type = "Session"
  document_format = "JSON"

  content = jsonencode({
    schemaVersion = "1.0"
    description   = "Enforces KMS encryption and CloudWatch logging for SSM sessions"
    sessionType   = "Standard_Stream"
    inputs = {
      s3BucketName                = ""
      s3KeyPrefix                 = ""
      s3EncryptionEnabled         = false
      cloudWatchLogGroupName      = aws_cloudwatch_log_group.ssm_sessions.name
      cloudWatchEncryptionEnabled = true
      kmsKeyId                    = aws_kms_key.scheduler_dek.arn
      runAsEnabled                = false
    }
  })

  tags = {
    Name = "schedulerbot-ssm-session-preferences"
  }
}
