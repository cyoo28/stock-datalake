#!/usr/bin/env python
# coding: utf-8

# # Code Exclusive to Colab

# In[ ]:


import os
if 'COLAB_GPU' in os.environ:
  # Mount Google Drive to notebook
  from google.colab import drive
  drive.mount('/content/gdrive')
  import sys
  sys.path.append('/content/gdrive/My Drive/Colab Notebooks')


# In[ ]:


if 'COLAB_GPU' in os.environ:
  # Set configuration file to access AWS
  os.environ['AWS_CONFIG_FILE']="/content/gdrive/My Drive/cred-stockdata.txt"
  # Set environment variables
  os.environ['bucket'] = "026090555438-stockdata"
  os.environ['metaKey'] = "metadata"
  os.environ['htmlKey'] = "htmldata"
  os.environ["headKey"] = "tableHead.txt"
  os.environ["tableKey"] = "tableContents.txt"


# # Import Packages

# In[ ]:


import boto3
import json
import datetime


# # HTMLFormatter Class

# In[ ]:


# Class for working with HTML
# Formats tags and generates an HTML file
class HTMLformatter:
  def __init__(self):
    # Setup s3 client and HTML text
    self.text = ""
    session = boto3.Session()
    self.s3 = session.client('s3')

  # Format head tag
  # Arg: title [str] **tab name** ,
  #      meta [dict] **metadata**
  # Returns: formatted head tag [str]
  def head(self, title, meta):
    head = "<head>\n<title>{}</title>".format(title)
    for key, value in meta.items():
      head += "<meta name={} content={}>".format(key, value)
    return head

  # Format heading tag
  # Arg: heading [str] **heading/section name**,
  #      size [str] **font size**
  # Returns: formatted heading tag [str]
  def heading(self, heading, size):
    return "<h{}>{}</h{}>".format(size, heading, size)

  # Format a tag
  # Arg: url [str] **link to website**,
  #      text [str] **displayed text**
  # Returns: formatted a tag [str]
  def a(self, url, text):
    aTag = "<a href={}>{}</a>".format(url,text)
    return aTag

  # Open the table tag
  # Arg: heading [str] **table heading name**,
  #      columnNames [str] **column headings**,
  # Returns: table opening tag [str]
  def tableHead(self, heading, columnNames):
    tableHeading = self.heading(heading, 2)
    tableSettings = "\n<table border=\"1\" cellpadding=\"10\">\n  <tr>"
    tableColumns = ""
    for columnName in columnNames:
      tableColumns += "\n    <th>{}</th>".format(columnName)
    tableColumns += "\n  </tr>"
    return tableHeading + tableSettings + tableColumns

  # Add entries to table tag
  # Arg: table [str] **table html tag**,
  #      columnNames [str] **column headings**,
  #      entries [list of dict] **objects to be put into the table**,
  #      existTable [str, default=None] **existing html table contents tag**
  # Returns: table contents tag [str]
  def tableContents(self, columnNames, entries, existTable=None):
    table = ""
    for entry in entries:
      table += "\n  <tr>"
      for columnName in columnNames:
        table += "\n    <td>{}</td>".format(entry[columnName])
      table += "\n  </tr>"
    if not existTable==None:
      table += existTable
    return table

  # Close the table tag
  # Returns: table closing tag [str]
  def tableTail(self):
    return "\n</table>"

  # Format the table tag
  # Arg: heading [str] **table heading name**,
  #      column_names [str] **column headings**,
  #      entries [list of dict] **entries to add to html table contents**,
  #      existTable [str, default=None] **existing html table contents tag**
  # Returns: formatted table tag [str]
  def fullTable(self, heading, columnNames, entries, existTable=None):
    head = self.tableHead(heading, columnNames)
    contents = self.tableContents(columnNames, entries, existTable)
    tail = self.tableTail()
    return head + contents + tail

  # Format body tag
  # Arg: heading [str] **body heading name**,
  #      text [str] **text to be displayed**
  # Returns: formatted body tag [str]
  def body(self, heading, text):
    bodyHeading = self.heading(heading, 2)
    bodyText = "<body>"
    for para in text:
      bodyText += "\n  <p>{}</p>".format(para)
    bodyText += "\n</body>"
    return bodyHeading+"\n"+bodyText

  # Begin the HTML file
  def openHTML(self):
    self.text += "<!DOCTYPE html>\n<html>"
    return 0

  # Add element(s) to HTML file
  # Arg: *elements **HTML elements produced by other functions** [str]
  def addHTML(self, *elements):
    for element in elements:
      self.text += "\n"+element
    return 0

  # End the HTML file
  def closeHTML(self):
    self.text += "\n</html>"
    return 0

  # Write the entire HTML file at once
  # Arg: *elements [str] **HTML elements produced by other functions**
  def fullWrite(self, *elements):
    self.clearHTML()
    self.openHTML()
    for element in elements:
      self.addHTML(element)
    self.closeHTML()
    return 0

  # Clear the HTML file
  def clearHTML(self):
    self.text = ""
    return 0

  # Review the HTML file
  def reviewHTML(self):
    return self.text

  # Save the HTML file to S3
  # Arg: bucket [str] **bucket name**,
  #      key [str] **key to save to**
  def saveHTML(self, bucket, key):
    self.s3.put_object(
        Body=self.text,
        Bucket=bucket,
        Key=key,
        ContentType='text/html'
    )
    return 0


