aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 129033205317.dkr.ecr.eu-west-2.amazonaws.com
docker build -t c23-epipelagic-ecr-dynamo  --provenance=false --platform="linux/amd64" .
docker tag c23-epipelagic-ecr-dynamo:latest 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c23-epipelagic-ecr-dynamo:latest
docker push 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c23-epipelagic-ecr-dynamo:latest