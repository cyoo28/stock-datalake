# Stock Datalake
This project is a reference architecture for storing data and presenting it in a secure manner. This project was completed in January 2025.

## Table of Contents
* [What was the problem?](#what-was-the-problem?)
* [What was the solution?](#what-was-the-solution?)
* [What were the results?](#what-were-the-results?)

## What was the problem?


## What was the solution?
To collect data for the data lake, I implemented a scraper that would scrape articles published to multiple CNBC RSS feeds and save them to S3. Each
### Setup
* Python 3.11.2
  * beautifulSoup4 4.12.3
  * requests 2.32.3
  * feedparser 6.0.11
  * boto3 1.36.1
* HTML
* Terraform/CloudFormation
* IAM
* S3
* Lambda
* CloudFront
* Route53

## What were the results?
The stock articles are available at: [https://stockdata.ix.ixcloudsecurity.com](https://stockdata.ix.ixcloudsecurity.com). This list is regularly updated.
### Issues that still need to be addressed
One issue that has been observed is that some articles require a premium subscription. As a result, the scraper is unable to access these articles and the entry saved to S3 is empty. One potential work around is to ignore articles that are inaccesible.
