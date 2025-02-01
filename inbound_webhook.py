#!/usr/bin/env python3
"""
Updated inbound_webhook.py integrating ElevenLabs TTS
with proper asynchronous handling, conversation context,
and error fallbacks.
"""

import os
import json
import time
import datetime
import threading
from flask import Flask, request, Response, url_for
from twilio.twiml.voice_response import VoiceResponse, Gather
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, TimeoutError

# Import both our OpenRouter and ElevenLabs modules from our Assistant
from Assistant import OpenRouterAPI, ElevenLabsTTS

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Ensure the static directory exists (to serve synthesized audio files)
STATIC_DIR = os.path.join(os.getcwd(), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

# ----------------------------
# Global modules and conversation management
# ----------------------------

# Initialize OpenRouter API (for generating AI text)
openrouter_api = OpenRouterAPI()

# Ensure the static directory exists (to serve synthesized audio files)
STATIC_DIR = os.path.join(os.getcwd(), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

# Check for required start_audio.mp3
start_audio_path = os.path.join(STATIC_DIR, 'start_audio.mp3')
if not os.path.exists(start_audio_path):
    print(f"Warning: Required start_audio.mp3 not found at: {start_audio_path}")

# Dictionary to keep conversation history in memory per Twilio CallSid.
# (In production an external persistent store is recommended.)
conversation_history = {}

def cleanup_file_later(file_path, delay=600):
    """Delete the specified file after 'delay' seconds."""
    def remove_file():
        try:
            os.remove(file_path)
            print(f"Cleaned up audio file: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {str(e)}")
    timer = threading.Timer(delay, remove_file)
    timer.start()

def get_conversation_context(call_sid):
    """Retrieve or initialize conversation history for a call."""
    if call_sid not in conversation_history:
        conversation_history[call_sid] = []
    return conversation_history[call_sid]

def update_conversation_history(call_sid, role, content):
    """Append a message to the conversation history for this call."""
    history = get_conversation_context(call_sid)
    history.append({"role": role, "content": content})
    # Limit context to the last 5 messages
    conversation_history[call_sid] = history[-5:]

def build_prompt_from_history(call_sid):
    """Combine conversation history into a single prompt string.
    Each turn is prefixed with 'User:' or 'Assistant:'."""
    history = get_conversation_context(call_sid)
    prompt = "\n".join(f"{msg['role'].capitalize()}: {msg['content']}" for msg in history)
    return prompt

# ----------------------------
# ElevenLabs TTS Asynchronous call helper
# ----------------------------

def get_tts_audio(text):
    """
    Get the ElevenLabs audio data for the given text.
    """
    try:
        print("\nStarting ElevenLabs synthesis...")
        tts_engine = ElevenLabsTTS()
        audio_data = tts_engine.synthesize(text)
        
        if audio_data:
            # Save audio data to a temporary file
            temp_file = os.path.join(STATIC_DIR, f"response_{int(time.time())}.mp3")
            with open(temp_file, 'wb') as f:
                f.write(audio_data)
            
            # Schedule cleanup
            cleanup_file_later(temp_file)
            
            # Return path relative to static directory
            return f"/static/{os.path.basename(temp_file)}"
        else:
            print("Warning: No audio data received from synthesize()")
            return None
    except Exception as e:
        print("Error in ElevenLabs TTS synthesis:", e)
        raise

# ----------------------------
# Define our Twilio routes
# ----------------------------

@app.route("/", methods=["POST"])
def root():
    """Play welcome message and redirect to voice handler."""
    response = VoiceResponse()
    response.play('/static/start_audio.mp3')
    response.redirect("/voice")
    return Response(str(response), mimetype="application/xml")

@app.after_request
def after_request(response):
    """Bypass ngrok browser warning."""
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response

@app.route("/voice", methods=["GET", "POST"])
def voice():
    """
    Twilio calls this when a new call comes in.
    It plays the welcome message and uses <Gather> with speech input.
    """
    response = VoiceResponse()
    call_sid = request.values.get('CallSid')
    
    print("\n=== New Call Started ===")
    print(f"Call SID: {call_sid}")
    print(f"Time: {datetime.datetime.now()}")
    
    # Initialize conversation context for this call if needed
    get_conversation_context(call_sid)
    
    # Set up a Gather with speech input
    gather = Gather(input="speech", action="/process_voice", method="POST", timeout=5)
    response.append(gather)
    
    # If nothing is received, play greeting again
    response.play('/static/start_audio.mp3')
    
    # Clean up conversation history on hangup
    if call_sid in conversation_history:
        del conversation_history[call_sid]
    
    return Response(str(response), mimetype="application/xml")

@app.route("/process_voice", methods=["POST"])
def process_voice():
    """
    Receives the caller's speech, generates a reply using conversation context,
    synthesizes audio with ElevenLabs (async), and returns a TwiML response.
    """
    response = VoiceResponse()
    call_sid = request.values.get('CallSid')
    
    # Debug logging
    print("\n=== New Voice Request ===")
    print(f"Call SID: {call_sid}")
    print(f"Time: {datetime.datetime.now()}")
    
    base_url = request.host_url  # e.g. https://your-ngrok-subdomain.ngrok.io/
    speech_text = request.values.get("SpeechResult", "").strip()
    
    if not speech_text:
        print("No speech detected in request")
        response.redirect("/voice")
        return Response(str(response), mimetype="application/xml")
    
    try:
        # Update conversation with user's input
        print(f"\nUser Speech: {speech_text}")
        update_conversation_history(call_sid, "user", speech_text)
        
        # Check if the conversation should end
        if any(exit_word in speech_text.lower() for exit_word in ["goodbye", "bye", "exit", "quit"]):
            print("Exit word detected, ending call")
            response.play('/static/goodbye_audio.mp3')  # Optional: custom goodbye message
            response.hangup()
            if call_sid in conversation_history:
                del conversation_history[call_sid]
            return Response(str(response), mimetype="application/xml")
        
        # Build the prompt from conversation history to provide context
        prompt = build_prompt_from_history(call_sid)
        
        # Generate AI reply from OpenRouter API using the full conversation context
        try:
            print(f"\nGenerating AI response...")
            print(f"Prompt context:\n{prompt}")
            ai_reply = openrouter_api.generate_text(prompt)
            print(f"AI Response: {ai_reply}")
        except Exception as e:
            error_text = "I'm sorry, I'm having trouble understanding you right now. Please try again later."
            response.say("We're experiencing technical difficulties. Please try again.")
            print("Error from OpenRouter API:", e)
            response.hangup()
            return Response(str(response), mimetype="application/xml")
        
        # Update conversation history with the assistant's reply
        update_conversation_history(call_sid, "assistant", ai_reply)
        
        # Use asynchronous call to ElevenLabs TTS to synthesize the response
        audio_url = None
        try:
            print("\nStarting ElevenLabs synthesis...")
            print(f"Audio synthesis complete. URL: {audio_url}")
        except TimeoutError:
            print("ElevenLabs TTS synthesis timed out.")
        except Exception as e:
            print("Exception during TTS synthesis:", e)
        
        # Get TTS audio
        try:
            print("\nStarting TTS stream synthesis...")
            tts_engine = ElevenLabsTTS()
            audio_stream = tts_engine.synthesize(ai_reply)
            
            # Save audio stream to temporary file
            temp_file = os.path.join(STATIC_DIR, f"response_{int(time.time())}.mp3")
            with open(temp_file, 'wb') as f:
                for chunk in audio_stream:
                    if isinstance(chunk, bytes):
                        f.write(chunk)
            
            # Schedule cleanup
            cleanup_file_later(temp_file)
            
            # Play the temporary file
            response.play(url_for('static', filename=os.path.basename(temp_file)))
                
        except Exception as e:
            print(f"Error getting TTS stream: {str(e)}")
            print(f"Error type: {type(e)}")
            raise  # Re-raise to fail the request - no fallback
        
        response.pause(length=1)
        
        # Ask the caller if they have another question using a new Gather
        gather = Gather(input="speech", action="/process_voice", method="POST", timeout=5)
        response.say("Do you need any other assistance?")
        response.append(gather)
        
    except Exception as e:
        print("Unexpected error in process_voice:", e)
        response.play('/static/error_audio.mp3')  # Optional: custom error message
        response.hangup()
    
    return Response(str(response), mimetype="application/xml")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
