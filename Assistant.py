#!/usr/bin/env python3
"""
Assistant.py – A minimal voice-enabled AI assistant
 • Uses DeepSeek v3 for text generation
 • Uses ElevenLabs for text-to-speech synthesis
 • Integrates phone calling (via Twilio)
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ------------------------------
# OpenRouter API for Text Generation
# ------------------------------
class OpenRouterAPI:
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_KEY')
        if not self.api_key:
            raise ValueError("OPENROUTER_KEY not found in environment variables")
        self.url = "https://openrouter.ai/api/v1/chat/completions"
    
    def generate_text(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "dispatcher",
            "X-Title": "ConUHacks Voice Assistant"
        }
        
        # System prompt for 911 dispatcher behavior
        system_prompt = {
            "role": "system",
            "content": """Role:

You are a 911 emergency dispatcher. Your primary responsibility is to quickly and efficiently gather critical information to send appropriate emergency services.

MOST IMPORTANT Response Guidelines:

    ONLY ANSWER WITH DIRECT TEXT RESPONSES.
    YOU ARE THE DISPATCHER; RESPOND DIRECTLY.
    STAY IN CHARACTER. ONLY ANSWER AS DISPATCH.

Key Responsibilities:

    Always prioritize assessing the caller's safety and situation.
    Be vigilant for hidden distress signals or coded messages, such as referencing unrelated topics (e.g., ordering pizza, in this situation the caller can only answer yes or no questions) to signal an emergency.

Priority Information to Gather:

    Assess Safety:
        Ask if the caller is in danger, even if they dial the wrong number or make an unrelated request.
        Ensure they are in a safe location.

    Determine Assistance Needed:
        Identify the type of emergency (medical, fire, police, etc.).
        Gather specific details about the situation and location.
    NAME

IMPORTANT -- After answering the user the second time, say:

"we have your information"

