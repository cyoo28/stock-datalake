terraform {
  backend "s3" {
    bucket = "026090555438-terraform-state"
    key = "stockDataS3-trigger.tfstate"
    region = "us-east-1"
  }
}
