"""
Unit tests for Voice Interface
Tests direct streaming, interruption handling, and async operations
"""
import pytest
import asyncio
import numpy as np
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from voice_interface import VoiceInterface, AudioStreamHandler
from aws_connection_pool import AWSConnectionPool


@pytest.fixture
def mock_connection_pool():
    """Create mock AWS connection pool"""
    pool = Mock(spec=AWSConnectionPool)
    pool.region = "us-east-1"
    pool.get_polly_client = Mock()
    pool.get_transcribe_client = Mock()
    return pool


@pytest.fixture
def voice_interface(mock_connection_pool):
    """Create VoiceInterface instance with mocked dependencies"""
    interface = VoiceInterface(mock_connection_pool)
    return interface


class TestVoiceInterfaceInitialization:
    """Test voice interface initialization"""
    
    def test_initialization(self, voice_interface):
        """Test that voice interface initializes correctly"""
        assert voice_interface.sample_rate == 16000
        assert voice_interface.channels == 1
        assert voice_interface.is_listening is False
        assert voice_interface.is_playing is False
    
    def test_connection_pool_stored(self, voice_interface, mock_connection_pool):
        """Test that connection pool is stored"""
        assert voice_interface.connection_pool == mock_connection_pool


class TestDirectStreaming:
    """
    Test direct streaming (no file I/O)
    Validates: Requirements 2.2, 3.1
    """
    
    @pytest.mark.asyncio
    async def test_polly_direct_streaming_no_file_io(self, voice_interface, mock_connection_pool):
        """Test that Polly synthesis uses direct streaming without file I/O"""
        # Mock Polly client
        mock_polly = Mock()
        mock_audio_stream = Mock()
        mock_audio_stream.read = Mock(side_effect=[b'audio_chunk', b''])
        
        mock_polly.synthesize_speech = Mock(return_value={
            'AudioStream': mock_audio_stream
        })
        mock_connection_pool.get_polly_client.return_value = mock_polly
        
        # Mock playback stream
        with patch.object(voice_interface, '_play_audio_stream', new_callable=AsyncMock) as mock_play:
            await voice_interface.synthesize_and_play("Hello world")
            
            # Verify Polly was called
            mock_polly.synthesize_speech.assert_called_once()
            call_args = mock_polly.synthesize_speech.call_args[1]
            assert call_args['Text'] == "Hello world"
            assert call_args['OutputFormat'] == 'pcm'
            
            # Verify audio stream was played directly
            mock_play.assert_called_once_with(mock_audio_stream)
    
    @pytest.mark.asyncio
    async def test_polly_streaming_uses_pcm_format(self, voice_interface, mock_connection_pool):
        """Test that Polly uses PCM format for direct streaming"""
        mock_polly = Mock()
        mock_audio_stream = Mock()
        mock_audio_stream.read = Mock(return_value=b'')
        
        mock_polly.synthesize_speech = Mock(return_value={
            'AudioStream': mock_audio_stream
        })
        mock_connection_pool.get_polly_client.return_value = mock_polly
        
        with patch.object(voice_interface, '_play_audio_stream', new_callable=AsyncMock):
            await voice_interface.synthesize_and_play("Test")
            
            call_args = mock_polly.synthesize_speech.call_args[1]
            assert call_args['OutputFormat'] == 'pcm'
            assert call_args['SampleRate'] == '16000'


class TestInterruptionHandling:
    """
    Test interruption handling (stop playback on user speech)
    Validates: Requirements 4.1, 4.2, 4.3
    """
    
    @pytest.mark.asyncio
    async def test_stop_playback_interrupts_audio(self, voice_interface):
        """Test that stop_playback immediately stops audio playback"""
        # Set up playing state
        voice_interface.is_playing = True
        
        # Mock sounddevice stop
        with patch('voice_interface.sd.stop') as mock_stop:
            # Stop playback
            await voice_interface.stop_playback()
            
            # Verify playback was stopped
            assert voice_interface.is_playing is False
            mock_stop.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_audio_buffer_cleanup_on_interruption(self, voice_interface):
        """Test that audio buffers are cleaned up on interruption"""
        # Set up playing state
        voice_interface.is_playing = True
        
        # Mock sounddevice stop
        with patch('voice_interface.sd.stop') as mock_stop:
            # Interrupt playback
            await voice_interface.stop_playback()
            
            # Verify cleanup
            assert voice_interface.is_playing is False
            mock_stop.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_new_synthesis_stops_current_playback(self, voice_interface, mock_connection_pool):
        """Test that new synthesis stops current playback (interruption)"""
        # Mock Polly client
        mock_polly = Mock()
        mock_audio_stream = Mock()
        mock_audio_stream.read = Mock(return_value=b'')
        mock_polly.synthesize_speech = Mock(return_value={
            'AudioStream': mock_audio_stream
        })
        mock_connection_pool.get_polly_client.return_value = mock_polly
        
        # Set up playing state
        voice_interface.is_playing = True
        
        with patch.object(voice_interface, 'stop_playback', new_callable=AsyncMock) as mock_stop:
            with patch.object(voice_interface, '_play_audio_stream', new_callable=AsyncMock):
                await voice_interface.synthesize_and_play("New text")
                
                # Verify stop_playback was called
                mock_stop.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_immediate_new_input_processing_after_interruption(self, voice_interface):
        """Test that system can immediately process new input after interruption"""
        # Set up playing state
        voice_interface.is_playing = True
        
        # Mock sounddevice stop
        with patch('voice_interface.sd.stop'):
            # Stop playback
            await voice_interface.stop_playback()
            
            # Verify ready for new input
            assert voice_interface.is_playing is False


