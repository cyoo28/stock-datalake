locals {
    funcName = "scrapeRSS"
    roleName = "lambda-fullS3"
    ruleName = "run-daily"
}

resource "aws_iam_role" "myRole" {
  name = local.roleName
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "s3Access" {
  role = aws_iam_role.myRole.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "lambdaExecute" {
  role = aws_iam_role.myRole.name
  policy_arn = "arn:aws:iam::aws:policy/AWSLambdaExecute"
}

resource "aws_cloudwatch_log_group" "myLogGroup" {
  name = "/aws/lambda/${local.funcName}"
  retention_in_days = 3
}

resource "aws_cloudwatch_event_rule" "myRule" {
  name = local.ruleName
  schedule_expression = "cron(0 1/6 * * ? *)"
}

resource "aws_cloudwatch_event_target" "myTarget" {
  rule = aws_cloudwatch_event_rule.myRule.name
  target_id = local.funcName
  arn = aws_lambda_function.myLambda.arn
}

resource "aws_lambda_permission" "myPermissions" {
  statement_id  = "scraper-permission"
  action = "lambda:InvokeFunction"
  function_name = aws_lambda_function.myLambda.function_name
  principal = "events.amazonaws.com"
  source_arn = aws_cloudwatch_event_rule.myRule.arn
}

resource "aws_lambda_function" "myLambda" {
  filename = "${path.cwd}/${local.funcName}.zip"
  source_code_hash = filebase64sha256("${path.cwd}/${local.funcName}.zip")
  function_name = local.funcName
  role = aws_iam_role.myRole.arn
  handler = "${local.funcName}.main"
  runtime = "python3.13"
  timeout = 900
  memory_size = 1024
  environment {
    variables = {
      bucket = "026090555438-stockdata"
      rssKey = "rssList.json"
    }
  }
}