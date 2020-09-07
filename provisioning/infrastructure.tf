terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

provider "aws" {
  profile = "default"
  region  = "us-east-1"

  access_key                  = "mock_access_key"
  secret_key                  = "mock_secret_key"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  s3_force_path_style         = true

  endpoints {
    dynamodb       = "http://localhost:4569"
    s3             = "http://localhost:4572"
    sqs            = "http://localhost:4576"
  }
}

resource "aws_dynamodb_table" "dynamodb-users-table" {
  name         = "users"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "user_id"

  attribute {
    name = "user_id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "dynamodb-articles-table" {
  name         = "articles"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "user_id"
  range_key    = "article_id"

  attribute {
    name = "user_id"
    type = "S"
  }

  attribute {
    name = "article_id"
    type = "S"
  }
}

resource "aws_s3_bucket" "article_bucket" {
  bucket = "kermes-articles"
  acl    = "private"
}

resource "aws_s3_bucket" "ebooks_bucket" {
  bucket = "kermes-ebooks"
  acl    = "private"
}

resource "aws_sqs_queue" "fetch_article_queue" {
  name                        = "kermes-fetch-article.fifo"
  fifo_queue                  = true
  content_based_deduplication = true
}

resource "aws_sqs_queue" "fetch_completed_queue" {
  name                        = "kermes-fetch-completed.fifo"
  fifo_queue                  = true
  content_based_deduplication = true
}
