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
  os.environ["bucket"] = "026090555438-stockdata"
  os.environ["rssKey"] = "rssList.json"

# In[ ]:


"""
# CNBC Top News
topNews = {"network":"CNBC", "feed":"Top News", "url":"https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114"}
# Earnings
earning = {"network":"CNBC", "feed":"Earnings", "url":"https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=15839135"}
# Economy
economy = {"network":"CNBC", "feed":"Economy", "url":"https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=20910258"}
# Finance
finance = {"network":"CNBC", "feed":"Finance", "url":"https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664"}
# Tech
tech = {"network":"CNBC", "feed":"Tech", "url":"https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=19854910"}
# Investing
invest = {"network":"CNBC", "feed":"Investing", "url":"https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=15839069"}
"""

# # Import Packages

# In[ ]:


import feedparser
import requests
from bs4 import BeautifulSoup
import json
import boto3
import datetime

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

# # SaveStockData Class

# In[ ]:


# Class for saving stock data to s3
class SaveStockData:
  def __init__(self):
    session = boto3.Session()
    self.s3 = session.client('s3')

  # Create key path for metadata
  # Arg: newEntry [dict] **entry from RSS feed**,
  #      network [str] **network that published the RSS feed**
  # Returns: metaKey [str] **meta key**
  def createMetaPath(self, newEntry, network):
    # Gather necessary info from entry to create key
    id = newEntry["id"]
    year = newEntry["published_parsed"][0]
    month = newEntry["published_parsed"][1]
    day = newEntry["published_parsed"][2]
    # Create key
    metaKey = "metadata/{}/{}/{}/{}/{}.json".format(network, year, month, day, id)
    return metaKey

  # Create key path for textdata
  # Arg: newEntry [dict] **entry from RSS feed**,
  #      network [str] **network that published the RSS feed**
  # Returns: textKey [str] **text key**
  def createTextPath(self, newEntry, network):
    # Gather necessary info from entry to create key
    id = newEntry["id"]
    year = newEntry["published_parsed"][0]
    month = newEntry["published_parsed"][1]
    day = newEntry["published_parsed"][2]
    # Create key
    textKey = "textdata/{}/{}/{}/{}/{}.json".format(network, year, month, day, id)
    return textKey

  # Collect metadata to save
  # Arg: newEntry [dict] **entry from RSS feed**,
  #      feed [str] **RSS feed name**
  # Returns: metaData [json dict] **meta data**
  def collectMetaData(self, newEntry, feed):
    title = newEntry["title"]
    link = newEntry["link"]
    date = newEntry["published"]
    sponsor = newEntry["metadata_sponsored"]
    metaType = newEntry["metadata_type"]
    metaData = json.dumps({"title":title,"link":link,"date":date,"feed":feed,"sponsor":sponsor,"type":metaType})
    return metaData

  # Collect textdata to save
  # Arg: newEntry [dict] **entry from RSS feed**,
  #      feed [str] **RSS feed name**
  # Returns: textData [json str] **text data**
  def collectTextData(self, newEntry):
    textData = json.dumps(newEntry["text"])
    return textData

  # Save data to s3
  # Arg: data [obj] **data to be saved**,
  #      bucket [str] **bucket name**,
  #      key [str] **key to save to**
  def saveData(self, data, bucket, key):
    self.s3.put_object(
        Body=data,
        Bucket=bucket,
        Key=key
    )
    print("Saved object at {}".format(key))
    return 0

# # Scrape RSS Feeds

# In[ ]:


# Fetch the entries from an RSS feed
# Arg: source [str] **contains RSS feed link**
# Returns: entries [list of dict] **contains entries in RSS feed**
def fetchRSS(source):
  # fetch the RSS feed
  RSS = feedparser.parse(source)
  # extract the entries from the retrieved feed
  entries = RSS.entries
  return entries

# # Parse HTML

# In[ ]:


# Scrape an entry using the url
# Arg: url [str] **contains url for the entry**
# Returns: soup [BeautifulSoup obj]
def scraper(url):
  # scrape the data from the url using requests and BeautifulSoup
  page = requests.get(url)
  soup = BeautifulSoup(page.content, "html.parser")
  return soup

# Extract text from the scraped/parsed entry
# Arg: soup [BeautifulSoup obj]
# Returns: result [str] **contains the text of the entry**
def textExtract(soup):
  # extract the data corresponding to the entry from the soup
  entryGroups = soup.find_all("div", {"class": "group"})
  sections = []
  for group in entryGroups:
    section = group.find_all("p")
    if section:
      sections.append(section)
  # extract the text of the entry
  text = []
  for section in sections:
    for para in section:
      text.append(para.get_text())
  # return the entry joined as a single string
  return ("\n").join(text)

# # Get publication dates

# In[ ]:


# Get publication dates of files
# Arg: bucket [str] **bucket name**,
#      keys [list of str] **list of keys that require dates**
#      s3Helper [AccessS3 inst]
# Returns: dates [list of str] **list of dates for keys**
def getDates(bucket, keys, s3Helper):
  dates = []
  for key in keys:
    date = (json.loads(s3Helper.getObj(bucket, key)['Body'].read().decode()))
    dates.append(date["date"])
  return dates

