#!/usr/bin/env python3
"""
Updated inbound_webhook.py integrating asynchronous AI processing for Twilio calls.
It now offloads AI text generation and TTS synthesis to a background thread so that
the Twilio connection is not dropped while waiting for a 5‑10 second response.
"""

import os
import json
import time
import datetime
import threading
import csv
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

# (Re)create static directory (if needed)
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

# Check for required start_audio.mp3
start_audio_path = os.path.join(STATIC_DIR, 'start_audio.mp3')
if not os.path.exists(start_audio_path):
    print(f"Warning: Required start_audio.mp3 not found at: {start_audio_path}")

# Dictionary to keep conversation history in memory per Twilio CallSid.
conversation_history = {}

def cleanup_file_later(file_path, delay=600):
    """Delete the specified file later."""
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
    conversation_history[call_sid] = history[-5:]

def build_prompt_from_history(call_sid):
    """Combine conversation history into a single prompt string."""
    history = get_conversation_context(call_sid)
    prompt = "\n".join(f"{msg['role'].capitalize()}: {msg['content']}" for msg in history)
    return prompt

# ----------------------------
# ElevenLabs TTS Asynchronous call helper (unchanged)
# ----------------------------

def get_tts_audio(text):
    """Get the ElevenLabs audio data for the given text."""
    try:
        print("\nStarting ElevenLabs synthesis...")
        tts_engine = ElevenLabsTTS()
        audio_data = tts_engine.synthesize(text)
        
        if audio_data:
            temp_file = os.path.join(STATIC_DIR, f"response_{int(time.time())}.mp3")
            with open(temp_file, 'wb') as f:
                f.write(audio_data)
            
            cleanup_file_later(temp_file)
            return f"/static/{os.path.basename(temp_file)}"
        else:
            print("Warning: No audio data received from synthesize()")
            return None
    except Exception as e:
        print("Error in ElevenLabs TTS synthesis:", e)
        raise

# ----------------------------
# Global asynchronous task support
# ----------------------------

# Create a global ThreadPoolExecutor and a dictionary to hold tasks per CallSid.
executor = ThreadPoolExecutor(max_workers=5)
ai_tasks = {}

def process_ai_response(call_sid, prompt):
    """
    Background task that generates AI text and synthesizes TTS audio.
    This function returns the relative URL of the synthesized audio file.
    """
    try:
        print(f"\nGenerating AI response asynchronously for Call SID: {call_sid}")
        ai_reply = openrouter_api.generate_text(prompt)
        print(f"AI Response: {ai_reply}")
    except Exception as e:
        ai_reply = "I'm sorry, I'm having trouble understanding you right now. Please try again later."
        print("Error in AI generation:", e)
    # Update conversation history with the assistant’s reply.
    update_conversation_history(call_sid, "assistant", ai_reply)
    try:
        audio_url = get_tts_audio(ai_reply)
        print(f"Audio synthesis complete. URL: {audio_url}")
    except Exception as e:
        print("Error synthesizing TTS audio asynchronously:", e)
        raise e
    return audio_url

# ----------------------------
# New route to poll for asynchronous response
# ----------------------------

@app.route("/check_ai", methods=["GET", "POST"])
def check_ai():
    call_sid = request.values.get('CallSid')
    response = VoiceResponse()
    if not call_sid or call_sid not in ai_tasks:
        # No background task found? Continue gathering.
        gather = Gather(input="speech", action="/process_voice", method="POST", timeout=10)
        response.append(gather)
        return Response(str(response), mimetype="application/xml")
    future = ai_tasks[call_sid]
    if not future.done():
        # Still processing – pause briefly and poll again.
        response.pause(length=1)
        response.redirect(url_for("check_ai", CallSid=call_sid))
        return Response(str(response), mimetype="application/xml")
    try:
        audio_url = future.result()
    except Exception as e:
        print("Error in background AI processing:", e)
        response.play('/static/error_audio.mp3')
        response.hangup()
        return Response(str(response), mimetype="application/xml")
    # If the background work succeeded, play the TTS synthesized audio.
    response.play(audio_url)
    response.pause(length=1)
    gather = Gather(input="speech", action="/process_voice", method="POST", timeout=10)
    response.append(gather)
    # Remove the completed task from our lookup.
    del ai_tasks[call_sid]
    return Response(str(response), mimetype="application/xml")

# ----------------------------
# Twilio routes
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
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response

@app.route("/voice", methods=["GET", "POST"])
def voice():
    """
    Twilio calls this when a new call comes in.
    It plays the welcome message and uses <Gather> for speech input.
    """
    response = VoiceResponse()
    call_sid = request.values.get('CallSid')
    
    print("\n=== New Call Started ===")
    print(f"Call SID: {call_sid}")
    print(f"Time: {datetime.datetime.now()}")
    
    get_conversation_context(call_sid)
    
    gather = Gather(input="speech", action="/process_voice", method="POST", timeout=10)
    response.append(gather)
    response.play('/static/start_audio.mp3')
    
    if call_sid in conversation_history:
        del conversation_history[call_sid]
    
    return Response(str(response), mimetype="application/xml")

@app.route("/process_voice", methods=["POST"])
def process_voice():
    """
    Receives the caller's speech, updates the conversation context,
    and then offloads AI text generation and TTS synthesis asynchronously.
    The caller is immediately informed to “hold” and the call is redirected
    to '/check_ai' for polling the result.
    """
    response = VoiceResponse()
    call_sid = request.values.get('CallSid')
    
    print("\n=== New Voice Request ===")
    print(f"Call SID: {call_sid}")
    print(f"Time: {datetime.datetime.now()}")
    
    base_url = request.host_url
    speech_text = request.values.get("SpeechResult", "").strip()
    
    if not speech_text:
        print("No speech detected in request")
        response.redirect("/voice")
        return Response(str(response), mimetype="application/xml")
    
    try:
        print(f"\nUser Speech: {speech_text}")
        update_conversation_history(call_sid, "user", speech_text)
        
        if any(exit_word in speech_text.lower() for exit_word in ["goodbye", "bye", "exit", "quit", "information"]):
            print("Exit word detected, ending call")
            try:
                # Extract location, phone, and situation from conversation
                context = get_conversation_context(call_sid)
                conversation_text = ' '.join([msg['content'] for msg in context])
                
                # Open CSV in append mode
                with open('911.csv', 'a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    # Write timestamp, call_sid, and full conversation text
                    writer.writerow([
                        time.strftime("%Y-%m-%d %H:%M:%S"),  # timestamp
                        call_sid,                            # call_sid
                        conversation_text                    # full conversation
                    ])
                print("Conversation context saved to CSV")
            except Exception as e:
                print(f"Error saving conversation to CSV: {e}")
            
            response.play('/static/goodbye_audio.mp3')
            response.hangup()
            if call_sid in conversation_history:
                del conversation_history[call_sid]
            return Response(str(response), mimetype="application/xml")
        
        # Build the prompt based on conversation history.
        prompt = build_prompt_from_history(call_sid)
        
        # Offload the heavy AI text generation and TTS synthesis in background.
        future = executor.submit(process_ai_response, call_sid, prompt)
        ai_tasks[call_sid] = future
        
        # Inform the caller to hold while the processing is in progress.
        response.say("Please hold while we process your request.")
        response.redirect("/check_ai?CallSid=" + call_sid)
        
    except Exception as e:
        print("Unexpected error in process_voice:", e)
        response.play('/static/error_audio.mp3')
        response.hangup()
    
    return Response(str(response), mimetype="application/xml")

# ... other routes or code remain unchanged ...

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
