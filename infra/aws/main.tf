data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_ec2_managed_prefix_list" "cloudfront" {
  name = "com.amazonaws.global.cloudfront.origin-facing"
}

data "aws_cloudfront_cache_policy" "optimized" {
  name = "Managed-CachingOptimized"
}

data "aws_cloudfront_cache_policy" "disabled" {
  name = "Managed-CachingDisabled"
}

data "aws_cloudfront_origin_request_policy" "all_viewer_except_host" {
  name = "Managed-AllViewerExceptHostHeader"
}

locals {
  name         = "physiovision-${var.environment}"
  frontend_url = "https://${aws_cloudfront_distribution.app.domain_name}"
  selected_azs = slice(data.aws_availability_zones.available.names, 0, 2)
  common_environment = concat([
    { name = "ANALYSIS_JOB_MAX_CONCURRENCY", value = "1" },
    { name = "APP_ENV", value = var.environment },
    { name = "APP_VERSION", value = var.app_version },
    { name = "API_HOST", value = "0.0.0.0" },
    { name = "API_PORT", value = "8000" },
    { name = "DATABASE_HOST", value = aws_db_instance.database.address },
    { name = "DATABASE_PORT", value = tostring(aws_db_instance.database.port) },
    { name = "DATABASE_NAME", value = aws_db_instance.database.db_name },
    { name = "CORS_ALLOWED_ORIGINS", value = local.frontend_url },
    { name = "FRONTEND_URL", value = local.frontend_url },
    { name = "REQUIRE_AUTH_FOR_ANALYSIS", value = "true" },
    { name = "ENABLE_PUBLIC_DEMO_MODE", value = "false" },
    { name = "ENABLE_SESSION_HISTORY", value = "true" },
    { name = "ENABLE_THERAPIST_DASHBOARD", value = "true" },
    { name = "ENABLE_REPORT_GENERATION", value = "true" },
    { name = "ENABLE_OVERLAY_GENERATION", value = "true" },
    { name = "ENABLE_ML_SECOND_OPINION", value = "false" },
    { name = "ENABLE_EXERCISE_RECOGNITION", value = "true" },
    { name = "ACTIVE_SEQUENCE_RECOGNITION_MODEL_ID", value = "disabled" },
    { name = "ACTIVE_FRAME_RECOGNITION_MODEL_ID", value = "exercise_pose_xgb_20260809T154328Z" },
    { name = "ENABLE_SUBJECT_CONTINUITY_GUARD", value = "true" },
    { name = "SEED_SUPER_ADMIN_ON_START", value = tostring(var.seed_super_admin) },
    { name = "EMAIL_DELIVERY_MODE", value = var.email_delivery_mode },
    { name = "REQUIRE_EMAIL_VERIFICATION", value = "false" },
    { name = "EMAIL_FROM", value = var.email_from },
    { name = "SMTP_HOST", value = var.smtp_host },
    { name = "SMTP_PORT", value = tostring(var.smtp_port) },
    { name = "SMTP_USE_TLS", value = "true" },
    { name = "MAX_UPLOAD_SIZE_MB", value = "100" },
    { name = "ARTIFACT_RETENTION_HOURS", value = tostring(var.artifact_retention_hours) },
    { name = "POSE_TARGET_FPS", value = "12" },
    ], var.environment == "staging" ? [
    { name = "CLINICAL_ORGANIZATION_NAME", value = "PhysioVision AI staging" },
    { name = "CLINICAL_ESCALATION_CONTACT", value = "Your assigned clinician or local emergency services" },
    { name = "CLINICAL_ESCALATION_INSTRUCTION", value = "This staging service is not monitored for emergencies. Stop and contact your assigned clinician or local emergency services." },
  ] : [])
  base_secrets = [
    { name = "SECRET_KEY", valueFrom = "${var.app_secret_arn}:SECRET_KEY::" },
    { name = "DATABASE_USER", valueFrom = "${aws_db_instance.database.master_user_secret[0].secret_arn}:username::" },
    { name = "DATABASE_PASSWORD", valueFrom = "${aws_db_instance.database.master_user_secret[0].secret_arn}:password::" },
  ]
  admin_secrets = var.seed_super_admin ? [
    { name = "SUPER_ADMIN_EMAIL", valueFrom = "${var.app_secret_arn}:SUPER_ADMIN_EMAIL::" },
    { name = "SUPER_ADMIN_PASSWORD", valueFrom = "${var.app_secret_arn}:SUPER_ADMIN_PASSWORD::" },
    { name = "SUPER_ADMIN_FULL_NAME", valueFrom = "${var.app_secret_arn}:SUPER_ADMIN_FULL_NAME::" },
  ] : []
  smtp_secrets = var.email_delivery_mode == "smtp" ? [
    { name = "SMTP_USERNAME", valueFrom = "${var.app_secret_arn}:SMTP_USERNAME::" },
    { name = "SMTP_PASSWORD", valueFrom = "${var.app_secret_arn}:SMTP_PASSWORD::" },
  ] : []
}

