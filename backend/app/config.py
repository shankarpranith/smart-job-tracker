import os

# Points to DynamoDB Local by default.
# In Phase 4 (Lambda) and real AWS deployment, this env var will be unset,
# and boto3 will automatically use the real AWS DynamoDB endpoint instead.
DYNAMODB_ENDPOINT_URL = os.getenv("DYNAMODB_ENDPOINT_URL", "http://localhost:8080")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "JobApplications")