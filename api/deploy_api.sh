aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin ${ecr_repository_api_url}
docker build -t c23-epipelagic-ecr-api --provenance=false --platform="linux/amd64" .
docker tag c23-epipelagic-ecr-api:latest ${ecr_repository_api_url}:latest
docker push ${ecr_repository_api_url}:latest