resource "aws_vpc" "main" {
  cidr_block           = "10.42.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags                 = { Name = "${local.name}-vpc" }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "${local.name}-igw" }
}

resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  availability_zone       = local.selected_azs[count.index]
  cidr_block              = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index)
  map_public_ip_on_launch = true
  tags                    = { Name = "${local.name}-public-${count.index + 1}" }
}

resource "aws_subnet" "database" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  availability_zone = local.selected_azs[count.index]
  cidr_block        = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index + 10)
  tags              = { Name = "${local.name}-database-${count.index + 1}" }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  tags = { Name = "${local.name}-public" }
}

resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_db_subnet_group" "main" {
  name       = local.name
  subnet_ids = aws_subnet.database[*].id
}

resource "aws_security_group" "alb" {
  name        = "${local.name}-alb"
  description = "CloudFront origin traffic only"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    prefix_list_ids = [data.aws_ec2_managed_prefix_list.cloudfront.id]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "ecs" {
  name   = "${local.name}-ecs"
  vpc_id = aws_vpc.main.id
  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "database" {
  name   = "${local.name}-database"
  vpc_id = aws_vpc.main.id
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }
}

resource "aws_security_group" "efs" {
  name   = "${local.name}-efs"
  vpc_id = aws_vpc.main.id
  ingress {
    from_port       = 2049
    to_port         = 2049
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }
}

resource "aws_db_instance" "database" {
  identifier                  = local.name
  engine                      = "postgres"
  engine_version              = "16"
  instance_class              = var.db_instance_class
  allocated_storage           = 20
  max_allocated_storage       = 100
  storage_type                = "gp3"
  storage_encrypted           = true
  db_name                     = "physiovision"
  username                    = "physiovision_admin"
  manage_master_user_password = true
  db_subnet_group_name        = aws_db_subnet_group.main.name
  vpc_security_group_ids      = [aws_security_group.database.id]
  publicly_accessible         = false
  backup_retention_period     = var.environment == "production" ? 14 : 1
  deletion_protection         = var.protect_data
  skip_final_snapshot         = !var.protect_data
  final_snapshot_identifier   = var.protect_data ? "${local.name}-final" : null
  auto_minor_version_upgrade  = true
  apply_immediately           = false
}

resource "aws_efs_file_system" "artifacts" {
  encrypted        = true
  performance_mode = "generalPurpose"
  throughput_mode  = "bursting"
  lifecycle_policy { transition_to_ia = var.environment == "production" ? "AFTER_7_DAYS" : "AFTER_1_DAY" }
  tags = { Name = "${local.name}-artifacts" }
}

resource "aws_efs_mount_target" "artifacts" {
  count           = 2
  file_system_id  = aws_efs_file_system.artifacts.id
  subnet_id       = aws_subnet.public[count.index].id
  security_groups = [aws_security_group.efs.id]
}

resource "aws_efs_access_point" "artifacts" {
  file_system_id = aws_efs_file_system.artifacts.id
  posix_user {
    uid = 1000
    gid = 1000
  }
  root_directory {
    path = "/artifacts"
    creation_info {
      owner_uid   = 1000
      owner_gid   = 1000
      permissions = "0750"
    }
  }
}

resource "aws_ecr_repository" "backend" {
  name                 = "physiovision/backend"
  image_tag_mutability = "IMMUTABLE"
  image_scanning_configuration { scan_on_push = true }
  encryption_configuration { encryption_type = "AES256" }
}

resource "aws_ecr_lifecycle_policy" "backend" {
  repository = aws_ecr_repository.backend.name
  policy     = jsonencode({ rules = [{ rulePriority = 1, description = "Keep only recent immutable images", selection = { tagStatus = "any", countType = "imageCountMoreThan", countNumber = var.environment == "production" ? 15 : 5 }, action = { type = "expire" } }] })
}

resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/${local.name}"
  retention_in_days = var.environment == "production" ? 90 : 7
}

