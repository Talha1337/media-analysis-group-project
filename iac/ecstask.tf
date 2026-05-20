resource "aws_ecr_repository" "c23_epipelagic_ecr_dynamo" {
  name                 = "c23-epipelagic-ecr-dynamo"
  image_tag_mutability = "MUTABLE"
  force_delete = true
  image_scanning_configuration {
    scan_on_push = false
  }
}

resource "null_resource" "dummy_image" {
  provisioner "local-exec" {
    command = <<EOF
      aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${aws_ecr_repository.c23_epipelagic_ecr_dynamo.repository_url}
      docker pull public.ecr.aws/lambda/provided:al2023
      docker tag public.ecr.aws/lambda/provided:al2023 ${aws_ecr_repository.c23_epipelagic_ecr_dynamo.repository_url}:latest
      docker push ${aws_ecr_repository.c23_epipelagic_ecr_dynamo.repository_url}:latest
    EOF
  }

  depends_on = [aws_ecr_repository.c23_epipelagic_ecr_dynamo]
}