# # AccessS3 Class
# 

# In[22]:


# Class for accessing s3
class AccessS3:
  def __init__(self):
    # Setup s3 client
    session = boto3.Session()
    self.s3 = session.client('s3')
    self.paginator = self.s3.get_paginator('list_objects_v2')

  # Get an object
  # Arg: bucket [str] **bucket name**,
  #      key [str] **object key**,
  # Returns: [s3 obj]
  def getObj(self, bucket, key):
    return self.s3.get_object(Bucket=bucket, Key=key)

  # Delete an object
  # Arg: bucket [str] **bucket name**,
  #      key [str] **object key**
  def deleteObj(self, bucket, key):
    self.s3.delete_object(Bucket=bucket, Key=key)
    print("Deleted object at {}".format(key))
    return 0

  # Save an object
  # Arg: data [obj] **data to be saved**
  #      bucket [str] **bucket name**,
  #      key [str] **object key**
  def saveObj(self, data, bucket, key):
    self.s3.put_object(
      Body=data,
      Bucket=bucket,
      Key=key
    )
    print("Saved object at {}".format(key))
    return 0

  # Return objects contained in a key
  # Arg: bucket [str] **bucket name**,
  #      key [str] **object key**
  #      sort [str] default None **sort entries by upload date "newFirst" newest to oldest "newLast" oldest to newest**
  # Returns: objs [list of s3 objs] **objects in key**
  def scanObjs(self, bucket, key, sort=None):
    objs = []
    # Get all objects in bucket and key pair
    pages = self.paginator.paginate(Bucket=bucket, Prefix=key)
    # if you would like to sort the objects by upload dates,
    if sort:
      for page in pages:
        for content in page['Contents']:
          # Only add objects that do not end in "/" (folder keys end in "/")
          if not content['Key'].endswith("/"):
            objs.append(content)
      # Sort by last modified date
      lastModified = lambda obj: int(obj['LastModified'].strftime('%s'))
      if sort=="newFirst":
        sortedObjs =  [obj['Key'] for obj in sorted(objs, key=lastModified, reverse=True)]
      elif sort=="newLast":
        sortedObjs =  [obj['Key'] for obj in sorted(objs, key=lastModified)]
      return sortedObjs
    # otherwise,
    else:
      # Convert iterator to list
      for page in pages:
        for content in page['Contents']:
          # Only add object keys that do not end in "/" (folder keys end in "/")
          if not content['Key'].endswith("/"):
            objs.append(content['Key'])
      return objs

  # Look up a specific object
  # Arg: bucket [str] **bucket name**
  #      key [str] **lookup key**
  #      subKey [str] **substring of key to look for**
  # Returns: matchObjs [list of s3 objs] **object key if it exists**
  def lookupObj(self, bucket, key, subKey):
    matchObjs = []
    # Return objects contained in a key
    objs = self.scanObjs(bucket, key)
    # Add object keys that contain the lookup substring
    for obj in objs:
      if subKey in obj:
        matchObjs.append(obj)
    return matchObjs


# # StockData Object Class

# In[24]:


# Class to represent stock data entries
class StockData:
  # Arg: bucket [str] **bucket name**
  #      baseKey [str] **base key for the obj**
  def __init__(self, bucket, baseKey):
    self.baseKey = baseKey
    self.id = baseKey.rsplit("/", 1)[1].split(".",1)[0]
    self.bucket = bucket

  # Get meta data for object
  # Arg: s3Helper [AccessS3 inst]
  # Returns: meta [dict] **meta data**
  def getMeta(self, s3Helper):
    metaKey = "metadata/{}".format(self.baseKey)
    meta = json.loads(s3Helper.getObj(self.bucket, metaKey)['Body'].read().decode())
    return meta

  # Get text data for object
  # Arg: s3Helper [AccessS3 inst]
  # Returns: text [str] **text data**
  def getText(self, s3Helper):
    textKey = "textdata/{}".format(self.baseKey)
    text = json.loads(s3Helper.getObj(self.bucket, textKey)['Body'].read().decode())
    text = text.split("\n")
    return text