resource "aws_iam_role" "ecs_execution" {
  name               = "${local.name}-ecs-execution"
  assume_role_policy = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Principal = { Service = "ecs-tasks.amazonaws.com" }, Action = "sts:AssumeRole" }] })
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "ecs_secrets" {
  name = "secrets"
  role = aws_iam_role.ecs_execution.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = [var.app_secret_arn, aws_db_instance.database.master_user_secret[0].secret_arn]
    }]
  })
}

resource "aws_iam_role" "ecs_task" {
  name               = "${local.name}-ecs-task"
  assume_role_policy = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Principal = { Service = "ecs-tasks.amazonaws.com" }, Action = "sts:AssumeRole" }] })
}

resource "aws_ecs_cluster" "main" {
  name = local.name
  setting {
    name  = "containerInsights"
    value = var.environment == "production" ? "enabled" : "disabled"
  }
}

resource "aws_lb" "backend" {
  name                       = substr(local.name, 0, 32)
  load_balancer_type         = "application"
  internal                   = false
  security_groups            = [aws_security_group.alb.id]
  subnets                    = aws_subnet.public[*].id
  drop_invalid_header_fields = true
  enable_deletion_protection = var.protect_data
  idle_timeout               = 300
}

resource "aws_lb_target_group" "backend" {
  name                 = substr("${local.name}-api", 0, 32)
  port                 = 8000
  protocol             = "HTTP"
  target_type          = "ip"
  vpc_id               = aws_vpc.main.id
  deregistration_delay = 120
  health_check {
    path                = "/ready"
    matcher             = "200"
    interval            = 30
    timeout             = 10
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.backend.arn
  port              = 80
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }
}

