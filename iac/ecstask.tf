resource "aws_ecr_repository" "c23_epipelagic_ecr_dynamo" {
  name                 = "c${var.COHORT_NUMBER}-epipelagic-ecr-dynamo"
  image_tag_mutability = "MUTABLE"
  force_delete = true
  image_scanning_configuration {
    scan_on_push = false
  }
}

resource "aws_ecr_repository" "c23_epipelagic_ecr_etl" {
  name                 = "c${var.COHORT_NUMBER}-epipelagic-ecr-etl"
  image_tag_mutability = "MUTABLE"
  force_delete = true
  image_scanning_configuration {
    scan_on_push = false
  }
}

resource "aws_ecr_repository" "c23_epipelagic_ecr_dashboard" {
  name                 = "c${var.COHORT_NUMBER}-epipelagic-ecr-dashboard"
  image_tag_mutability = "MUTABLE"
  force_delete = true
  image_scanning_configuration {
    scan_on_push = false
  }
}

data "aws_ecs_cluster" "cohort_cluster" {
  cluster_name = "c${var.COHORT_NUMBER}-ecs-cluster"
}

data "aws_vpc" "cohort_vpc" {
  filter {
    name   = "tag:Name"
    values = ["c${var.COHORT_NUMBER}-VPC"]
  }
}

data "aws_subnets" "public_subnets" {
    
    filter {
        name   = "vpc-id"
        values = [data.aws_vpc.cohort_vpc.id]
    }

    filter {
        name = "tag:Name"
        values = [
            "c${var.COHORT_NUMBER}-public-subnet-*"
        ]
    }
}

resource "null_resource" "dummy_image" {
  provisioner "local-exec" {
    command = <<EOF
      aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin ${aws_ecr_repository.c23_epipelagic_ecr_dynamo.repository_url}
      docker pull public.ecr.aws/lambda/provided:al2023
      docker tag public.ecr.aws/lambda/provided:al2023 ${aws_ecr_repository.c23_epipelagic_ecr_dynamo.repository_url}:latest
      docker push ${aws_ecr_repository.c23_epipelagic_ecr_dynamo.repository_url}:latest
    EOF
  }

  depends_on = [aws_ecr_repository.c23_epipelagic_ecr_dynamo]
}

resource "aws_iam_role" "c23_epipelagic_etl_role" {
  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = ["ecs-tasks.amazonaws.com"] # Allow both ECS and EventBridge to assume this role
        }
      },
    ]
  })
}

resource "aws_iam_role" "c23_epipelagic_dashboard_role" {

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_security_group" "c23_epipelagic_etl_sg" {
  name        = "c${var.COHORT_NUMBER}-epipelagic-etl-sg"
  description = "Security group for ETL ECS tasks"
  vpc_id      = data.aws_vpc.cohort_vpc.id
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

data "aws_iam_policy_document" "etl_task_policy_doc" {
  statement {
    sid    = "AllowPutItemDynamoDB"
    effect = "Allow"
    actions = [
      "dynamodb:PutItem"
    ]
    resources = [aws_dynamodb_table.c23_epipelagic_public_figures.arn]
  }
}

data "aws_iam_policy_document" "dashboard_task_policy_doc" {
  statement {
    sid    = "AllowReadItemDynamoDB"
    effect = "Allow"
    actions = [
      "dynamodb:GetItem",
      "dynamodb:Query",
      "dynamodb:Scan"
    ]
    resources = [aws_dynamodb_table.c23_epipelagic_public_figures.arn]
  }
}

resource "aws_iam_policy" "c23_epipelagic_dashboard_task_policy" {
    name = "c${var.COHORT_NUMBER}-epipelagic-dashboard-task-policy"
    policy = data.aws_iam_policy_document.dashboard_task_policy_doc.json
}

resource "aws_iam_policy" "c23_epipelagic_etl_task_policy" {
    name = "c${var.COHORT_NUMBER}-epipelagic-etl-task-policy"
    policy = data.aws_iam_policy_document.etl_task_policy_doc.json
}

resource "aws_iam_role_policy_attachment" "etl_task_policy_attachment" {
    role       = aws_iam_role.c23_epipelagic_etl_role.name
    policy_arn = aws_iam_policy.c23_epipelagic_etl_task_policy.arn
}

resource "aws_iam_role_policy_attachment" "dashboard_task_policy_attachment" {
    role       = aws_iam_role.c23_epipelagic_dashboard_role.name
    policy_arn = aws_iam_policy.c23_epipelagic_dashboard_task_policy.arn
}

resource "aws_ecs_task_definition" "c23_epipelagic_etl_task" {
  family                   = "c${var.COHORT_NUMBER}-epipelagic-etl-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  # The execution role handles ECR pulls, secrets, and logging
  execution_role_arn = "arn:aws:iam::129033205317:role/ecsTaskExecutionRole"
  # The task role is what your application code uses
  task_role_arn = aws_iam_role.c23_epipelagic_etl_role.arn

  container_definitions = jsonencode([
    {
      name      = "etl-container"
      image     = "${aws_ecr_repository.c23_epipelagic_ecr_etl.repository_url}:latest"
      essential = true
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/c23-epipelagic-etl-logs"
          "awslogs-region"        = var.REGION
          "awslogs-stream-prefix" = "etl"
        }
      }
    }
  ])
}

resource "aws_ecs_task_definition" "c23_epipelagic_dashboard_task" {
  family                   = "c${var.COHORT_NUMBER}-epipelagic-dashboard-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  # The execution role handles ECR pulls, secrets, and logging
  execution_role_arn = "arn:aws:iam::129033205317:role/ecsTaskExecutionRole"
  # The task role is what your application code uses
  task_role_arn = aws_iam_role.c23_epipelagic_dashboard_role.arn


  container_definitions = jsonencode([
    {
      name      = "dashboard-container"
      image     = "${aws_ecr_repository.c23_epipelagic_ecr_dashboard.repository_url}:latest"
      essential = true
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/c${var.COHORT_NUMBER}-epipelagic-dashboard-logs"
          "awslogs-region"        = var.REGION
          "awslogs-stream-prefix" = "dashboard"
        }
      }
    }
  ])
}