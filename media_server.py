import asyncio
import base64
import json
import time
from typing import Dict, List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
import uvicorn

# Import our API modules
from Assistant import OpenRouterAPI, ElevenLabsTTS

app = FastAPI()

# Global conversation context by call SID
conversation_history: Dict[str, List[Dict[str, str]]] = {}

# Initialize AI and TTS modules
openrouter_api = OpenRouterAPI()
tts_engine = ElevenLabsTTS()

# Audio buffer settings
AUDIO_BUFFER_TIME = 3.0  # seconds

async def transcribe_audio(audio_bytes: bytes) -> str:
    """Placeholder for real-time speech-to-text.
    In production, integrate with a streaming STT service."""
    await asyncio.sleep(0.5)
    # Simulate transcription - replace with real STT service
    return "simulated transcription"

def update_conversation_history(call_sid: str, role: str, content: str) -> None:
    """Update conversation history for a call."""
    if call_sid not in conversation_history:
        conversation_history[call_sid] = []
    conversation_history[call_sid].append({"role": role, "content": content})
    # Limit conversation to last 5 turns
    conversation_history[call_sid] = conversation_history[call_sid][-5:]

@app.websocket("/media")
async def media_ws(websocket: WebSocket):
    """Handle WebSocket connection for Twilio Media Streams."""
    await websocket.accept()
    
    # Get CallSid from query params
    params = websocket.query_params
    call_sid = params.get("CallSid", f"anonymous-{int(time.time())}")
    print(f"New media stream connected for CallSid: {call_sid}")
    
    # Initialize conversation history
    if call_sid not in conversation_history:
        conversation_history[call_sid] = []
    
    # Create queue for audio chunks
    audio_queue = asyncio.Queue()
    
    # Start STT processing task
    stt_task = asyncio.create_task(stt_worker(call_sid, audio_queue, websocket))
    
    try:
        while True:
            # Read incoming messages from Twilio
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("event") == "media":
                media = message.get("media", {})
                payload = media.get("payload", "")
                # Convert base64 payload to bytes
                audio_bytes = base64.b64decode(payload)
                # Queue the audio chunk
                await audio_queue.put(audio_bytes)
                
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for CallSid: {call_sid}")
    finally:
        stt_task.cancel()
        # Cleanup conversation context
        if call_sid in conversation_history:
            del conversation_history[call_sid]

async def stt_worker(call_sid: str, audio_queue: asyncio.Queue, websocket: WebSocket):
    """Process audio chunks and generate responses."""
    audio_buffer = bytearray()
    last_buffer_time = time.time()
    
    while True:
        try:
            # Wait for next audio chunk
            audio_chunk = await asyncio.wait_for(audio_queue.get(), timeout=AUDIO_BUFFER_TIME)
            audio_buffer.extend(audio_chunk)
            
        except asyncio.TimeoutError:
            if len(audio_buffer) == 0:
                continue
                
        # Process buffer if enough time has passed
        current_time = time.time()
        if current_time - last_buffer_time >= AUDIO_BUFFER_TIME and len(audio_buffer) > 0:
            try:
                # Transcribe audio
                transcription = await transcribe_audio(bytes(audio_buffer))
                
                if transcription.strip():
                    print(f"CallSid {call_sid} transcribed: {transcription}")
                    update_conversation_history(call_sid, "user", transcription)
                    
                    # Build prompt with context
                    prompt = "\n".join(f"{msg['role'].capitalize()}: {msg['content']}" 
                                     for msg in conversation_history[call_sid])
                    
                    # Generate AI response
                    ai_reply = openrouter_api.generate_text(prompt)
                    print(f"CallSid {call_sid} AI reply: {ai_reply}")
                    update_conversation_history(call_sid, "assistant", ai_reply)
                    
                    # Synthesize voice response
                    try:
                        audio_stream = tts_engine.synthesize(ai_reply)
                        
                        # Stream audio back in chunks
                        chunk_size = 1024
                        for chunk in audio_stream:
                            if isinstance(chunk, bytes):
                                # Send chunks as media messages
                                out_message = {
                                    "event": "media",
                                    "media": {
                                        "payload": base64.b64encode(chunk).decode("utf-8"),
                                        "track": "outbound"
                                    }
                                }
                                await websocket.send_text(json.dumps(out_message))
                                await asyncio.sleep(0.02)  # Control streaming rate
                                
                        # No prompt for more input - just continue listening
                    except Exception as tts_error:
                        print(f"Error synthesizing TTS response: {tts_error}")
                        
                # Reset buffer
                audio_buffer = bytearray()
                last_buffer_time = current_time
                
            except Exception as stt_error:
                print(f"Error during STT processing for CallSid {call_sid}: {stt_error}")
                audio_buffer = bytearray()
                last_buffer_time = current_time

if __name__ == "__main__":
    uvicorn.run("media_server:app", host="0.0.0.0", port=5000, reload=True)
