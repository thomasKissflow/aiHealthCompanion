"""
Amazon Transcribe API Integration
Provides endpoints for real-time speech-to-text
"""
import os
import asyncio
import logging
from typing import Optional
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent

logger = logging.getLogger(__name__)


class SimpleTranscriptHandler(TranscriptResultStreamHandler):
    """Handler that collects final transcripts"""
    
    def __init__(self, output_stream):
        super().__init__(output_stream)
        self.transcript_parts = []
        self.final_transcript = ""
    
    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        """Handle transcript events and collect final results"""
        results = transcript_event.transcript.results
        for result in results:
            if result.alternatives and not result.is_partial:
                transcript = result.alternatives[0].transcript
                self.transcript_parts.append(transcript)
                logger.info(f"[Transcribe] Final: {transcript}")


class TranscribeService:
    """Service for Amazon Transcribe streaming"""
    
    def __init__(self, region: str = "us-east-1"):
        """
        Initialize Transcribe service
        
        Args:
            region: AWS region
        """
        self.region = region
        self.sample_rate = 16000
        logger.info(f"[Transcribe] Service initialized for region: {region}")
    
    async def transcribe_audio_stream(
        self,
        audio_chunks: list,
        language_code: str = "en-US"
    ) -> Optional[str]:
        """
        Transcribe audio chunks to text
        
        Args:
            audio_chunks: List of audio data chunks (bytes)
            language_code: Language code (default: en-US)
            
        Returns:
            Transcribed text or None if error
        """
        try:
            logger.info(f"[Transcribe] Starting transcription ({len(audio_chunks)} chunks)")
            
            # Create client
            client = TranscribeStreamingClient(region=self.region)
            
            # Start stream
            stream = await client.start_stream_transcription(
                language_code=language_code,
                media_sample_rate_hz=self.sample_rate,
                media_encoding="pcm",
            )
            
            # Create handler
            handler = SimpleTranscriptHandler(stream.output_stream)
            
            # Send audio chunks
            async def write_chunks():
                for chunk in audio_chunks:
                    await stream.input_stream.send_audio_event(audio_chunk=chunk)
                await stream.input_stream.end_stream()
            
            # Process stream
            await asyncio.gather(write_chunks(), handler.handle_events())
            
            # Get final transcript
            final_text = " ".join(handler.transcript_parts).strip()
            
            if final_text:
                logger.info(f"[Transcribe] Complete: {final_text}")
                return final_text
            else:
                logger.warning("[Transcribe] No transcript generated")
                return None
                
        except Exception as e:
            logger.error(f"[Transcribe] Error: {e}")
            return None
    
    async def transcribe_audio_bytes(
        self,
        audio_data: bytes,
        chunk_size: int = 8192
    ) -> Optional[str]:
        """
        Transcribe audio bytes to text
        
        Args:
            audio_data: Raw audio bytes (PCM 16-bit, 16kHz, mono)
            chunk_size: Size of chunks to send
            
        Returns:
            Transcribed text or None if error
        """
        # Split audio into chunks
        chunks = [
            audio_data[i:i+chunk_size]
            for i in range(0, len(audio_data), chunk_size)
        ]
        
        return await self.transcribe_audio_stream(chunks)
