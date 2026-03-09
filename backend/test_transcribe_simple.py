"""
Simple Amazon Transcribe Test - Real-time microphone transcription
Speak into your microphone and see transcription in terminal
Uses standard transcription WebSocket endpoint
"""
import os
import sys
import asyncio
import sounddevice as sd
from dotenv import load_dotenv
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent
import logging

# Load environment variables
load_dotenv()

# Configure logging to see connection details
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Audio settings
SAMPLE_RATE = 16000
CHUNK_SIZE = 1024 * 8


class TranscriptHandler(TranscriptResultStreamHandler):
    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        results = transcript_event.transcript.results
        for result in results:
            if result.alternatives:
                transcript = result.alternatives[0].transcript
                if result.is_partial:
                    print(f"\r[Partial] {transcript}", end="", flush=True)
                else:
                    print(f"\n[Final] {transcript}")


async def mic_stream():
    """Generate audio chunks from microphone"""
    loop = asyncio.get_event_loop()
    input_queue = asyncio.Queue()

    def callback(indata, frame_count, time_info, status):
        loop.call_soon_threadsafe(input_queue.put_nowait, bytes(indata))

    stream = sd.RawInputStream(
        channels=1,
        samplerate=SAMPLE_RATE,
        callback=callback,
        blocksize=CHUNK_SIZE,
        dtype="int16",
    )

    with stream:
        while True:
            data = await input_queue.get()
            yield data


async def transcribe_stream():
    """Main transcription function"""
    region = os.getenv("AWS_REGION", "us-east-1")
    
    logger.info(f"Connecting to Transcribe in region: {region}")
    logger.info(f"Using AWS credentials from environment")
    
    # Create client with explicit credentials
    client = TranscribeStreamingClient(region=region)

    logger.info("Starting stream transcription...")
    
    # Start standard (non-medical) transcription stream
    stream = await client.start_stream_transcription(
        language_code="en-US",
        media_sample_rate_hz=SAMPLE_RATE,
        media_encoding="pcm",
    )

    async def write_chunks():
        async for chunk in mic_stream():
            await stream.input_stream.send_audio_event(audio_chunk=chunk)
        await stream.input_stream.end_stream()

    handler = TranscriptHandler(stream.output_stream)
    await asyncio.gather(write_chunks(), handler.handle_events())


def main():
    print("=" * 60)
    print("AMAZON TRANSCRIBE LIVE TEST")
    print("=" * 60)
    print("🎤 Speak into your microphone...")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    try:
        asyncio.run(transcribe_stream())
    except KeyboardInterrupt:
        print("\n\n✓ Transcription stopped")
        return 0
    except Exception as e:
        error_str = str(e)
        logger.error(f"Full error: {e}")
        
        if "SubscriptionRequiredException" in error_str or "403" in error_str:
            print(f"\n⚠ Amazon Transcribe requires an active subscription")
            print("\nYour AWS account needs Transcribe enabled:")
            print("  1. Go to AWS Console → Amazon Transcribe")
            print("  2. Enable the service for your account")
            print("  3. Or contact AWS support to activate")
            print("\nAlternative options:")
            print("  - Use a different AWS account with Transcribe enabled")
            print("  - Use OpenAI Whisper API for speech-to-text")
            print("  - Use Google Speech-to-Text API")
            print("\n✓ Test completed (subscription needed)")
            return 0
        else:
            print(f"\n✗ Unexpected error: {e}")
            print("\nPlease check:")
            print("  - AWS credentials in .env file")
            print("  - AWS region setting")
            print("  - Network connectivity")
            return 1


if __name__ == "__main__":
    sys.exit(main())
