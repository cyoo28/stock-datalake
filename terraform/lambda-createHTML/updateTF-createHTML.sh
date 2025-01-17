# Create local variable for local save name
export localName='createHTML'
export codePath='../../code/'
export colabID='14P5iHmGGwjD2oYZx3tmGlwY6OXZ8lfC8'

# Download notebook from colab and convert to .py
pushd $codePath
wget -O "$localName.ipynb" 'https://docs.google.com/uc?export=download&id='$colabID
. ~/env/dev/bin/activate
jupyter nbconvert --to python "$localName.ipynb"
deactivate
popd
# Update zip file
zip -jg "$localName.zip" "$codePath$localName.py"
# deploy into AWS
terraform apply
