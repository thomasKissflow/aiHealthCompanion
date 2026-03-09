"""
Interactive Amazon Polly Test
Type text and hear it spoken through your speakers
"""
import os
import sys
from dotenv import load_dotenv
from aws_connection_pool import AWSConnectionPool
import logging
import subprocess
import tempfile

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def speak_text(text: str, pool: AWSConnectionPool):
    """
    Convert text to speech and play through speakers
    
    Args:
        text: Text to speak
        pool: AWS connection pool
    """
    try:
        polly_client = pool.get_polly_client()
        
        logger.info(f"Converting to speech: '{text}'")
        
        # Synthesize speech
        response = polly_client.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId='Joanna',  # Female voice
            Engine='neural'     # High quality neural voice
        )
        
        # Get audio stream
        audio_stream = response['AudioStream'].read()
        logger.info(f"Generated {len(audio_stream)} bytes of audio")
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
            temp_audio.write(audio_stream)
            temp_file_path = temp_audio.name
        
        logger.info("Playing audio through speakers...")
        
        # Play audio using macOS 'afplay' command
        subprocess.run(['afplay', temp_file_path], check=True)
        
        # Clean up temp file
        os.remove(temp_file_path)
        
        logger.info("✓ Audio playback complete")
        
    except Exception as e:
        logger.error(f"✗ Error: {e}")


def main():
    """Interactive Polly test"""
    print("=" * 60)
    print("AMAZON POLLY INTERACTIVE TEST")
    print("=" * 60)
    print("Type text and press Enter to hear it spoken.")
    print("Type 'quit' or 'exit' to stop.")
    print("=" * 60)
    print()
    
    # Initialize AWS connection pool
    pool = AWSConnectionPool()
    
    while True:
        try:
            # Get user input
            text = input("Enter text to speak: ").strip()
            
            if not text:
                continue
            
            if text.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break
            
            # Speak the text
            speak_text(text, pool)
            print()
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print()


if __name__ == "__main__":
    main()
