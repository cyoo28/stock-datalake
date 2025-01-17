#!/usr/bin/env python
# coding: utf-8

# <a href="https://colab.research.google.com/github/iyoo2018/findatalake/blob/master/createHTML.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

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
  os.environ['html'] = "htmldata"
  os.environ['meta'] = "metadata"

# # Import Packages

# In[ ]:


import boto3
import json

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

# In[ ]:


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
  # Returns: objs [list of s3 objs] **objects in key**
  def scanObjs(self, bucket, key, sort=False):
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
      sortedObjs =  [obj['Key'] for obj in sorted(objs, key=lastModified, reverse=True)]
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

# In[ ]:


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
# 

# In[ ]:


# Scan for files to create HTMLs for
# Arg: mode [str] **lambda mode**,
#      bucket [str] **bucket name**,
#      metaKey [str] **meta key**,
#      htmlKey [str] **html key**,
#      s3Helper [AccessS3 inst]
# Returns: stockObjs [list of StockData objs]
def checkHTML(mode, bucket, metaKey, htmlKey, s3Helper):
  # if in create mode,
  if mode=="create":
    # get all meta keys
    metas = s3Helper.scanObjs(bucket, metaKey)
    # get the base keys without the "metadata/" prefix
    baseKeys = [meta.split("/",1)[1] for meta in metas]
  # otherwise if in update mode,
  elif mode=="update":
    # get all meta and html keys
    metas = s3Helper.scanObjs(bucket, metaKey)
    htmls = s3Helper.scanObjs(bucket, htmlKey)
    # extract the entry ids
    ids = [meta.rsplit("/", 1)[1].split(".",1)[0] for meta in metas]
    # only add metadata that doesn't already have an html file
    newMetas = [meta for id, meta in zip(ids, metas) if not any([id in html for html in htmls])]
    # get the base keys without the "metadata/" prefix
    baseKeys = [newMeta.split("/",1)[1] for newMeta in newMetas]
  # Create stockData objs
  stockObjs = []
  for baseKey in baseKeys:
    stockObjs.append(StockData(bucket, baseKey))
  return stockObjs

# # Create Each HTML

# In[ ]:


# Create an HTML file for a single file
# Arg: stockObjs [list of StockData objs],
#      s3Helper [AccessS3 inst],
#      formatter [HTMLFormatter inst]
def createSingleHTML(stockObj, s3Helper, formatter):
  # Get the metadata for file
  meta_content = stockObj.getMeta(s3Helper)
  # Create the head and heading
  head = formatter.head("{}.html".format(stockObj.id), {"description":"data for article id: {}".format(stockObj.id)})
  heading = formatter.heading(meta_content['title'], 1)
  # Add entry id
  meta_content['id'] = stockObj.id
  # Add link to website as formatted a tag
  meta_content['external-link'] = formatter.a(meta_content['link'],'website')
  meta_content.pop('link')
  # Create the table
  table = formatter.fullTable("Metadata", list(meta_content.keys()), [meta_content])
  # Get the text data for file
  text_content = stockObj.getText(s3Helper)
  # Create the body
  body = formatter.body("Text", text_content)
  # Create a link to return to index.html
  return_link = formatter.a("https://{}.s3.us-east-1.amazonaws.com/index.html".format(stockObj.bucket),"Click to return to index.html")
  # Create the full HTML file
  formatter.fullWrite(head, heading, table, body, return_link)
  # Write the HTML file to S3
  htmlKey = "htmldata/{}.html".format(stockObj.id)
  formatter.saveHTML(stockObj.bucket, htmlKey)
  return 0

# # Create All HTMLs

# In[ ]:


# Create all HTML files
# Arg: mode [str] **lambda mode**,
#      bucket [str] **bucket name**,
#      metaKey [str] **meta key**,
#      htmlKey [str] **html key**,
#      s3Helper [AccessS3 inst],
#      formatter [HTMLFormatter inst]
# Returns: count [int] **number of HTMLs saved**
def createAllHTML(mode, bucket, metaKey, htmlKey, s3Helper, formatter):
  # Scan for all files
  stockObjs = checkHTML(mode, bucket, metaKey, htmlKey, s3Helper)
  # Create all html files
  for stockObj in stockObjs:
    createSingleHTML(stockObj, s3Helper, formatter)
  return len(stockObjs)

# # main

# In[ ]:


def main(event, context):
  # Set up variable, AccessS3 class, and HTML formatter class
  bucket = os.environ["bucket"]
  s3Helper = AccessS3()
  formatter = HTMLformatter()
  # If set to create or update mode,
  if event.get('mode')=="create" or event.get('mode')=="update":
    # Set variables
    mode = event["mode"]
    metaKey = os.environ["meta"]
    htmlKey = os.environ['html']
    # Create all HTMLs based on mode
    count = createAllHTML(mode, bucket, metaKey, htmlKey, s3Helper, formatter)
    if count > 0:
      print("Successfully created {} HTML file(s)".format(count))
    else:
      print("No new HTML files were created")
  # otherwise if set to review mode,
  elif event.get('mode')=="review":
    # Set variables
    mode = event["mode"]
    metaKey = os.environ["meta"]
    htmlKey = os.environ['html']
    # Get all html and meta objects
    htmls = s3Helper.scanObjs(bucket, htmlKey)
    metas = s3Helper.scanObjs(bucket, metaKey)
    # Report how many html and meta objects there are
    print('There are {} htmls and {} entries'.format(len(htmls),len(metas)))
  # otherwise it must be an s3 trigger event
  else:
    # Extract the key from the s3 event
    metaKey = event['Records'][0]['s3']['object']['key']
    baseKey = metaKey.split("/",1)[1]
    # Create a stockData obj
    stockObj = StockData(bucket, baseKey)
    # Create an HTML for the stockData obj
    createSingleHTML(stockObj, s3Helper, formatter)
    print("Successfully created HTML file for file id: {}".format(baseKey.rsplit("/",1)[1].split(".",1)[0]))

  return {
    'statusCode': 200,
  }

# In[ ]:


if 'COLAB_GPU' in os.environ:
  # event can consist of:
  # create - create all html files
  # update - only create html files that don't already exist
  # review - view the html files that already exist
  # s3 upload event - creates html file for uploaded s3 file
  result = main({"mode":"update"},"")
  print(result)

# In[ ]:



