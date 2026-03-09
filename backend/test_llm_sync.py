"""
Test Bedrock synchronously to check response time
"""
import os
import json
import boto3
import time
from dotenv import load_dotenv

load_dotenv()

client = boto3.client(
    service_name='bedrock-runtime',
    region_name=os.getenv('AWS_REGION', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

print("Testing Bedrock response time...")

body = json.dumps({
    "prompt": "User: Say hello in one sentence\n\nAssistant:",
    "max_gen_len": 100,
    "temperature": 0.7,
    "top_p": 0.9
})

start = time.time()
response = client.invoke_model(
    modelId="meta.llama3-8b-instruct-v1:0",
    body=body
)
elapsed = time.time() - start

response_body = json.loads(response['body'].read())
print(f"\nResponse time: {elapsed:.2f}s")
print(f"Response: {response_body['generation']}")
