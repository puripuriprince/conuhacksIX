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
            "HTTP-Referer": "https://github.com/your-repo",  # Update with your actual site
            "X-Title": "AI Voice Assistant"
        }
        
        payload = {
            "model": "deepseek/deepseek-v3",  # Using DeepSeek v3 model
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(self.url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
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
class ElevenLabsTTS:
    def __init__(self, voice_id=None):
        self.api_key = os.getenv('ELEVEN_API_KEY')
        if not self.api_key:
            raise ValueError("ELEVEN_API_KEY not found in environment variables")
        # Depending on the ElevenLabs API, the URL might need a voice_id
        # For now, we assume a generic endpoint:
        if voice_id is None:
            self.voice_id = "default_voice"
        else:
            self.voice_id = voice_id
        self.url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
    
    def synthesize(self, text):
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            # You can include voice settings or other parameters here.
        }
        response = requests.post(self.url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.content  # Binary audio
        else:
            error_msg = f"ElevenLabs API error {response.status_code}: {response.text}"
            print(error_msg)
            return None

    def play_audio(self, audio_content, filename="output.mp3"):
        # Save the audio content to a file
        with open(filename, "wb") as f:
            f.write(audio_content)
        print(f"Audio saved to {filename}")
        print("Note: Audio playback is not available. You can play the saved file manually.")

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
        audio = self.tts_engine.synthesize(text)
        if audio:
            self.tts_engine.play_audio(audio)
        else:
            print("Could not synthesize speech.")

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
        text_generator = OpenRouterAPI()  # Using OpenRouter instead of DeepSeek
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