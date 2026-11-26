# ECS Fargate Cluster, Task Definitions, and Services (FR-NET-01, FR-NET-02)

resource "aws_ecs_cluster" "scheduler" {
  name = "schedulerbot-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name = "schedulerbot-cluster"
  }
}

# IAM Execution Role for Fargate task pulling and logging
resource "aws_iam_role" "ecs_execution_role" {
  name = "schedulerbot-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "schedulerbot-ecs-execution-role"
  }
}

resource "aws_iam_role_policy_attachment" "ecs_execution_standard" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# IAM Policy for Execution Role to decrypt secrets with KMS
resource "aws_iam_policy" "ecs_execution_kms" {
  name        = "schedulerbot-execution-kms-policy"
  description = "Allows ECS Execution Role to access KMS key and Secrets Manager"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Resource = [aws_kms_key.scheduler_dek.arn]
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = ["*"]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_kms_attach" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = aws_iam_policy.ecs_execution_kms.policy_arn
}

# IAM Task Role for application containers (KMS Envelope Crypto and ECS Exec)
resource "aws_iam_role" "ecs_task_role" {
  name = "schedulerbot-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "schedulerbot-ecs-task-role"
  }
}

# Task Role Policy: KMS Envelope Encryption (EPIC-13) and SSM Session Manager Exec (FR-NET-02)
resource "aws_iam_policy" "ecs_task_policy" {
  name        = "schedulerbot-ecs-task-policy"
  description = "Permissions for ECS tasks: KMS envelope encryption and SSM Exec"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "EnvelopeEncryption"
        Effect = "Allow"
        Action = [
          "kms:GenerateDataKey",
          "kms:Decrypt",
          "kms:Encrypt",
          "kms:DescribeKey"
        ]
        Resource = [aws_kms_key.scheduler_dek.arn]
      },
      {
        Sid    = "ECSExecSSMMessages"
        Effect = "Allow"
        Action = [
          "ssmmessages:CreateControlChannel",
          "ssmmessages:CreateDataChannel",
          "ssmmessages:OpenControlChannel",
          "ssmmessages:OpenDataChannel"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_policy_attach" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.ecs_task_policy.policy_arn
}

# 1. API Gateway Task Definition
resource "aws_ecs_task_definition" "api_gateway" {
  family                   = "schedulerbot-api-gateway"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "api-gateway"
      image     = var.api_image
      essential = true

      portMappings = [
        {
          containerPort = 3000
          hostPort      = 3000
          protocol      = "tcp"
        }
      ]

      environment = [
        { name = "NODE_ENV", value = var.environment },
        { name = "PORT", value = "3000" },
        { name = "META_GRAPH_API_VERSION", value = "v22.0" },
        { name = "KMS_KEY_ID", value = "alias/schedulerbot-dek" },
        { name = "DATABASE_URL", value = "postgresql://${var.db_master_username}@${aws_rds_cluster.postgres16.endpoint}:5432/${var.db_name}?sslmode=require" }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.api_gateway.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "api-gateway"
        }
      }
    }
  ])

  tags = {
    Name = "schedulerbot-api-gateway-task"
  }
}

# 2. Delivery Worker Task Definition
resource "aws_ecs_task_definition" "delivery_worker" {
  family                   = "schedulerbot-delivery-worker"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "delivery-worker"
      image     = var.worker_image
      essential = true

      environment = [
        { name = "NODE_ENV", value = var.environment },
        { name = "META_GRAPH_API_VERSION", value = "v22.0" },
        { name = "KMS_KEY_ID", value = "alias/schedulerbot-dek" },
        { name = "DATABASE_URL", value = "postgresql://${var.db_master_username}@${aws_rds_cluster.postgres16.endpoint}:5432/${var.db_name}?sslmode=require" }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.delivery_worker.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "delivery-worker"
        }
      }
    }
  ])

  tags = {
    Name = "schedulerbot-delivery-worker-task"
  }
}

# 3. API Gateway Service (Private subnets, behind ALB, no public IP)
resource "aws_ecs_service" "api_gateway" {
  name                   = "schedulerbot-api-gateway"
  cluster                = aws_ecs_cluster.scheduler.id
  task_definition        = aws_ecs_task_definition.api_gateway.arn
  desired_count          = 2
  launch_type            = "FARGATE"
  enable_execute_command = true

  network_configuration {
    subnets          = aws_subnet.private_app[*].id
    security_groups  = [aws_security_group.ecs_app.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api_gateway.arn
    container_name   = "api-gateway"
    container_port   = 3000
  }

  tags = {
    Name = "schedulerbot-api-gateway-service"
  }
}

# 4. Delivery Worker Service (Private subnets, background worker, no public IP)
resource "aws_ecs_service" "delivery_worker" {
  name                   = "schedulerbot-delivery-worker"
  cluster                = aws_ecs_cluster.scheduler.id
  task_definition        = aws_ecs_task_definition.delivery_worker.arn
  desired_count          = 2
  launch_type            = "FARGATE"
  enable_execute_command = true

  network_configuration {
    subnets          = aws_subnet.private_app[*].id
    security_groups  = [aws_security_group.ecs_app.id]
    assign_public_ip = false
  }

  tags = {
    Name = "schedulerbot-delivery-worker-service"
  }
}
