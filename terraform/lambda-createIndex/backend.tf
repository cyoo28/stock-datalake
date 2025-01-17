terraform {
  backend "s3" {
    bucket = "026090555438-terraform-state"
    key = "createIndex.tfstate"
    region = "us-east-1"
  }
}
