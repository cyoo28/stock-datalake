locals {
    funcName = "deleteDup"
    roleName = "lambda-fullS3"
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