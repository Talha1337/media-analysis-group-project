resource "aws_iam_policy" "c23_epipelagic_lambda_policy" {
    name = "c23-epipelagic-lambda-policy"
    policy = data.aws_iam_policy_document.lambda_role_doc.json
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
    role       = aws_iam_role.c23_epipelagic_lambda_role.name
    policy_arn = aws_iam_policy.c23_epipelagic_lambda_policy.arn
}

resource "aws_iam_role" "c23_epipelagic_lambda_role" {
  name = "c23-epipelagic-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

data "aws_iam_policy_document" "lambda_role_doc" {
  statement {
    sid    = "LambdaBasicExecution"
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }
  statement {
    sid = "AllowECS"
    effect = "Allow"
    actions = [
      "ecs:RunTask",
      "ecs:StopTask",
      "ecs:DescribeTasks"
    ]
    resources = ["*"]
  }
  statement {
    sid = "AllowDynamoDBQuery"
    effect = "Allow"
    actions = [
      "dynamodb:Query"
    ]
    resources = ["*"]
  }
}

# 1. Look up the latest image metadata from ECR
data "aws_ecr_image" "latest_image" {
  repository_name = aws_ecr_repository.c23_epipelagic_ecr_dynamo.name # Your repo name
  image_tag       = "latest"
}


resource "aws_lambda_function" "c23_epipelagic_container_function" {
  function_name = "c23-epipelagic-container-function"
  role          = aws_iam_role.c23_epipelagic_lambda_role.arn
  package_type  = "Image"
  image_uri     = data.aws_ecr_image.latest_image.image_uri

  memory_size = 512
  timeout     = 30

  depends_on = [null_resource.dummy_image] # Ensure image is pushed before Lambda creation
}
# terraform apply -replace="aws_lambda_function.c23_epipelagic_container_function" to force Lambda update after image push

resource "aws_lambda_permission" "c23_api_gateway_invoke_permission" {
  statement_id  = "8e6fccfe-16a0-5e6f-abcf-8017e459fcaf"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.c23_epipelagic_container_function.arn
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.c23_epipelagic_http_api.execution_arn}/*/*/"
}
output "lambda_function_name" {
  value = aws_lambda_function.c23_epipelagic_container_function.arn
}

output "source_arn_api_http_execution" {
  value = aws_apigatewayv2_api.c23_epipelagic_http_api.execution_arn
}