resource "aws_ecs_task_definition" "backend" {
  family                   = local.name
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = tostring(var.ecs_cpu)
  memory                   = tostring(var.ecs_memory)
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  volume {
    name = "artifacts"
    efs_volume_configuration {
      file_system_id     = aws_efs_file_system.artifacts.id
      transit_encryption = "ENABLED"
      authorization_config {
        access_point_id = aws_efs_access_point.artifacts.id
        iam             = "DISABLED"
      }
    }
  }

  container_definitions = jsonencode([{
    name                   = "backend"
    image                  = var.backend_image
    essential              = true
    portMappings           = [{ containerPort = 8000, hostPort = 8000, protocol = "tcp" }]
    environment            = local.common_environment
    secrets                = concat(local.base_secrets, local.admin_secrets, local.smtp_secrets)
    mountPoints            = [{ sourceVolume = "artifacts", containerPath = "/app/backend/artifacts", readOnly = false }]
    readonlyRootFilesystem = false
    linuxParameters        = { initProcessEnabled = true }
    healthCheck            = { command = ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/ready', timeout=4)\" || exit 1"], interval = 30, timeout = 5, retries = 3, startPeriod = 30 }
    logConfiguration       = { logDriver = "awslogs", options = { "awslogs-group" = aws_cloudwatch_log_group.backend.name, "awslogs-region" = var.aws_region, "awslogs-stream-prefix" = "api" } }
  }])
}

resource "aws_ecs_service" "backend" {
  name                               = "backend"
  cluster                            = aws_ecs_cluster.main.id
  task_definition                    = aws_ecs_task_definition.backend.arn
  desired_count                      = var.desired_count
  launch_type                        = "FARGATE"
  platform_version                   = "1.4.0"
  health_check_grace_period_seconds  = 120
  deployment_minimum_healthy_percent = 100
  deployment_maximum_percent         = 200
  enable_execute_command             = true

  network_configuration {
    subnets          = aws_subnet.public[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = true
  }
  load_balancer {
    target_group_arn = aws_lb_target_group.backend.arn
    container_name   = "backend"
    container_port   = 8000
  }
  depends_on = [aws_lb_listener.http, aws_efs_mount_target.artifacts]
}

resource "aws_s3_bucket" "frontend" {
  bucket_prefix = "physiovision-${var.environment}-web-"
}

resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket                  = aws_s3_bucket.frontend.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_lifecycle_configuration" "frontend" {
  bucket     = aws_s3_bucket.frontend.id
  depends_on = [aws_s3_bucket_versioning.frontend]

  rule {
    id     = "remove-stale-deployment-versions"
    status = "Enabled"
    filter {}

    noncurrent_version_expiration {
      noncurrent_days = var.environment == "production" ? 30 : 7
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 1
    }
  }
}

resource "aws_cloudfront_origin_access_control" "frontend" {
  name                              = local.name
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_function" "spa" {
  name    = replace(local.name, "-", "_")
  runtime = "cloudfront-js-2.0"
  code    = <<-JS
    function handler(event) {
      var request = event.request;
      if (request.uri.indexOf('.') === -1 && request.uri.indexOf('/api/') !== 0) request.uri = '/index.html';
      return request;
    }
  JS
}

resource "aws_cloudfront_distribution" "app" {
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  price_class         = "PriceClass_100"
  comment             = local.name

  origin {
    origin_id                = "frontend"
    domain_name              = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.frontend.id
  }
  origin {
    origin_id   = "backend"
    domain_name = aws_lb.backend.dns_name
    custom_origin_config {
      http_port                = 80
      https_port               = 443
      origin_protocol_policy   = "http-only"
      origin_ssl_protocols     = ["TLSv1.2"]
      origin_read_timeout      = 60
      origin_keepalive_timeout = 5
    }
  }

  default_cache_behavior {
    target_origin_id       = "frontend"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD", "OPTIONS"]
    cache_policy_id        = data.aws_cloudfront_cache_policy.optimized.id
    compress               = true
    function_association {
      event_type   = "viewer-request"
      function_arn = aws_cloudfront_function.spa.arn
    }
  }

  ordered_cache_behavior {
    path_pattern             = "/api/*"
    target_origin_id         = "backend"
    viewer_protocol_policy   = "redirect-to-https"
    allowed_methods          = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods           = ["GET", "HEAD", "OPTIONS"]
    cache_policy_id          = data.aws_cloudfront_cache_policy.disabled.id
    origin_request_policy_id = data.aws_cloudfront_origin_request_policy.all_viewer_except_host.id
    compress                 = true
  }

  dynamic "ordered_cache_behavior" {
    for_each = toset(["/health", "/ready"])
    content {
      path_pattern             = ordered_cache_behavior.value
      target_origin_id         = "backend"
      viewer_protocol_policy   = "redirect-to-https"
      allowed_methods          = ["GET", "HEAD", "OPTIONS"]
      cached_methods           = ["GET", "HEAD", "OPTIONS"]
      cache_policy_id          = data.aws_cloudfront_cache_policy.disabled.id
      origin_request_policy_id = data.aws_cloudfront_origin_request_policy.all_viewer_except_host.id
      compress                 = true
    }
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  viewer_certificate {
    cloudfront_default_certificate = true
    minimum_protocol_version       = "TLSv1.2_2021"
  }
}

resource "aws_s3_bucket_policy" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "AllowCloudFrontRead", Effect = "Allow", Principal = { Service = "cloudfront.amazonaws.com" }, Action = "s3:GetObject",
      Resource  = "${aws_s3_bucket.frontend.arn}/*",
      Condition = { StringEquals = { "AWS:SourceArn" = aws_cloudfront_distribution.app.arn } }
    }]
  })
}