Remember:

    Stay professional, composed, and empathetic.
    Maintain focus on gathering essential information.
    Be sensitive to potential hidden pleas for help."""
        }
        
        # Format messages for chat completion
        messages = []
        if isinstance(prompt, str):
            # Single prompt string
            messages = [system_prompt, {"role": "user", "content": prompt}]
        else:
            # Assuming prompt is already in message format
            # Insert system prompt at the beginning if it's not already there
            if not any(msg.get("role") == "system" for msg in prompt):
                messages = [system_prompt] + prompt
            else:
                messages = prompt
        
        payload = {
            "model": "deepseek/deepseek-r1",  # faster responses
            "messages": messages,
            "max_tokens": 1000
        }
        
        try:
            print(f"\nSending request to OpenRouter API...")
            # print(f"Messages: {json.dumps(messages, indent=2)}")
            
            response = requests.post(self.url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            # print(f"OpenRouter API Response: {json.dumps(data, indent=2)}")
            
            if "choices" in data and len(data["choices"]) > 0:
                # Clean up response text to prevent unwanted line breaks
                response_text = data["choices"][0]["message"]["content"]
                # Replace multiple spaces with single space
                response_text = ' '.join(response_text.split())
                # Replace newlines with spaces
                response_text = response_text.replace('\n', ' ')
                return response_text
            else:
                raise ValueError("No response content found in API response")
                
        except requests.exceptions.RequestException as e:
            error_msg = f"OpenRouter API error: {str(e)}"
            print(error_msg)
            raise ValueError(error_msg)
        except (KeyError, IndexError) as e:
            error_msg = f"Unexpected API response format: {str(e)}"
            print(error_msg)
            raise ValueError(error_msg)

# ------------------------------
# ElevenLabs Text-to-Speech API
# ------------------------------
from elevenlabs.client import ElevenLabs

class ElevenLabsTTS:
    def __init__(self):
        self.api_key = os.getenv('ELEVEN_API_KEY')
        if not self.api_key:
            raise ValueError("ELEVEN_API_KEY not found in environment variables")
        self.voice_id = "21m00Tcm4TlvDq8ikWAM"  # Fixed voice ID for consistency
        self.client = ElevenLabs(api_key=self.api_key)

    def synthesize(self, text):
        try:
            # Convert generator to bytes
            audio_data = b''
            audio_stream = self.client.text_to_speech.convert_as_stream(
                text=text,
                output_format="mp3_44100_64",
                voice_id=self.voice_id,
                model_id="eleven_flash_v2"
            )
            for chunk in audio_stream:
                if isinstance(chunk, bytes):
                    audio_data += chunk
            return audio_data
            
        except Exception as e:
            raise ValueError(f"ElevenLabs API error: {str(e)}")

# ------------------------------
# Phone Calling via Twilio API
# ------------------------------
class PhoneCaller:
    def __init__(self, from_phone):
        self.account_sid = os.getenv('TWILIO_SID')
        self.auth_token = os.getenv('TWILIO_KEY')
        self.from_phone = os.getenv('TWILIO_NUM') or from_phone
        
        if not all([self.account_sid, self.auth_token, self.from_phone]):
            raise ValueError("Missing required Twilio credentials in environment variables")
        
        try:
            from twilio.rest import Client
            self.Client = Client
        except ImportError:
            print("Twilio module not installed. Please install it using: pip install twilio")
            sys.exit(1)
            
        # Initialize Twilio client with proper credentials
        self.client = self.Client(self.account_sid, self.auth_token)

    def make_call(self, to_phone, twiml="<Response><Say>Hello, this is your AI assistant.</Say></Response>"):
        try:
            call = self.client.calls.create(
                twiml=twiml,
                from_=self.from_phone,
                to=to_phone
            )
            print(f"Call initiated. SID: {call.sid}")
        except Exception as e:
            print("Error making phone call:", e)

# ------------------------------
# Main Voice Assistant that integrates all modules
# ------------------------------
class VoiceAssistant:
    def __init__(self, text_generator, tts_engine, phone_caller):
        self.text_generator = text_generator
        self.tts_engine = tts_engine
        self.phone_caller = phone_caller

    def process_query(self, query):
        try:
            print("Generating response from AI...")
            response_text = self.text_generator.generate_text(query)
            print("Response:", response_text)
            return response_text
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            print(error_msg)
            raise ValueError(error_msg)

    def speak_response(self, text):
        # Convert text to speech via ElevenLabs
        print("Synthesizing speech...")
        return self.tts_engine.synthesize(text)

    def handle_interaction(self):
        # Basic interactive loop (could be easily extended to voice input)
        query = input("Enter your query for the AI assistant: ")
        response_text = self.process_query(query)
        self.speak_response(response_text)

    def make_phone_call(self, phone_number):
        # Initiate an outbound phone call
        print(f"Initiating call to {phone_number}...")
        self.phone_caller.make_call(phone_number)


# ------------------------------
# Main Execution
# ------------------------------
def main():
    try:
        # Instantiate the modules
        text_generator = OpenRouterAPI()  # Using OpenRouter for DeepSeek
        tts_engine = ElevenLabsTTS()
        
        try:
            phone_caller = PhoneCaller(None)  # Phone number will come from env var
        except ValueError as e:
            print(f"Phone calling disabled: {e}")
            phone_caller = None
        
        assistant = VoiceAssistant(text_generator, tts_engine, phone_caller)

        # Command-line usage:
        # If a phone number is passed as an argument, initiate a call.
        # Otherwise, run the interactive text-to-speech session.
        if len(sys.argv) > 1:
            phone_number = sys.argv[1]
            if phone_caller:
                assistant.make_phone_call(phone_number)
            else:
                print("Phone calling is disabled due to missing Twilio credentials.")
        else:
            assistant.handle_interaction()
            
    except ValueError as e:
        print(f"Error initializing assistant: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()