"""
Interactive Amazon Transcribe Test
Speak into your microphone and see the transcription in terminal
"""
import os
import sys
import time
import json
from dotenv import load_dotenv
from aws_connection_pool import AWSConnectionPool
import logging
import subprocess
import tempfile
import uuid

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def record_audio(duration: int = 5) -> str:
    """
    Record audio from microphone
    
    Args:
        duration: Recording duration in seconds
        
    Returns:
        Path to recorded audio file
    """
    temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    temp_file_path = temp_file.name
    temp_file.close()
    
    logger.info(f"Recording for {duration} seconds...")
    print(f"\n🎤 RECORDING NOW - Speak into your microphone! ({duration} seconds)")
    
    # Record audio using macOS 'sox' or 'rec' command
    # If sox is not installed, we'll use a Python library
    try:
        # Try using sox (if installed: brew install sox)
        subprocess.run([
            'rec', '-r', '16000', '-c', '1', '-b', '16',
            temp_file_path, 'trim', '0', str(duration)
        ], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback: Use Python's sounddevice and scipy
        try:
            import sounddevice as sd
            import scipy.io.wavfile as wav
            
            sample_rate = 16000
            recording = sd.rec(int(duration * sample_rate), 
                             samplerate=sample_rate, 
                             channels=1, 
                             dtype='int16')
            sd.wait()
            wav.write(temp_file_path, sample_rate, recording)
        except ImportError:
            logger.error("Please install sox (brew install sox) or sounddevice (pip install sounddevice scipy)")
            raise
    
    logger.info("✓ Recording complete")
    return temp_file_path


def transcribe_audio(audio_file_path: str, pool: AWSConnectionPool) -> str:
    """
    Transcribe audio file using Amazon Transcribe
    
    Args:
        audio_file_path: Path to audio file
        pool: AWS connection pool
        
    Returns:
        Transcribed text
    """
    try:
        transcribe_client = pool.get_transcribe_client()
        s3_client = pool._get_s3_client()  # We'll need S3 for Transcribe
        
        # Generate unique job name
        job_name = f"transcribe-test-{uuid.uuid4().hex[:8]}"
        bucket_name = os.getenv("S3_BUCKET_NAME", "ai-health-companion-temp")
        s3_key = f"transcribe/{job_name}.wav"
        
        logger.info("Uploading audio to S3...")
        
        # Upload to S3
        with open(audio_file_path, 'rb') as audio_file:
            s3_client.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=audio_file
            )
        
        logger.info("Starting transcription job...")
        
        # Start transcription job
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': f's3://{bucket_name}/{s3_key}'},
            MediaFormat='wav',
            LanguageCode='en-US'
        )
        
        # Wait for completion
        logger.info("Waiting for transcription to complete...")
        while True:
            status = transcribe_client.get_transcription_job(
                TranscriptionJobName=job_name
            )
            job_status = status['TranscriptionJob']['TranscriptionJobStatus']
            
            if job_status in ['COMPLETED', 'FAILED']:
                break
            
            time.sleep(2)
        
        if job_status == 'COMPLETED':
            # Get transcript
            transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
            import urllib.request
            with urllib.request.urlopen(transcript_uri) as response:
                transcript_data = json.loads(response.read())
                transcript_text = transcript_data['results']['transcripts'][0]['transcript']
            
            # Cleanup
            s3_client.delete_object(Bucket=bucket_name, Key=s3_key)
            transcribe_client.delete_transcription_job(TranscriptionJobName=job_name)
            
            return transcript_text
        else:
            raise Exception("Transcription job failed")
            
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        logger.info("Note: Transcribe requires S3 bucket and may need subscription")
        raise


def simple_transcribe_test(pool: AWSConnectionPool):
    """
    Simplified test that just checks if Transcribe client works
    """
    try:
        transcribe_client = pool.get_transcribe_client()
        
        # List recent jobs to verify connectivity
        response = transcribe_client.list_transcription_jobs(MaxResults=1)
        
        logger.info("✓ Transcribe client is working")
        logger.info("Note: Full transcription requires S3 bucket setup and subscription")
        logger.info("For now, we've verified the client connection is successful")
        
        return True
    except Exception as e:
        logger.error(f"✗ Transcribe test failed: {e}")
        return False


def main():
    """Interactive Transcribe test"""
    print("=" * 60)
    print("AMAZON TRANSCRIBE INTERACTIVE TEST")
    print("=" * 60)
    print("This test will verify Transcribe connectivity.")
    print("Full audio transcription requires S3 bucket setup.")
    print("=" * 60)
    print()
    
    # Initialize AWS connection pool
    pool = AWSConnectionPool()
    
    # Run simplified test
    logger.info("Testing Transcribe connectivity...")
    simple_transcribe_test(pool)
    
    print("\n" + "=" * 60)
    print("For full audio transcription:")
    print("1. Set up an S3 bucket")
    print("2. Add S3_BUCKET_NAME to .env file")
    print("3. Ensure Transcribe subscription is active")
    print("=" * 60)


if __name__ == "__main__":
    main()
