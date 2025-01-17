# Create local variable for local save name
export localName=$1

# Create zip file
pushd ~/env/$localName/lib/python3\.11/site-packages/
zip -r ~/findatalake/terraform/lambda-$localName/$localName.zip *
popd