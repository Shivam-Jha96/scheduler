# RDS Aurora PostgreSQL 16 Cluster with pg_cron support (EP14-T2)

resource "aws_rds_cluster_parameter_group" "pg16_cron" {
  name        = "schedulerbot-pg16-cron-params"
  family      = "aurora-postgresql16"
  description = "Cluster parameter group enabling pg_cron and SSL for PostgreSQL 16"

  parameter {
    name         = "shared_preload_libraries"
    value        = "pg_cron"
    apply_method = "pending-reboot"
  }

  parameter {
    name         = "cron.database_name"
    value        = var.db_name
    apply_method = "pending-reboot"
  }

  parameter {
    name         = "rds.force_ssl"
    value        = "1"
    apply_method = "immediate"
  }

  tags = {
    Name = "schedulerbot-pg16-cron-params"
  }
}

resource "aws_rds_cluster" "postgres16" {
  cluster_identifier              = "schedulerbot-pg16-cluster"
  engine                          = "aurora-postgresql"
  engine_version                  = "16.4"
  database_name                   = var.db_name
  master_username                 = var.db_master_username
  manage_master_user_password     = true
  storage_encrypted               = true
  kms_key_id                      = aws_kms_key.scheduler_dek.arn
  db_cluster_parameter_group_name = aws_rds_cluster_parameter_group.pg16_cron.name
  db_subnet_group_name            = aws_db_subnet_group.rds_subnet_group.name
  vpc_security_group_ids          = [aws_security_group.rds_db.id]
  deletion_protection             = true
  backup_retention_period         = 14
  preferred_backup_window         = "02:00-03:00"
  skip_final_snapshot             = false
  final_snapshot_identifier       = "schedulerbot-pg16-final-snapshot"

  tags = {
    Name = "schedulerbot-pg16-cluster"
  }
}

resource "aws_rds_cluster_instance" "postgres16" {
  count                       = 2
  identifier                  = "schedulerbot-pg16-instance-${count.index + 1}"
  cluster_identifier          = aws_rds_cluster.postgres16.id
  instance_class              = "db.t4g.medium"
  engine                      = aws_rds_cluster.postgres16.engine
  engine_version              = aws_rds_cluster.postgres16.engine_version
  db_subnet_group_name        = aws_db_subnet_group.rds_subnet_group.name
  auto_minor_version_upgrade  = true

  tags = {
    Name = "schedulerbot-pg16-instance-${count.index + 1}"
  }
}
