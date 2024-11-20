---
date: '2024-11-11T22:13:59-06:00'
draft: true
title: 'Deploy Hugo website to S3 using Gitlab Actions'
---

Introduction

    Brief introduction to Hugo and its use for building static websites.
    Overview of why deploying to Amazon S3 is a great option (e.g., low-cost, scalability, etc.).

2. Prerequisites

    Tools and accounts needed:
        AWS Account.
        Installed Hugo CLI.
        Installed AWS CLI (optional but useful).
        Basic knowledge of Hugo and S3.

3. Step 1: Create a Hugo Site

    How to create a new Hugo site using the Hugo CLI.
    Example command: hugo new site my-hugo-site.
    Basic structure overview of a Hugo project.

4. Step 2: Build the Hugo Site

    Generate static files using the hugo command.
    Explain the public folder and its contents.

5. Step 3: Create an Amazon S3 Bucket

    Navigate to the AWS Management Console.
    Create a new S3 bucket (steps to create a bucket).
    Bucket naming conventions and considerations (e.g., uniqueness, region selection).

6. Step 4: Configure S3 Bucket for Static Website Hosting

    Enable static website hosting on the S3 bucket.
    Configure index and error documents (e.g., index.html and 404.html).

7. Step 5: Upload the Hugo Site Files to S3

    Manual upload using the AWS Management Console.
    Optional: Upload using AWS CLI (e.g., aws s3 sync ./public s3://your-bucket-name).
    Configuring permissions for public access (e.g., setting bucket policies, enabling public read access).

8. Step 6: Set Up Permissions and Bucket Policy (if applicable)

    Configuring bucket policies to allow public access to website files.
    Optional: Security considerations and how to restrict access if needed.

9. Step 7: Testing Your Deployment

    Accessing your Hugo website using the bucket URL.
    Checking for common issues (e.g., missing files, incorrect configurations).

10. Optional: Set Up a Custom Domain (if applicable)

    Registering a custom domain with Route 53 or another registrar.
    Configuring DNS settings for S3.
    Configuring HTTPS using AWS Certificate Manager and CloudFront (optional).

11. Conclusion

    Recap of the deployment process.
    Advantages of using S3 for hosting static sites.
    Encouragement to explore further enhancements (e.g., using CloudFront for CDN capabilities).
