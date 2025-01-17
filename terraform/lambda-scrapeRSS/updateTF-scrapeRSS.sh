# Create local variable for local save name
export localName='scrapeRSS'
export codePath='../../code/'

# Convert .ipynb to .py
pushd $codePath
. ~/env/dev/bin/activate
jupyter nbconvert --to python "$localName.ipynb"
deactivate
popd
# Update zip file
zip -jg "$localName.zip" "$codePath$localName.py"
# deploy into AWS
terraform apply
