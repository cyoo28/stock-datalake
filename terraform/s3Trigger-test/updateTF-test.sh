export localName='test-s3-trigger'
zip "$localName.zip" "$localName.py"
# deploy into AWS
terraform apply