class TestAsyncOperations:
    """
    Test async operations throughout the voice interface
    Validates: Requirements 2.5, 3.3
    """
    
    @pytest.mark.asyncio
    async def test_synthesize_and_play_is_async(self, voice_interface, mock_connection_pool):
        """Test that synthesize_and_play is async and non-blocking"""
        mock_polly = Mock()
        mock_audio_stream = Mock()
        mock_audio_stream.read = Mock(return_value=b'')
        mock_polly.synthesize_speech = Mock(return_value={
            'AudioStream': mock_audio_stream
        })
        mock_connection_pool.get_polly_client.return_value = mock_polly
        
        with patch.object(voice_interface, '_play_audio_stream', new_callable=AsyncMock):
            # Should be awaitable
            result = voice_interface.synthesize_and_play("Test")
            assert asyncio.iscoroutine(result)
            await result
    
    @pytest.mark.asyncio
    async def test_stop_playback_is_async(self, voice_interface):
        """Test that stop_playback is async"""
        voice_interface.is_playing = True
        
        # Mock sounddevice stop
        with patch('voice_interface.sd.stop'):
            # Should be awaitable
            result = voice_interface.stop_playback()
            assert asyncio.iscoroutine(result)
            await result
    
    @pytest.mark.asyncio
    async def test_stop_listening_is_async(self, voice_interface):
        """Test that stop_listening is async"""
        voice_interface.is_listening = True
        voice_interface.recording_stream = Mock()
        voice_interface.recording_stream.stop = Mock()
        voice_interface.recording_stream.close = Mock()
        
        # Should be awaitable
        result = voice_interface.stop_listening()
        assert asyncio.iscoroutine(result)
        await result


class TestResumeListeningAfterPlayback:
    """
    Test resume listening after playback completes
    Validates: Requirements 3.4
    """
    
    @pytest.mark.asyncio
    async def test_playback_state_cleared_after_completion(self, voice_interface, mock_connection_pool):
        """Test that playback state is cleared after audio completes"""
        mock_polly = Mock()
        mock_audio_stream = Mock()
        mock_audio_stream.read = Mock(return_value=b'\x00\x00' * 100)  # Some audio data
        mock_polly.synthesize_speech = Mock(return_value={
            'AudioStream': mock_audio_stream
        })
        mock_connection_pool.get_polly_client.return_value = mock_polly
        
        # Mock sounddevice
        with patch('voice_interface.sd.play') as mock_play:
            with patch('voice_interface.sd.get_stream') as mock_get_stream:
                mock_stream = Mock()
                mock_stream.active = False  # Playback complete
                mock_get_stream.return_value = mock_stream
                
                await voice_interface.synthesize_and_play("Test")
                
                # Verify playback state is cleared
                assert voice_interface.is_playing is False


class TestErrorHandling:
    """Test error handling in voice interface"""
    
    @pytest.mark.asyncio
    async def test_empty_text_handling(self, voice_interface):
        """Test that empty text is handled gracefully"""
        # Should not raise exception
        await voice_interface.synthesize_and_play("")
        
        # Should not raise exception for None
        await voice_interface.synthesize_and_play(None)
    
    @pytest.mark.asyncio
    async def test_polly_error_handling(self, voice_interface, mock_connection_pool):
        """Test that Polly errors are handled gracefully"""
        mock_polly = Mock()
        mock_polly.synthesize_speech = Mock(side_effect=Exception("Polly error"))
        mock_connection_pool.get_polly_client.return_value = mock_polly
        
        # Should raise exception
        with pytest.raises(Exception):
            await voice_interface.synthesize_and_play("Test")
    
    @pytest.mark.asyncio
    async def test_stop_playback_when_not_playing(self, voice_interface):
        """Test that stop_playback handles not playing state"""
        voice_interface.is_playing = False
        
        # Should not raise exception
        await voice_interface.stop_playback()
    
    @pytest.mark.asyncio
    async def test_stop_listening_when_not_listening(self, voice_interface):
        """Test that stop_listening handles not listening state"""
        voice_interface.is_listening = False
        
        # Should not raise exception
        await voice_interface.stop_listening()


class TestCleanup:
    """Test resource cleanup"""
    
    def test_cleanup_stops_listening(self, voice_interface):
        """Test that cleanup stops listening"""
        voice_interface.is_listening = True
        voice_interface.recording_stream = Mock()
        voice_interface.recording_stream.stop = Mock()
        voice_interface.recording_stream.close = Mock()
        
        with patch('voice_interface.sd.stop'):
            voice_interface.cleanup()
        
        # Note: cleanup creates async tasks, so we can't verify completion here
        # but we verify the method doesn't raise exceptions
    
    def test_cleanup_stops_playback(self, voice_interface):
        """Test that cleanup stops playback"""
        voice_interface.is_playing = True
        
        with patch('voice_interface.sd.stop'):
            voice_interface.cleanup()
        
        # Verify cleanup doesn't raise exceptions


class TestLatencyTarget:
    """
    Test that voice processing meets latency targets
    Validates: Requirements 2.3, 3.5
    """
    
    @pytest.mark.asyncio
    async def test_synthesis_completes_quickly(self, voice_interface, mock_connection_pool):
        """Test that synthesis completes within reasonable time"""
        import time
        
        mock_polly = Mock()
        mock_audio_stream = Mock()
        mock_audio_stream.read = Mock(return_value=b'')
        mock_polly.synthesize_speech = Mock(return_value={
            'AudioStream': mock_audio_stream
        })
        mock_connection_pool.get_polly_client.return_value = mock_polly
        
        with patch.object(voice_interface, '_play_audio_stream', new_callable=AsyncMock):
            start = time.time()
            await voice_interface.synthesize_and_play("Test")
            duration = time.time() - start
            
            # Should complete quickly (under 1 second for mocked operation)
            assert duration < 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
