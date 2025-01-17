# Create local variable for local save name
export localName='createIndex'
export codePath='../../code/'
export colabID='160naQYGyHLk8JSMHqIWzz-F_8-_Frfdd'

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
