"""
Test direct Bedrock API call using boto3
"""
import os
import json
import boto3
from dotenv import load_dotenv

load_dotenv()

# Initialize Bedrock client
bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name=os.getenv('AWS_REGION', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

print("Testing direct Bedrock API call...")
print(f"Region: {os.getenv('AWS_REGION', 'us-east-1')}")

# List available models
print("\n=== LISTING AVAILABLE MODELS ===")
try:
    bedrock_client = boto3.client(
        service_name='bedrock',
        region_name=os.getenv('AWS_REGION', 'us-east-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    
    response = bedrock_client.list_foundation_models()
    print(f"Found {len(response['modelSummaries'])} models")
    
    # Show first few models
    for model in response['modelSummaries'][:5]:
        print(f"  - {model['modelId']}: {model.get('modelName', 'N/A')}")
    
except Exception as e:
    print(f"Error listing models: {e}")

# Try invoking with a common model
print("\n=== TESTING MODEL INVOCATION ===")
test_models = [
    "anthropic.claude-3-sonnet-20240229-v1:0",
    "anthropic.claude-v2",
    "amazon.titan-text-express-v1",
    "meta.llama3-8b-instruct-v1:0"
]

for model_id in test_models:
    print(f"\nTrying model: {model_id}")
    try:
        # Prepare request based on model type
        if "claude" in model_id:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 100,
                "messages": [
                    {"role": "user", "content": "Say hello in one sentence"}
                ]
            })
        elif "titan" in model_id:
            body = json.dumps({
                "inputText": "Say hello in one sentence",
                "textGenerationConfig": {
                    "maxTokenCount": 100,
                    "temperature": 0.7
                }
            })
        elif "llama" in model_id:
            body = json.dumps({
                "prompt": "Say hello in one sentence",
                "max_gen_len": 100,
                "temperature": 0.7
            })
        else:
            continue
        
        response = bedrock.invoke_model(
            modelId=model_id,
            body=body
        )
        
        response_body = json.loads(response['body'].read())
        print(f"✓ SUCCESS with {model_id}")
        print(f"Response: {json.dumps(response_body, indent=2)[:200]}...")
        break
        
    except Exception as e:
        print(f"✗ Failed: {e}")

print("\n=== DONE ===")
