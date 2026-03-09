"""
Simple Amazon Polly Test - Speaks a predefined message
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

# Text to speak - CHANGE THIS TO TEST DIFFERENT TEXT
TEXT_TO_SPEAK = "Hello! This is a test of Amazon Polly. The AI Health Companion is working perfectly."

def main():
    """Test Polly with predefined text"""
    print("=" * 60)
    print("AMAZON POLLY SIMPLE TEST")
    print("=" * 60)
    print(f"Text to speak: {TEXT_TO_SPEAK}")
    print("=" * 60)
    print()
    
    try:
        # Initialize AWS connection pool
        pool = AWSConnectionPool()
        polly_client = pool.get_polly_client()
        
        logger.info("Converting text to speech...")
        
        # Synthesize speech
        response = polly_client.synthesize_speech(
            Text=TEXT_TO_SPEAK,
            OutputFormat='mp3',
            VoiceId='Joanna',  # Female voice
            Engine='neural'     # High quality neural voice
        )
        
        # Get audio stream
        audio_stream = response['AudioStream'].read()
        logger.info(f"✓ Generated {len(audio_stream)} bytes of audio")
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
            temp_audio.write(audio_stream)
            temp_file_path = temp_audio.name
        
        logger.info("🔊 Playing audio through speakers...")
        print("\n🔊 LISTEN TO YOUR SPEAKERS!\n")
        
        # Play audio using macOS 'afplay' command
        subprocess.run(['afplay', temp_file_path], check=True)
        
        # Clean up temp file
        os.remove(temp_file_path)
        
        logger.info("✓ Audio playback complete")
        print("\n✓ Test completed successfully!")
        
    except Exception as e:
        logger.error(f"✗ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
