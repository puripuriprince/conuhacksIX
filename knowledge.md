# Voice Assistant Project

## Overview
Emergency dispatch voice assistant that:
- Takes voice input via Twilio
- Processes speech to text
- Generates responses using DeepSeek Chat (via OpenRouter)
- Synthesizes natural speech using ElevenLabs TTS
- Maintains conversation context
- Handles phone calls via Twilio
- Behaves as a professional 911 dispatcher

## Emergency Response Protocol
- System maintains professional, serious tone
- Prioritizes gathering critical information
- Focuses on location, emergency type, and situation details
- Provides clear instructions to callers
- Maintains call until assistance is confirmed
- Behaves as a professional 911 dispatcher

## Emergency Response Protocol
- System maintains professional, serious tone
- Prioritizes gathering critical information
- Focuses on location, emergency type, and situation details
- Provides clear instructions to callers
- Maintains call until assistance is confirmed

## Key Components

### Voice Processing Flow
1. User calls Twilio number
2. Twilio captures speech and sends to webhook
3. OpenRouter generates AI response
4. ElevenLabs synthesizes natural voice
5. Response played back to user via Twilio

### APIs Used
- OpenRouter API (GPT-3.5-turbo) for text generation
- ElevenLabs (streaming TTS) for text-to-speech
- Twilio for phone handling

### Audio Settings
- ElevenLabs voice ID: JBFqnCBsd6RMkjVDRZzb
- MP3 format: 44.1kHz, 64kbps
- Stream audio chunks directly to client
- Clean up audio files after 10 minutes
- Always use ElevenLabs TTS, no fallback
- Use ElevenLabs Python client with convert_as_stream for audio synthesis

## Twilio Call Handling
- Use background processing for long-running operations (AI/TTS)
- Keep connection alive with hold/redirect pattern
- Store async results in thread-safe shared dictionary
- Clean up results after use
- Use short pauses (2-3s) between hold messages

### Important Implementation Details
- Only start_audio.mp3 required in /static directory
- Conversation history kept in memory (per call)
- Stream audio chunks directly for faster playback
- No temporary audio file storage needed

## Environment Variables Required
- OPENROUTER_KEY
- ELEVEN_API_KEY
- TWILIO_SID
- TWILIO_KEY
- TWILIO_NUM

## Development Notes
- Flask server runs on port 5000
- Ngrok tunnel required for Twilio webhook
- Static directory must exist and be accessible
- Debug logs track entire conversation flow
- High quality voice settings configured in ElevenLabsTTS
- Server timeout after 30s is normal - use Ctrl+C to stop manually
- Speech input timeout set to 10 seconds to allow adequate response time
