# Dedicated Multi-AZ VPC for SchedulerBot (FR-NET-01)
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "schedulerbot-vpc-${var.environment}"
  }
}

# Internet Gateway for ALB & NAT Gateway public egress
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "schedulerbot-igw-${var.environment}"
  }
}

# 2x Public Subnets (strictly for ALB and NAT Gateway)
resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index + 1) # 10.44.1.0/24, 10.44.2.0/24
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "schedulerbot-public-subnet-${var.availability_zones[count.index]}"
    Tier = "Public"
  }
}

# 2x Private Application Subnets (for stateless Fastify API & delivery workers)
resource "aws_subnet" "private_app" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index + 11) # 10.44.11.0/24, 10.44.12.0/24
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = false

  tags = {
    Name = "schedulerbot-private-app-subnet-${var.availability_zones[count.index]}"
    Tier = "PrivateApp"
  }
}

# 2x Isolated Database Subnets (for RDS Aurora PG 16 - zero route to internet)
resource "aws_subnet" "isolated_db" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index + 21) # 10.44.21.0/24, 10.44.22.0/24
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = false

  tags = {
    Name = "schedulerbot-isolated-db-subnet-${var.availability_zones[count.index]}"
    Tier = "IsolatedDB"
  }
}

# Elastic IP for NAT Gateway
resource "aws_eip" "nat" {
  domain     = "vpc"
  depends_on = [aws_internet_gateway.igw]

  tags = {
    Name = "schedulerbot-nat-eip-${var.environment}"
  }
}

# NAT Gateway in Public Subnet 0 for outbound Meta Graph API v22.0 calls
resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id
  depends_on    = [aws_internet_gateway.igw]

  tags = {
    Name = "schedulerbot-nat-gw-${var.environment}"
  }
}

# Route Table: Public Subnets (to Internet Gateway)
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "schedulerbot-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Route Table: Private App Subnets (outbound via NAT Gateway)
resource "aws_route_table" "private_app" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat.id
  }

  tags = {
    Name = "schedulerbot-private-app-rt"
  }
}

resource "aws_route_table_association" "private_app" {
  count          = 2
  subnet_id      = aws_subnet.private_app[count.index].id
  route_table_id = aws_route_table.private_app.id
}

# Route Table: Isolated DB Subnets (Strictly internal - zero 0.0.0.0/0 route)
resource "aws_route_table" "isolated_db" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "schedulerbot-isolated-db-rt"
  }
}

resource "aws_route_table_association" "isolated_db" {
  count          = 2
  subnet_id      = aws_subnet.isolated_db[count.index].id
  route_table_id = aws_route_table.isolated_db.id
}

# DB Subnet Group for RDS Aurora
resource "aws_db_subnet_group" "rds_subnet_group" {
  name        = "schedulerbot-db-subnet-group"
  description = "Subnet group for isolated Aurora PostgreSQL 16 cluster"
  subnet_ids  = aws_subnet.isolated_db[*].id

  tags = {
    Name = "schedulerbot-db-subnet-group"
  }
}
