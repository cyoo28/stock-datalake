locals {
    funcName = "test-s3-trigger"
    roleName = "lambda-fullS3"
    bucketName = "026090555438-stockdata"
}

resource "aws_s3_bucket_notification" "myS3Trigger" {
  bucket = "${local.bucketName}"
  lambda_function {
    lambda_function_arn = "${aws_lambda_function.myLambda.arn}"
    events = ["s3:ObjectCreated:*"]
    filter_prefix = "htmldata/"
    filter_suffix = ".html"
  }
}

resource "aws_lambda_permission" "myS3Permission" {
  statement_id = "AllowS3Invoke"
  action = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.myLambda.function_name}"
  principal = "s3.amazonaws.com"
  source_arn = "arn:aws:s3:::${local.bucketName}"
}

data "aws_iam_role" "myRole" {
  name = local.roleName
}

resource "aws_cloudwatch_log_group" "myLogGroup" {
  name = "/aws/lambda/${local.funcName}"
  retention_in_days = 3
}

resource "aws_lambda_function" "myLambda" {
  filename = "${path.cwd}/${local.funcName}.zip"
  source_code_hash = filebase64sha256("${path.cwd}/${local.funcName}.zip")
  function_name = local.funcName
  role = data.aws_iam_role.myRole.arn
  handler = "${local.funcName}.main"
  runtime = "python3.13"
  timeout = 900
  memory_size = 1024
  environment {
    variables = {
      bucket = "026090555438-stockdata"
    }
  }
}