aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin ${ecr_repository_dashboard_url}
docker build -t c23-epipelagic-ecr-dashboard --provenance=false --platform="linux/amd64" .
docker tag c23-epipelagic-ecr-dashboard:latest ${ecr_repository_dashboard_url}:latest
docker push ${ecr_repository_dashboard_url}:latest