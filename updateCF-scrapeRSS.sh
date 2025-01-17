# Create variables for google colab file ID and local file save name
export localName='scrapeRSS'
export colabID='15X8XDBI4ma9apUM48CUpcT-Y67v8dkcZ'

# Download notebook from colab and convert to .py
wget -O "$localName.ipynb" 'https://docs.google.com/uc?export=download&id='$colabID
. ~/env/dev/bin/activate
jupyter nbconvert --to python "$localName.ipynb"
deactivate
# Update zip file
zip -g "$localName.zip" "$localName.py"

# Upload to S3
aws s3 cp ./scrapeRSS.zip s3://026090555438-stockdata/
# Update Lambda
aws lambda update-function-code --function-name scrapeRSS --s3-bucket 026090555438-stockdata --s3-key scrapeRSS.zip