# # Convert publication dates

# In[ ]:


# Convert publication dates of files
# Arg: unstrDates [list of str] **unstructed dates**
# Returns: [list of str] **list of structured dates**
def convertDates(unstrDates):
  dateFormat = "%a, %d %b %Y %H:%M:%S %Z"
  return [datetime.datetime.strptime(unstrDate, dateFormat) for unstrDate in unstrDates]

# # Save New Entries to S3

# In[ ]:


# Save the text data and metadata for a new entry
# Arg: newEntry [dict] **new entry to be saved**,
#      network [str] **network that published the RSS feed**,
#      feed [str] **name of the RSS feed**,
#      bucket [str] **S3 bucket where data is stored**
def saveSingleEntry(newEntry, network, feed, bucket):
  stockSaver = SaveStockData()

  # scrape and add the text to the entry
  entryURL = newEntry["link"]
  soup = scraper(entryURL)
  result = textExtract(soup)
  newEntry["text"] = result

  # create object path
  metaKey = stockSaver.createMetaPath(newEntry, network)
  textKey = stockSaver.createTextPath(newEntry, network)

  # collect metadata and text data
  metaData = stockSaver.collectMetaData(newEntry, feed)
  textData = stockSaver.collectTextData(newEntry)

  # upload metadata
  stockSaver.saveData(metaData, bucket, metaKey)
  # upload text data
  stockSaver.saveData(textData, bucket, textKey)
  return 0

# In[ ]:


# Save new entries to S3 and update old ones
# Arg: entries [list of dict] **entries gathered from feed**
#      network [str] **network that published the RSS feed**
#      feed [str] **name of the RSS feed**
#      bucket [str] **bucket where data is stored**
#      s3Helper [AccessS3 inst]
# Returns: count [int] **number of entries saved for feed**
def saveNewEntries(entries, network, feed, bucket, s3Helper):
  # Setup save counter
  count = 0
  print("This feed has {} entries".format(len(entries)))
  # Get the existing entries from s3
  existKeys = s3Helper.scanObjs(bucket, "metadata")
  for entry in entries:
    # Get the entry id
    entryID = entry["id"]
    # if the entry id does not already exist,
    if not any(entryID in existKey for existKey in existKeys):
      # then save it to s3
      print("Saving new entry id: {}".format(entryID))
      saveSingleEntry(entry, network, feed, bucket)
      count += 1
    # otherwise it already exists
    else:
      # Search for matching entries
      matchKeys = [existKey.split("/", 1)[1] for existKey in existKeys if entryID in existKey]
      metaKeys = ["metadata/"+matchKey for matchKey in matchKeys]
      textKeys = ["textdata/"+matchKey for matchKey in matchKeys]
      # Retrieve and convert dates to comparable datetime objects
      matchDates = getDates(bucket, metaKeys, s3Helper)
      existDates = convertDates(matchDates)
      latestDate = max(existDates)
      entryDate = convertDates([entry["published"]])[0]
      # if the entry has been updated,
      if entryDate > latestDate:
        print("Updating entry id: {}".format(entryID))
        for metaKey, textKey in zip(metaKeys, textKeys):
          # delete the old one(s)
          #print("Deleted {}".format(metaKey))
          #print("Deleted {}".format(textKey))
          s3Helper.deleteObj(bucket, metaKey)
          s3Helper.deleteObj(bucket, textKey)
        # and save the new one
        saveSingleEntry(entry, network, feed, bucket)
        count += 1
      # otherwise check for duplicates
      elif len(matchKeys) > 1:
        print("Deleting duplicate entries id: {}".format(entryID))
        for metaKey, textKey, existDate in zip(metaKeys, textKeys, existDates):
          if not existDate==latestDate:
            # and delete the older ones
            #print("Deleted {}".format(metaKey))
            #print("Deleted {}".format(textKey))
            s3Helper.deleteObj(bucket, metaKey)
            s3Helper.deleteObj(bucket, textKey)
  # Report the total number of entries that have been saved
  if count==0:
    print('No new entries for {}'.format(feed))
  else:
    print("{} new entries for {}".format(count, feed))
  return count

# # main

# In[ ]:


def main(event, context):
  # Set up variables and AccessS3 class
  count = 0
  bucket = os.environ["bucket"]
  rssKey = os.environ["rssKey"]
  s3Helper = AccessS3()
  # Retrieve list of RSS feeds to gather entries from
  obj = s3Helper.getObj(bucket, rssKey)
  rssList = json.loads(obj["Body"].read().decode())
  # Gather entries from the feeds and save new ones to S3
  count = 0
  for rss in rssList:
    rssNetwork = rss["network"]
    rssFeed = rss["feed"]
    rssURL = rss["url"]
    # Fetch entries from the current RSS feed
    print("Currently scraping from {}".format(rssFeed))
    entries = fetchRSS(rssURL)
    # Save new entries to S3
    count += saveNewEntries(entries, rssNetwork, rssFeed, bucket, s3Helper)
  print('{} total entries have been saved'.format(count))
  return {
      'statusCode': 200
  }

# # Test

# In[ ]:


if 'COLAB_GPU' in os.environ:
  # import text and test
  result = main(None, None)
  print(result)

# In[ ]:



