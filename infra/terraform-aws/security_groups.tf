# Security Groups enforcing Zero-Public-Port Ingress (FR-NET-01, FR-NET-02)

# 1. ALB Security Group: Ingress HTTPS 443 only from Internet
resource "aws_security_group" "alb" {
  name        = "schedulerbot-alb-sg"
  description = "Security group for internet-facing Application Load Balancer"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTPS ingress from internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description     = "Forward HTTP traffic to ECS application tasks on port 3000"
    from_port       = 3000
    to_port         = 3000
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_app.id]
  }

  tags = {
    Name = "schedulerbot-alb-sg"
  }
}

# 2. ECS Application Security Group: Strictly private, no public ingress
resource "aws_security_group" "ecs_app" {
  name        = "schedulerbot-ecs-app-sg"
  description = "Security group for private ECS Fargate tasks (API Gateway and Delivery Worker)"
  vpc_id      = aws_vpc.main.id

  # Ingress strictly from ALB on port 3000
  ingress {
    description     = "Ingress strictly from ALB on port 3000"
    from_port       = 3000
    to_port         = 3000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  # Egress to RDS Aurora PostgreSQL 16 on port 5432
  egress {
    description     = "PostgreSQL egress to RDS Aurora cluster"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.rds_db.id]
  }

  # Egress to HTTPS 443 for Meta Graph API v22.0, AWS KMS, and SSM endpoints
  egress {
    description = "Outbound HTTPS for Meta Graph API v22.0, AWS KMS, and SSM"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "schedulerbot-ecs-app-sg"
  }
}

# 3. RDS Aurora PostgreSQL Security Group: Zero 0.0.0.0/0 rules, strictly internal
resource "aws_security_group" "rds_db" {
  name        = "schedulerbot-rds-db-sg"
  description = "Security group for isolated Aurora PostgreSQL 16 cluster"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "PostgreSQL access strictly from ECS Fargate application tasks"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_app.id]
  }

  ingress {
    description     = "PostgreSQL access strictly from SSM VPC Endpoints for bastion-free admin"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ssm_endpoints.id]
  }

  tags = {
    Name = "schedulerbot-rds-db-sg"
  }
}

# 4. SSM VPC Endpoints Security Group: Private TLS access
resource "aws_security_group" "ssm_endpoints" {
  name        = "schedulerbot-ssm-endpoints-sg"
  description = "Security group for AWS Systems Manager and KMS VPC endpoints"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "TLS ingress from VPC CIDR for SSM and KMS endpoints"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  tags = {
    Name = "schedulerbot-ssm-endpoints-sg"
  }
}
