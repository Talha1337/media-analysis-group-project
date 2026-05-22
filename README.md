# Media Outlets Group Project

## Description

Group Project 1 (Week 13): Media Outlets for Otranto Development

## Contributors

Members of the _Otranto Development Team_ (Cohort 23):

- **Project Manager:** Carolina Guevara
- **Quality Assurance:** Kacper Likus
- **Architect:** Talha Javed
- **Data Engineers & Analysts:** Everyone

##  Setup

### Infrastructure

Terraform is used to set up and provision resources. In the `iac` directory, use `terraform apply` to begin this process. You will need to define the following variables to run this (in a `.tfvars` file):

- REGION
- AWS_KEY
- AWS_SECRET_KEY
- COHORT_NUMBER

###  Pushing images

The API, dashboard and pipeline are all run on the cloud infrastructure. There are appropriate deploy scripts for each of these in their respective folders to allow for pushing to ECR e.g. `./deploy_dashboard.sh`. You may need to do `chmod +x [script name]` prior to this to ensure that the shell script can be executed.

## Usage

### Deployment Scripts

[I'll add a bit about this soon.]

### ETL Pipeline

One can run `pipeline/pipeline.py` to extract RSS feed data, transforming it to enrich with public figures, sentiment analysis and keywords, to finally load this on to a DynamoDB table.

### Dashboard

[This](18.175.238.37:8501) displays a dashboard for Streamlit, where one can look up any particular person, given their **normalised name** (donald_trump rather than Donald Trump). This will visualise sentiments for their different articles, as well as list out the keywords and articles found for the specific public figure.

### API

The API takes in a GET request `[endpoint]?name=[normalised_name]` in order to look up the number of articles written about a particular figure, as well as the average sentiment of the person. 

