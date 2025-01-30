# Financial Datalake
This project is a reference architecture for storing data and presenting it in a secure manner. This project was completed in January 2025.

## Table of Contents
* [What was the problem?](#what-was-the-problem?)
* [What was the solution?](#what-was-the-solution?)
* [What were the results?](#what-were-the-results?)

## What was the problem?
Storing data in the cloud introduces challenges relating to security and accessibility. It is very important to understand how to properly provision permissions to your data so that users can gain access to the information they need without exposing your data to unneccessary risk. This project seeks to serve as a reference architecture for how to securely store and access data saved to S3 in a scalable and cost-efficient manner. The solution leverages AWS services to implement best practices for cloud data storage and security, enabling seamless upload and retrieval of sensitive information. The data that is used for this data lake is publicly accessible data that is available through CNBC's website. However, the architecture outlined in this project is still applicable for private data that needs to be securely managed.

## What was the solution?
To collect articles for the data lake, I created multiple Lambda functions in AWS using Terraform. I implemented a scraper using beautifulSoup and requests that would scrape articles published to multiple CNBC RSS feeds and save them to S3. For each article, I would create an HTML file containing the contents of the article as well as relevant information such as the publication date and a link to the actual article. I also created an index.html file, which contained a table listing all the articles that I had saved to S3. The code for this project can be reviewed in the code subdirectory and used the following resources:
 ### Code Setup
 * Python 3.11.2
  * beautifulSoup4 4.12.3
  * requests 2.32.3
  * feedparser 6.0.11
  * boto3 1.36.1

From here, there are a few ways that you can host a static website, 2 of which being:
 1. Enable static hosting on the S3 bucket
 2. Use CloudFront with Origin Access Control

The first method of hosting from S3 requires you to allow public access to the bucket and to create a bucket policy granting permissions to the objects within your bucket. An example bucket policy is shown below:
```
{
    "Version": "2008-10-17",
    "Id": "PolicyForPublicAccess",
    "Statement": [
        {
            "Sid": "AllowHtmlPublicAccess",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": [
                "arn:aws:s3:::BucketName/htmlFolder/*",
                "arn:aws:s3:::BucketName/index.html"
            ]
        }
    ]
}
```
This policy allows anyone (designated by the "*" principal) to read objects within the bucket. However, this access is only limited to an index.html file and the contents of "htmlFolder". In the context of this project, the "htmlFolder" directory contains the HTML files that have been created for the articles. 


To improve network performance and to use a custom domain name, I opted to use the second method of hosting with CloudFront. This requires you to create a CloudFront distribution with the bucket as the origin domain and to create a bucket policy similar to the following:
```
{
    "Version": "2008-10-17",
    "Id": "PolicyForCloudFrontPrivateContent",
    "Statement": [
        {
            "Sid": "AllowCloudFrontServicePrincipalReadOnly",
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudfront.amazonaws.com"
            },
            "Action": "s3:GetObject",
            "Resource": [
                "arn:aws:s3:::bucketName/exampleFolder/*",
                "arn:aws:s3:::bucketName/index.html"
            ],
            "Condition": {
                "StringEquals": {
                    "AWS:SourceArn": "arn:aws:cloudfront::AccountID:distribution/DistributionID"
                }
            }
        }
    ]
}
```
This bucket policy is similar to the previous one in that it allows read-only access to an index.html file and the contents of "htmlFolder". However, this time the principal is limited to CloudFront (specifically to the CloudFront distribution that we have specified with the "DistributionID"). I then used Route53 and AWS Certificate Manager to route traffic to a custom domain using HTTPS. I used the following resources to provision and host my static website:
### AWS Setup
* HTML
* Terraform/CloudFormation
* IAM
* S3
* Lambda
* CloudFront
* Route53

## What were the results?
The financial articles are available at: [https://findata.ix.ixcloudsecurity.com](https://findata.ix.ixcloudsecurity.com). This list is regularly updated.
### Issues that still need to be addressed
One issue that has been observed is that some articles require a premium subscription. As a result, the scraper is unable to access these articles and the entry saved to S3 is empty. One potential work around is to ignore articles that are inaccesible.
### Future projects
Creating a financial datalake with numerous articles opens the door to future work analyzing this information. It could be interesting to train a machine learning algorithm that is capable of producing actionable predictions in the stock market based on trending news and financial information.
