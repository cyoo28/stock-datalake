# Create local variable for local save name
export localName='deleteDup'
export codePath='../../code/'
export colabID='1NPucThiBLnk9zutcK9m4EuHkTRgS1poP'

# Convert .ipynb to .py
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
