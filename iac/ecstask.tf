resource "aws_ecr_repository" "c23_epipelagic_ecr_dynamo" {
  name                 = "c23-epipelagic-ecr-dynamo"
  image_tag_mutability = "MUTABLE"
  force_delete = true
  image_scanning_configuration {
    scan_on_push = false
  }
}

data "aws_iam_policy_document" "c23_epipelagic_task_role_doc" {
  # First block: Athena
statement {
    sid    = "DynamoDBReadAccess"
    effect = "Allow"
    actions = [
      "dynamodb:GetItem",
      "dynamodb:BatchGetItem",
      "dynamodb:Scan",
      "dynamodb:Query",
      "dynamodb:ConditionCheckItem"
    ]
    resources = ["${aws_dynamodb_table.c23_epipelagic_public_figures.arn}"]
  }
}

# Then you turn that data into an actual policy resource
resource "aws_iam_policy" "c23_epipelagic_task_role_policy" {
  name   = "c23-epipelagic-task-role-policy"
  policy = data.aws_iam_policy_document.c23_epipelagic_task_role_doc.json
}

resource "aws_iam_role" "c23_epipelagic_task_role" {
  name = "c23-epipelagic-task-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "task_role_attachment" {
  role       = aws_iam_role.c23_epipelagic_task_role.name
  policy_arn = aws_iam_policy.c23_epipelagic_task_role_policy.arn
}

resource "aws_ecs_task_definition" "c23_epipelagic_ecs_task" {
  family = "c23-epipelagic-ecs-task"
  requires_compatibilities = ["FARGATE"]
  cpu = 1024
  memory = 2048

  network_mode = "awsvpc"
  task_role_arn = "${aws_iam_role.c23_epipelagic_task_role.arn}"
  execution_role_arn = "arn:aws:iam::129033205317:role/ecsTaskExecutionRole"
  container_definitions = jsonencode([
    {
      name      = "c23-epipelagic-dynamo-container"
      image     = "${aws_ecr_repository.c23_epipelagic_ecr_dynamo.repository_url}:latest"
      essential = true
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
        }
      ]
    }
  ])
}