terraform {
  backend "s3" {
    bucket = "c23-terraform-state"
    key    = "c23-epipelagic-dashboard/terraform.tfstate"
    region = "eu-west-2"
    encrypt = true
  }
}