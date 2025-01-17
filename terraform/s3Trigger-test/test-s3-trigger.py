def main(event, context):
  print("s3 trigger successful")
  return {
    'statusCode': 200,
  }
