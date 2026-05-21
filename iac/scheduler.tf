resource "aws_scheduler_schedule" "c23_epipelagic_etl_schedule" {
  name = "c${var.COHORT_NUMBER}-epipelagic-etl-schedule"
  schedule_expression = "cron(*/15 * * * ? *)" # Every 15 minutes
  flexible_time_window {
    mode = "OFF"
  }
  target {
    arn = data.aws_ecs_cluster.cohort_cluster.arn
    role_arn = aws_iam_role.c23_epipelagic_etl_role.arn
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