resource "aws_apigatewayv2_api" "c23_epipelagic_http_api" {
  name          = "c23-epipelagic-http-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "c23_epipelagic_lambda_integration" {
  api_id             = aws_apigatewayv2_api.c23_epipelagic_http_api.id
  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.c23_epipelagic_container_function.invoke_arn
  integration_method = "POST"
}