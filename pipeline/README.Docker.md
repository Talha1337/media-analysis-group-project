### Building and running your application

Build the pipeline image from this directory:
`docker build -t mypipeline .`

When you're ready, run the ETL pipeline container:
`docker run --rm mypipeline`

This image runs the CLI pipeline (`python3 pipeline.py`) and does not start an HTTP service.

### Deploying your application to the cloud

First, build your image, e.g.: `docker build -t mypipeline .`.
If your cloud uses a different CPU architecture than your development
machine (e.g., you are on a Mac M1 and your cloud provider is amd64),
you'll want to build the image for that platform, e.g.:
`docker build --platform=linux/amd64 -t mypipeline .`.

Then, push it to your registry, e.g. `docker push myregistry.com/mypipeline`.

Consult Docker's [getting started](https://docs.docker.com/go/get-started-sharing/)
docs for more detail on building and pushing.

### References
* [Docker's Python guide](https://docs.docker.com/language/python/)