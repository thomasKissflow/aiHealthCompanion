"""
Simple Amazon Bedrock Test - Asks a predefined question
Uses boto3 directly for Bedrock Runtime with correct message format
"""
import os
import sys
import json
from dotenv import load_dotenv
from aws_connection_pool import AWSConnectionPool
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Question to ask - CHANGE THIS TO TEST DIFFERENT QUESTIONS
QUESTION = "Can you explain the features of Amazon Bedrock in 2-3 sentences?"

def main():
    """Test Bedrock with predefined question"""
    print("=" * 60)
    print("AMAZON BEDROCK SIMPLE TEST")
    print("=" * 60)
    print(f"Question: {QUESTION}")
    print("=" * 60)
    print()
    
    try:
        # Initialize AWS connection pool
        pool = AWSConnectionPool()
        bedrock_client = pool.get_bedrock_runtime_client()
        
        logger.info("✓ Bedrock client initialized")
        logger.info("Sending request to Bedrock...")
        
        # Prepare request body with messages format (OpenAI-compatible)
        request_body = {
            "messages": [
                {
                    "role": "user",
                    "content": QUESTION
                }
            ],
            "max_tokens": 500,
            "temperature": 0.7,
            "top_p": 0.9,
        }
        
        # Invoke the model
        response = bedrock_client.invoke_model(
            modelId="openai.gpt-oss-20b-1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        
        logger.info(f"✓ Response received: {response_body}")
        
        # Extract the answer (OpenAI format)
        if 'choices' in response_body:
            answer = response_body['choices'][0]['message']['content']
        elif 'completion' in response_body:
            answer = response_body['completion']
        elif 'output' in response_body:
            answer = response_body['output']
        else:
            answer = str(response_body)
        
        print("\n🤖 BEDROCK RESPONSE:")
        print("-" * 60)
        print(answer)
        print("-" * 60)
        print("\n✓ Test completed successfully!")
        
        return 0
        
    except Exception as e:
        logger.error(f"✗ Error: {e}")
        logger.info("\nNote: This may be due to:")
        logger.info("  - Model ID not available in your region")
        logger.info("  - Model access not granted")
        logger.info("  - Incorrect model ID format")
        logger.info("\nLet's try with an available model...")
        
        # Try with Claude model
        try:
            logger.info("\nTrying with Claude Haiku model...")
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 500,
                "messages": [
                    {
                        "role": "user",
                        "content": QUESTION
                    }
                ]
            }
            
            response = bedrock_client.invoke_model(
                modelId="anthropic.claude-haiku-4-5-20251001-v1:0",
                contentType="application/json",
                accept="application/json",
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            answer = response_body['content'][0]['text']
            
            logger.info("✓ Response received from Claude")
            
            print("\n🤖 BEDROCK RESPONSE (Claude Haiku):")
            print("-" * 60)
            print(answer)
            print("-" * 60)
            print("\n✓ Test completed successfully with alternative model!")
            
            return 0
            
        except Exception as claude_error:
            logger.error(f"Claude model also failed: {claude_error}")
            return 1


if __name__ == "__main__":
    sys.exit(main())