# # Scan for Files

# In[23]:


# Scan for htmls to add to index.html
# Arg: mode [str] **lambda mode**,
#      bucket [str] **bucket name**,
#      metaKey [str] **meta key**,
#      htmlKey [str] **html key**,
#      tableKey [str] **table key**,
#      s3Helper [AccessS3 inst]
# Returns: stockObjs [list of StockData objs]
def checkHTML(mode, bucket, metaKey, htmlKey, tableKey, s3Helper):
  # get all (sorted) html and meta data
  htmls = s3Helper.scanObjs(bucket, htmlKey, sort="newFirst")
  metas = s3Helper.scanObjs(bucket, metaKey)
  # get the corresponding basekey for each html key (and verify that there is a metakey)
  baseKeys = []
  # if in create mode,
  if mode=="create":
    for html in htmls:
      # extract the id for lookup
      id = html.rsplit("/",1)[1].split(".",1)[0]
      # extract the baseKey for all htmls
      matchMeta = [meta for meta in metas if id in meta][0]
      baseKeys.append(matchMeta.split("/",1)[1])
  # if in update mode,
  if mode=="update":
    # make sure the html is not already in index.html
    table = s3Helper.getObj(bucket, tableKey)['Body'].read().decode()
    for html in htmls:
      # extract the id for lookup
      id = html.rsplit("/",1)[1].split(".",1)[0]
      # if the id is not in the table,
      if not id in table:
        # extract the id for lookup
        id = html.rsplit("/",1)[1].split(".",1)[0]
        # then extract the baseKey for the new html
        matchMeta = [meta for meta in metas if id in meta][0]
        baseKeys.append(matchMeta.split("/",1)[1])
  # Create stockData objs
  stockObjs = []
  for baseKey in baseKeys:
    stockObjs.append(StockData(bucket, baseKey))
  return stockObjs


# # Create/update the table

# In[25]:


# Create/update table with html files
# Arg: mode [str] **lambda mode**,
#      metaData [list of dict] **data to add to table**,
#      bucket [str] **bucket name**,
#      headKey [str] **table header key**,
#      tableKey [str] **table key**,
#      s3Helper [AccessS3 inst],
#      formatter [HTMLFormatter inst]
def modifyTable(mode, metaData, bucket, headKey, tableKey, s3Helper, formatter):
  # if in create mode,
  if mode=="create":
    # Create the table
    head = formatter.tableHead("Stock Data Files", list(metaData[0].keys()))
    table = formatter.tableContents(list(metaData[0].keys()), metaData)
    # Write the table header and contents to S3
    s3Helper.saveObj(head, bucket, headKey)
    s3Helper.saveObj(table, bucket, tableKey)
  # if in update mode
  elif mode=="update":
    # Get the table from s3
    existTable = s3Helper.getObj(bucket, tableKey)['Body'].read().decode()
    # Add html file to the table
    table = formatter.tableContents(list(metaData[0].keys()), metaData, existTable)
    # Write the table to S3
    s3Helper.saveObj(table, bucket, tableKey)
  return 0


# # Collect Metadata

# In[26]:


# Collect metadata for a single html
# Arg: stockObj [StockData objs],
#      s3Helper [AccessS3 inst],
#      formatter [HTMLFormatter inst]
# Returns: metaData [dict] **data to add to table**
def collectMeta(stockObj, s3Helper, formatter):
  # Get the metadata for file
  metaData = stockObj.getMeta(s3Helper)
  # Add article id
  metaData['id'] = stockObj.id
  # Add link to website as formatted a tag
  metaData['external-link'] = formatter.a(metaData['link'],'website')
  metaData.pop('link')
  # Add link to S3 HTML as formatted a tag
  url = "https://stockdata.ix.ixcloudsecurity.com/htmldata/{}.html".format(metaData['id'])
  metaData['internal-link'] = formatter.a(url,'s3')
  return metaData


# # Update Table for Each HTML

# In[27]:


# Update table with one html file
# Arg: mode [str] **lambda mode**,
#      stockObj [StockData objs],
#      headKey [str] **table header key**,
#      tableKey [str] **table key**,
#      s3Helper [AccessS3 inst],
#      formatter [HTMLFormatter inst]
def updateSingleTable(mode, stockObj, headKey, tableKey, s3Helper, formatter):
  # Create metadata for StockData objects
  metaData = [collectMeta(stockObj, s3Helper, formatter)]
  modifyTable(mode, metaData, stockObj.bucket, headKey, tableKey, s3Helper, formatter)
  return 0


