import os

from dotenv import load_dotenv

load_dotenv()

DYNAMODB_ENDPOINT_URL = os.getenv("DYNAMODB_ENDPOINT_URL")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "JobApplications")
S3_RESUME_BUCKET_NAME = os.getenv("S3_RESUME_BUCKET_NAME", "smart-job-tracker-resumes-shankar2026")
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN", "arn:aws:sns:us-east-1:862433051237:job-tracker-reminders")