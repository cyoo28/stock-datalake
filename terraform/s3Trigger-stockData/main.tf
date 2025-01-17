locals {
    bucketName = "026090555438-stockdata"
    createIndexArn = "arn:aws:lambda:us-east-1:026090555438:function:createIndex"
    createHtmlArn = "arn:aws:lambda:us-east-1:026090555438:function:createHTML"
}

resource "aws_s3_bucket_notification" "S3Trigger" {
  bucket = "${local.bucketName}"
  lambda_function {
    lambda_function_arn = local.createHtmlArn
    events = ["s3:ObjectCreated:*"]
    filter_prefix = "metadata/"
    filter_suffix = ".json"
  }
  lambda_function {
    lambda_function_arn = local.createIndexArn
    events = ["s3:ObjectCreated:*"]
    filter_prefix = "htmldata/"
    filter_suffix = ".html"
  }
}

resource "aws_lambda_permission" "indexPermission" {
  statement_id = "AllowS3Invoke"
  action = "lambda:InvokeFunction"
  function_name = "createIndex"
  principal = "s3.amazonaws.com"
  source_arn = "arn:aws:s3:::${local.bucketName}"
}


resource "aws_lambda_permission" "htmlPermission" {
  statement_id = "AllowS3Invoke"
  action = "lambda:InvokeFunction"
  function_name = "createHTML"
  principal = "s3.amazonaws.com"
  source_arn = "arn:aws:s3:::${local.bucketName}"
}