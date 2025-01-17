# Create variables for google colab file ID and local file save name
export localName='createHTML'
export colabID='14P5iHmGGwjD2oYZx3tmGlwY6OXZ8lfC8'

# Download notebook from colab and convert to .py
wget -O "$localName.ipynb" 'https://docs.google.com/uc?export=download&id='$colabID
. ~/env/dev/bin/activate
jupyter nbconvert --to python "$localName.ipynb"
deactivate
# Update zip file
zip -g "$localName.zip" "$localName.py"
