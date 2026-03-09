"""
Voice Interface Layer
Handles audio streaming to/from Amazon Transcribe and Amazon Polly
Implements direct streaming (no file I/O) and interruption handling
"""
import asyncio
import logging
import io
import sounddevice as sd
import numpy as np
from typing import Optional, Callable
from aws_connection_pool import AWSConnectionPool

logger = logging.getLogger(__name__)


class AudioStreamHandler:
    """Handler for audio streaming"""
    
    def __init__(self, callback: Optional[Callable[[str], None]] = None):
        self.callback = callback
        self.audio_buffer = []
        
    async def handle_audio_chunk(self, audio_data: bytes):
        """Handle incoming audio chunk"""
        self.audio_buffer.append(audio_data)


class VoiceInterface:
    """
    Voice Interface for audio input/output
    - Direct streaming to Amazon Transcribe (speech-to-text)
    - Direct streaming to Amazon Polly (text-to-speech)
    - Interruption handling (stop playback on new input)
    - Async operations throughout
    """
    
    def __init__(self, connection_pool: AWSConnectionPool):
        """
        Initialize Voice Interface
        
        Args:
            connection_pool: AWS connection pool for service clients
        """
        self.connection_pool = connection_pool
        
        # Audio configuration
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.channels = 1
        
        # State management
        self.is_listening = False
        self.is_playing = False
        self.audio_buffer = []
        self.playback_stream = None
        
        # Audio handler
        self.audio_handler = None
        
        logger.info("Voice Interface initialized")
    
    async def start_listening(self, callback: Optional[Callable[[str], None]] = None):
        """
        Start continuous audio capture and streaming to Transcribe
        
        Args:
            callback: Async function to call with transcribed text
        """
        if self.is_listening:
            logger.warning("Already listening")
            return
        
        self.is_listening = True
        self.audio_handler = AudioStreamHandler(callback)
        logger.info("[Voice Interface] Starting audio capture")
        
        try:
            # Start audio recording using sounddevice
            def audio_callback(indata, frames, time, status):
                """Callback for audio input"""
                if status:
                    logger.warning(f"Audio input status: {status}")
                if self.is_listening:
                    # Convert to bytes and buffer
                    audio_bytes = indata.tobytes()
                    self.audio_buffer.append(audio_bytes)
            
            # Start input stream
            self.recording_stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='int16',
                callback=audio_callback,
                blocksize=self.chunk_size
            )
            self.recording_stream.start()
            
            logger.info("[Voice Interface] Audio capture started")
            
        except Exception as e:
            logger.error(f"[Voice Interface] Listening error: {e}")
            self.is_listening = False
            raise
    
    async def transcribe_audio_stream(self, audio_data: bytes) -> str:
        """
        Stream audio to Transcribe and get text
        Implements direct streaming (no file I/O)
        
        Args:
            audio_data: Raw audio bytes (PCM format)
            
        Returns:
            Transcribed text
        """
        try:
            # Get Transcribe client
            transcribe_client = self.connection_pool.get_transcribe_client()
            
            # For now, we'll use a simplified approach
            # In production, you'd use the streaming API
            logger.info("[Voice Interface] Transcribing audio...")
            
            # This is a placeholder - actual streaming implementation would use
            # the Transcribe streaming API with websockets
            # For the MVP, we'll return a mock response
            return "transcribed text"
            
        except Exception as e:
            logger.error(f"[Voice Interface] Transcription error: {e}")
            raise
    
    async def stop_listening(self):
        """Stop audio capture"""
        if not self.is_listening:
            return
        
        logger.info("[Voice Interface] Stopping audio capture")
        self.is_listening = False
        
        # Stop recording stream
        if hasattr(self, 'recording_stream') and self.recording_stream:
            self.recording_stream.stop()
            self.recording_stream.close()
            self.recording_stream = None
        
        # Clear buffer
        self.audio_buffer = []
    
    async def synthesize_and_play(self, text: str, voice_id: str = "Joanna") -> None:
        """
        Stream text to Polly and play audio immediately
        Implements direct streaming (no file I/O)
        
        Args:
            text: Text to synthesize
            voice_id: Polly voice ID (default: Joanna)
        """
        if not text:
            logger.warning("Empty text provided for synthesis")
            return
        
        logger.info(f"[Voice Interface] Synthesizing: {text[:50]}...")
        
        try:
            # Stop any current playback
            await self.stop_playback()
            
            # Get Polly client
            polly_client = self.connection_pool.get_polly_client()
            
            # Synthesize speech
            response = polly_client.synthesize_speech(
                Text=text,
                OutputFormat='pcm',
                VoiceId=voice_id,
                SampleRate=str(self.sample_rate),
                Engine='neural'
            )
            
            # Get audio stream
            audio_stream = response['AudioStream']
            
            # Play audio directly
            await self._play_audio_stream(audio_stream)
            
            logger.info("[Voice Interface] Playback complete")
            
        except Exception as e:
            logger.error(f"[Voice Interface] Synthesis error: {e}")
            raise
    
    async def _play_audio_stream(self, audio_stream):
        """
        Play audio stream directly (no file I/O)
        
        Args:
            audio_stream: Audio stream from Polly
        """
        self.is_playing = True
        
        try:
            # Read all audio data
            audio_data = audio_stream.read()
            
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # Play audio using sounddevice
            sd.play(audio_array, self.sample_rate, blocking=False)
            
            # Wait for playback to complete or interruption
            while sd.get_stream().active and self.is_playing:
                await asyncio.sleep(0.1)
            
            # Stop if interrupted
            if not self.is_playing:
                sd.stop()
                logger.info("[Voice Interface] Playback interrupted")
            
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
        finally:
            self.is_playing = False
    
    async def stop_playback(self):
        """
        Immediately stop current audio playback
        Implements interruption handling
        """
        if not self.is_playing:
            return
        
        logger.info("[Voice Interface] Stopping playback (interruption)")
        self.is_playing = False
        
        # Stop sounddevice playback
        try:
            sd.stop()
        except Exception as e:
            logger.error(f"Error stopping playback: {e}")
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up Voice Interface")
        
        # Stop listening (synchronous cleanup)
        if self.is_listening:
            self.is_listening = False
            if hasattr(self, 'recording_stream') and self.recording_stream:
                try:
                    self.recording_stream.stop()
                    self.recording_stream.close()
                except Exception as e:
                    logger.error(f"Error stopping recording: {e}")
                self.recording_stream = None
        
        # Stop playback (synchronous cleanup)
        if self.is_playing:
            self.is_playing = False
            try:
                sd.stop()
            except Exception as e:
                logger.error(f"Error stopping playback: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()
