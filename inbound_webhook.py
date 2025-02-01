#!/usr/bin/env python3
# inbound_webhook.py

import os
import json
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from dotenv import load_dotenv

# Import the OpenRouterAPI from your assistant module
from Assistant import OpenRouterAPI

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize OpenRouter API with proper configuration
openrouter_api = OpenRouterAPI()

# --- Conversation History Management ---
conversation_history = {}

def get_conversation_context(call_sid):
    """Retrieve or initialize conversation history for a call"""
    if call_sid not in conversation_history:
        conversation_history[call_sid] = []
    return conversation_history[call_sid]

def update_conversation_history(call_sid, role, content):
    """Add a message to the conversation history"""
    history = get_conversation_context(call_sid)
    history.append({"role": role, "content": content})
    # Keep only last 5 messages to avoid context getting too long
    conversation_history[call_sid] = history[-5:]

# --- Inbound Call Entry Point ---
@app.route("/voice", methods=["GET", "POST"])
def voice():
    """
    This endpoint is hit by Twilio when a call comes in.
    It greets the caller and prompts for a spoken query.
    """
    response = VoiceResponse()
    call_sid = request.values.get('CallSid')
    
    # Initialize conversation for this call
    get_conversation_context(call_sid)
    
    # Use <Gather> with input="speech" for automatic speech recognition
    gather = Gather(input="speech", action="/process_voice", method="POST", timeout=5)
    welcome_message = "Hello, this is your AI assistant. Please ask your question after the beep."
    gather.say(welcome_message)
    response.append(gather)
    
    # If no speech is received, say goodbye
    response.say("We did not receive any input. Goodbye!")
    
    # Clean up conversation history if call ends
    if call_sid in conversation_history:
        del conversation_history[call_sid]
    
    return Response(str(response), mimetype="application/xml")

# --- Processing the Caller's Speech ---
@app.route("/process_voice", methods=["POST"])
def process_voice():
    """
    This endpoint receives the caller's speech via Twilio,
    processes it through OpenRouter API, and returns the spoken response.
    """
    response = VoiceResponse()
    call_sid = request.values.get('CallSid')
    speech_text = request.values.get("SpeechResult", "").strip()
    
    if speech_text:
        try:
            # Update conversation history with user's input
            update_conversation_history(call_sid, "user", speech_text)
            
            # Check for conversation end
            if any(exit_word in speech_text.lower() for exit_word in ["goodbye", "bye", "exit", "quit"]):
                response.say("Thank you for calling! Goodbye!")
                response.hangup()
                # Clean up conversation history
                if call_sid in conversation_history:
                    del conversation_history[call_sid]
            else:
                # Generate AI response using conversation history
                try:
                    ai_reply = openrouter_api.generate_text(speech_text)
                    # Update conversation history with AI's response
                    update_conversation_history(call_sid, "assistant", ai_reply)
                    
                    # Speak the response
                    response.say(ai_reply)
                    response.pause(length=1)
                    
                    # Continue the conversation
                    gather = Gather(input="speech", action="/process_voice", method="POST", timeout=5)
                    gather.say("Do you have another question? Please speak after the beep.")
                    response.append(gather)
                    response.say("No further input received. Goodbye!")
                    
                except ValueError as e:
                    error_message = "I apologize, but I'm having trouble processing your request right now. Please try again later."
                    response.say(error_message)
                    print(f"OpenRouter API error: {str(e)}")
                    response.hangup()
        except Exception as e:
            error_message = "I apologize, but something went wrong. Please try again later."
            response.say(error_message)
            print(f"Unexpected error: {str(e)}")
            response.hangup()
    else:
        response.say("Sorry, I did not catch that. Please try again.")
        response.redirect("/voice")
    
    return Response(str(response), mimetype="application/xml")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
