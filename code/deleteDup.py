#!/usr/bin/env python
# coding: utf-8

# <a href="https://colab.research.google.com/github/iyoo2018/findatalake/blob/master/deleteDup.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# # Code Exclusive to Colab

# In[1]:


import os
if 'COLAB_GPU' in os.environ:
  # Mount Google Drive to notebook
  from google.colab import drive
  drive.mount('/content/gdrive')
  import sys
  sys.path.append('/content/gdrive/My Drive/Colab Notebooks')

# In[2]:


if 'COLAB_GPU' in os.environ:
  # Set configuration file to access AWS
  os.environ['AWS_CONFIG_FILE']="/content/gdrive/My Drive/cred-stockdata.txt"
  # Set environment variables
  os.environ["bucket"] = "026090555438-stockdata"

# # Import Packages

# In[3]:


import json
import boto3
import datetime
from collections import Counter

# # AccessS3 Class

# In[4]:


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

# # Get publication dates

# In[5]:


# Get publication dates of files
# Arg: bucket [str] **bucket name**,
#      keys [list of str] **list of keys that require dates**
#      s3Helper [AccessS3 Instance]
# Returns: dates [list of str] **list of dates for keys**
def getDates(bucket, keys, s3Helper):
  dates = []
  for key in keys:
    date = (json.loads(s3Helper.getObj(bucket, key)['Body'].read().decode()))
    dates.append(date["date"])
  return dates

# # Convert publication dates

# In[6]:


# Convert publication dates of files
# Arg: unstrDates [list of str] **unstructed dates**
# Returns: [list of str] **list of structured dates**
def convertDates(unstrDates):
  dateFormat = "%a, %d %b %Y %H:%M:%S %Z"
  return [datetime.datetime.strptime(unstrDate, dateFormat) for unstrDate in unstrDates]

# # Lookup a key in a list of keys (not accessing s3)

# In[7]:


# Look up a key in a list of keys
# Arg: keys [list of str] **list of keys to look in**
#      lookupKey [str] **key to lookup**
# Returns: matchKeys [list of str] **list of matching keys**
def lookupKeys(keys, lookupKey):
  matchKeys = [key for key in keys if lookupKey in key]
  return matchKeys

# # Delete Duplicates

# In[8]:


# Find duplicates and delete old ones
# Arg: bucket [str] **bucket name**
def deleteDup(bucket):
  # Set up AccessS3 class and deletion counter
  s3Helper = AccessS3()
  count = 0
  # Get all object keys and entry ids in the bucket
  objs = s3Helper.scanObjs(bucket, "metadata")
  ids = [obj.rsplit('/', 1)[-1].split('.')[0] for obj in objs]
  # Count occurences of each id in the bucket
  occurences = Counter(ids)
  for id, occurence in occurences.items():
    # if the id occurs more than once,
    if occurence > 1:
      # Get all keys that match the id
      matchMetaKeys = lookupKeys(objs, id)
      matchTextKeys = ["textdata/"+key.split("/",1)[1] for key in matchMetaKeys]
      # Get the dates for each occurence and convert them to comparable datetime objects
      metaDates = getDates(bucket, matchMetaKeys, s3Helper)
      matchDates = convertDates(metaDates)
      newDate = max(matchDates)
      for metakey, textkey, date in zip(matchMetaKeys, matchTextKeys, matchDates):
        # Delete occurences that are not the most recent one
        if not date==newDate:
          #print("Deleted {}".format(metakey))
          #print("Deleted {}".format(textkey))
          s3Helper.deleteObj(bucket, metakey)
          s3Helper.deleteObj(bucket, textkey)
          count += 1
  print("{} have been deleted".format(count))
  return 0

# # main

# In[9]:


def main(event, context):
  bucket = os.environ["bucket"]
  deleteDup(bucket)
  return {
      'statusCode': 200
  }

# # Test

# In[10]:


if 'COLAB_GPU' in os.environ:
  result = main(None, None)
  print(result)

# In[ ]:



