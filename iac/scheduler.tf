resource "aws_iam_role" "c23_epipelagic_scheduler_role" {
  name = "c${var.COHORT_NUMBER}-epipelagic-scheduler-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = ["scheduler.amazonaws.com"] # Allow both ECS and EventBridge to assume this role
        }
       },
       {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = ["ecs-tasks.amazonaws.com"] # Allow both ECS and EventBridge to assume this role
        }
       },
    ]
  })
}

data "aws_iam_policy_document" "scheduler_policy_doc" {
  statement {
    sid    = "AllowRunTaskECS"
    effect = "Allow"
    actions = [
      "ecs:RunTask",
      "ecs:StopTask",
      "ecs:DescribeTasks",
      "iam:PassRole"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "c23_epipelagic_scheduler_policy" {
    name = "c${var.COHORT_NUMBER}-epipelagic-scheduler-policy"
    policy = data.aws_iam_policy_document.scheduler_policy_doc.json
}

resource "aws_iam_role_policy_attachment" "scheduler_policy_attachment" {
    role       = aws_iam_role.c23_epipelagic_scheduler_role.name
    policy_arn = aws_iam_policy.c23_epipelagic_scheduler_policy.arn
}


resource "aws_scheduler_schedule" "c23_epipelagic_etl_schedule" {
  name = "c${var.COHORT_NUMBER}-epipelagic-etl-schedule"
  schedule_expression = "cron(*/15 * * * ? *)" # Every 15 minutes
  flexible_time_window {
    mode = "OFF"
  }
  target {
    arn = data.aws_ecs_cluster.cohort_cluster.arn
    role_arn = aws_iam_role.c23_epipelagic_scheduler_role.arn
    ecs_parameters {
        task_definition_arn = aws_ecs_task_definition.c23_epipelagic_etl_task.arn
        launch_type = "FARGATE"
        network_configuration {
            security_groups = [aws_security_group.c23_epipelagic_etl_sg.id]
            subnets = data.aws_subnets.public_subnets.ids
            assign_public_ip = true
        }
    }
  }
}