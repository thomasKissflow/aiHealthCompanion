"""
Voice API Endpoints for AI Health Companion
Provides WebSocket endpoint for real-time voice interaction
"""
import asyncio
import logging
import json
from fastapi import WebSocket, WebSocketDisconnect
from voice_interface import VoiceInterface
from aws_connection_pool import AWSConnectionPool

logger = logging.getLogger(__name__)


class VoiceSession:
    """Manages a voice conversation session"""
    
    def __init__(self, websocket: WebSocket, voice_interface: VoiceInterface, supervisor_agent, session):
        self.websocket = websocket
        self.voice_interface = voice_interface
        self.supervisor_agent = supervisor_agent
        self.session = session
        self.is_active = True
        
    async def handle_transcription(self, text: str):
        """Handle transcribed text from user"""
        if not text or not text.strip():
            return
            
        logger.info(f"[Voice Session] Transcribed: {text}")
        
        # Send transcription to frontend
        await self.websocket.send_json({
            "type": "transcription",
            "text": text
        })
        
        # Process query through supervisor
        try:
            response = await self.supervisor_agent.process_query(text, self.session)
            
            if response:
                # Send response text to frontend
                await self.websocket.send_json({
                    "type": "response",
                    "text": response
                })
                
                # Synthesize and play response
                await self.voice_interface.synthesize_and_play(response)
                
        except Exception as e:
            logger.error(f"[Voice Session] Error processing query: {e}")
            await self.websocket.send_json({
                "type": "error",
                "message": "Error processing your request"
            })
    
    async def start(self):
        """Start voice session"""
        logger.info("[Voice Session] Starting voice session")
        
        # Start listening with callback
        await self.voice_interface.start_listening(
            callback=self.handle_transcription
        )
        
        # Send ready signal
        await self.websocket.send_json({
            "type": "ready",
            "message": "Voice interface ready"
        })
    
    async def stop(self):
        """Stop voice session"""
        logger.info("[Voice Session] Stopping voice session")
        self.is_active = False
        await self.voice_interface.stop_listening()
        await self.voice_interface.stop_playback()


async def handle_voice_websocket(
    websocket: WebSocket,
    connection_pool: AWSConnectionPool,
    supervisor_agent,
    session
):
    """
    Handle WebSocket connection for voice interaction
    
    Args:
        websocket: WebSocket connection
        connection_pool: AWS connection pool
        supervisor_agent: Supervisor agent for query processing
        session: User session
    """
    await websocket.accept()
    logger.info("[Voice API] WebSocket connection accepted")
    
    # Create voice interface
    voice_interface = VoiceInterface(connection_pool)
    
    # Create voice session
    voice_session = VoiceSession(
        websocket=websocket,
        voice_interface=voice_interface,
        supervisor_agent=supervisor_agent,
        session=session
    )
    
    try:
        # Start voice session
        await voice_session.start()
        
        # Keep connection alive and handle messages
        while voice_session.is_active:
            try:
                # Receive messages from frontend
                data = await websocket.receive_json()
                
                message_type = data.get("type")
                
                if message_type == "stop":
                    # User requested to stop
                    await voice_session.stop()
                    break
                    
                elif message_type == "mute":
                    # Mute microphone
                    await voice_interface.stop_listening()
                    await websocket.send_json({
                        "type": "status",
                        "message": "Microphone muted"
                    })
                    
                elif message_type == "unmute":
                    # Unmute microphone
                    await voice_interface.start_listening(
                        callback=voice_session.handle_transcription
                    )
                    await websocket.send_json({
                        "type": "status",
                        "message": "Microphone unmuted"
                    })
                    
                elif message_type == "interrupt":
                    # User interrupted - stop playback
                    await voice_interface.stop_playback()
                    await websocket.send_json({
                        "type": "status",
                        "message": "Playback interrupted"
                    })
                    
            except WebSocketDisconnect:
                logger.info("[Voice API] WebSocket disconnected")
                break
                
            except Exception as e:
                logger.error(f"[Voice API] Error handling message: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
                
    except Exception as e:
        logger.error(f"[Voice API] Error in voice session: {e}")
        
    finally:
        # Cleanup
        await voice_session.stop()
        voice_interface.cleanup()
        logger.info("[Voice API] Voice session ended")
