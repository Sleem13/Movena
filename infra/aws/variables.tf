variable "aws_region" {
  description = "AWS region for regional services. CloudFront remains global."
  type        = string
  default     = "eu-central-1"
}

variable "environment" {
  description = "Deployment environment. Start with staging until SES and the public domain are approved."
  type        = string
  default     = "staging"

  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "environment must be staging or production."
  }
}

variable "app_version" {
  type    = string
  default = "1.0.0"
}

variable "backend_image" {
  description = "Immutable ECR image URI produced by deploy.ps1."
  type        = string
  default     = "public.ecr.aws/docker/library/python:3.12-slim"
}

variable "app_secret_arn" {
  description = "Secrets Manager JSON secret containing SECRET_KEY and protected administrator fields."
  type        = string
  sensitive   = true
}

variable "email_delivery_mode" {
  type    = string
  default = "console"

  validation {
    condition     = contains(["console", "smtp"], var.email_delivery_mode)
    error_message = "email_delivery_mode must be console or smtp."
  }
}

variable "email_from" {
  type    = string
  default = "no-reply@movena.local"
}

variable "smtp_host" {
  type    = string
  default = ""
}

variable "smtp_port" {
  type    = number
  default = 587
}

variable "seed_super_admin" {
  type    = bool
  default = true
}

variable "db_instance_class" {
  type    = string
  default = "db.t4g.micro"
}

variable "ecs_cpu" {
  description = "Fargate CPU units. Video pose processing starts at 2 vCPU."
  type        = number
  default     = 2048
}

variable "ecs_memory" {
  description = "Fargate memory in MiB."
  type        = number
  default     = 4096
}

variable "desired_count" {
  type    = number
  default = 1
}

variable "enable_staging_schedule" {
  description = "Suspend staging compute and database resources outside weekday working hours."
  type        = bool
  default     = true
}

variable "staging_schedule_timezone" {
  description = "IANA timezone used by the staging cost-control schedules."
  type        = string
  default     = "Africa/Cairo"
}

variable "artifact_retention_hours" {
  type    = number
  default = 24
}

variable "protect_data" {
  description = "Enable deletion protection and final snapshots for persistent services."
  type        = bool
  default     = true
}