# # Update Table for All HTMLs

# In[28]:


# Create # Update table with multiple html files
# Arg: mode [str] **lambda mode**,
#      bucket [str] **bucket name**,
#      metaKey [str] **meta key**,
#      htmlKey [str] **html key**,
#      headKey [str] **table header key**,
#      tableKey [str] **table key**,
#      s3Helper [AccessS3 inst],
#      formatter [HTMLFormatter inst]
# Returns: count [int] **number of HTMLs added**
def updateAllTable(mode, bucket, metaKey, htmlKey, headKey, tableKey, s3Helper, formatter):
  # Scan for all files
  stockObjs = checkHTML(mode, bucket, metaKey, htmlKey, tableKey, s3Helper)
  # Check to see if there are any new htmls to add
  if len(stockObjs) > 1:
    # Create metadata for StockData objects
    metaData = [collectMeta(stockObj, s3Helper, formatter) for stockObj in stockObjs]
    modifyTable(mode, metaData, bucket, headKey, tableKey, s3Helper, formatter)
  return(len(stockObjs))


# # Create index.html

# In[29]:


# Create index.html
# Arg: bucket [str] **bucket name**,
#      headKey [str] **table header key**,
#      tableKey [str] **table key**,
#      s3Helper [AccessS3 inst],
#      formatter [HTMLFormatter inst]
def createIndex(bucket, headKey, tableKey, s3Helper, formatter):
  # Create head and heading
  head = formatter.head("index.html", {"description":"basic webpage for accessing saved stock data"})
  heading = formatter.heading("index.html", 1)
  # Get the table from s3 and close it
  tableHead = s3Helper.getObj(bucket, headKey)['Body'].read().decode()
  tableContent = s3Helper.getObj(bucket, tableKey)['Body'].read().decode()
  tableTail = formatter.tableTail()
  table = tableHead + tableContent + tableTail
  # Create the full HTML file
  formatter.fullWrite(head, heading, table)
  # Write the HTML file to S3
  key = "index.html"
  formatter.saveHTML(bucket, key)
  return 0


# # main

# In[30]:


def main(event, context):
  # Set up variables, AccessS3 class, and HTML formatter class
  bucket = os.environ["bucket"]
  tableKey = os.environ["tableKey"]
  headKey = os.environ["headKey"]
  s3Helper = AccessS3()
  formatter = HTMLformatter()
  # if set to create mode,
  if event.get('mode')=="create":
    # Set variable
    mode = event["mode"]
    metaKey = os.environ["metaKey"]
    htmlKey = os.environ["htmlKey"]
    # Create a new table from scratch
    count = updateAllTable(mode, bucket, metaKey, htmlKey, headKey, tableKey, s3Helper, formatter)
    print("Successfully created table with {} HTML file(s)".format(count))
  # otherwise if set to update mode,
  elif event.get('mode')=="update":
    # Set variable
    mode = event["mode"]
    metaKey = os.environ["metaKey"]
    htmlKey = os.environ["htmlKey"]
    # Add new html files to the table
    count = updateAllTable(mode, bucket, metaKey, htmlKey, headKey, tableKey, s3Helper, formatter)
    if count > 0:
      print("Successfully added {} HTML file(s) to the table".format(count))
    else:
      print("No new HTML files were added to the table")
  # otherwise it must be an s3 trigger event
  else:
    # Extract the key from the s3 event
    htmlKey = event['Records'][0]['s3']['object']['key']
    # Get the base key to access metadata and textdata
    id = htmlKey.rsplit("/",1)[1].split(".",1)[0]
    metaKey = s3Helper.lookupObj(bucket, "metadata", id)[0]
    baseKey = metaKey.split("/",1)[1]
    # Create a stockData obj
    stockObj = StockData(bucket, baseKey)
    # Add the new html to the table
    updateSingleTable("update", stockObj, headKey, tableKey, s3Helper, formatter)
    print("Successfully added {} to the table".format(htmlKey.rsplit("/",1)[1]))
  # Create index.html
  createIndex(bucket, headKey, tableKey, s3Helper, formatter)
  print("Successfully created index.html")
  return {
      'statusCode': 200
  }


# In[31]:


if 'COLAB_GPU' in os.environ:
  # event can consist of:
  # create - create index.html from scratch
  # update - manually update index.html
  # s3 upload event - update index.html with html file uploaded to s3
  main({"mode":"create"},"")


# In[ ]:


if __name__ == "__main__":
    main({"mode":"update"}, None)

