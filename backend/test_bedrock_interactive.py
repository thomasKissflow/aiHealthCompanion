"""
Interactive Amazon Bedrock Test
Ask questions and get AI responses in terminal
"""
import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def ask_bedrock(question: str, client: OpenAI) -> str:
    """
    Ask Bedrock a question and get response
    
    Args:
        question: Question to ask
        client: OpenAI client configured for Bedrock
        
    Returns:
        AI response text
    """
    try:
        logger.info(f"Asking Bedrock: '{question}'")
        
        # Use the responses API as per AWS sample code
        response = client.responses.create(
            model="openai.gpt-oss-20b-1:0",
            input=question
        )
        
        # Extract response text
        answer = response.output[1].content[0].text
        
        logger.info("✓ Response received")
        return answer
        
    except Exception as e:
        logger.error(f"✗ Error: {e}")
        return f"Error: {e}"


def main():
    """Interactive Bedrock test"""
    print("=" * 60)
    print("AMAZON BEDROCK INTERACTIVE TEST")
    print("=" * 60)
    print("Ask questions and get AI responses.")
    print("Type 'quit' or 'exit' to stop.")
    print("=" * 60)
    print()
    
    # Initialize OpenAI client with Bedrock endpoint
    try:
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL")
        )
        logger.info("✓ Bedrock client initialized")
    except Exception as e:
        logger.error(f"✗ Failed to initialize client: {e}")
        return
    
    # Test with sample question first
    print("\n🤖 Testing with sample question...")
    sample_question = "Can you explain the features of Amazon Bedrock?"
    sample_response = ask_bedrock(sample_question, client)
    print(f"\nQuestion: {sample_question}")
    print(f"Response: {sample_response}")
    print("\n" + "=" * 60)
    
    # Interactive loop
    while True:
        try:
            # Get user input
            question = input("\nYour question: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break
            
            # Get AI response
            response = ask_bedrock(question, client)
            
            # Display response
            print(f"\n🤖 Bedrock Response:")
            print("-" * 60)
            print(response)
            print("-" * 60)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {e}")


if __name__ == "__main__":
    main()
