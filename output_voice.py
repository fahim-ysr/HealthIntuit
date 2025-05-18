# Importing Modules
import os
import elevenlabs
from gtts import gTTS
from elevenlabs.client import ElevenLabs

def text_to_speech(response, filepath):
    language= "en"
    audio_obj = gTTS(
        text= response,
        lang= language,
        # For Canadian Accent
        tld='ca',
        slow= False
    )

    # Saving audio object to the file path
    audio_obj.save(filepath)

# Testing the text_to_speech function
text = "Hello, testing, 1, 2, 3, 4, 5."
text_to_speech(response= text, filepath= "tts_testing.mp3")


# !Setting up Text-to-Speech Model

# Import ElevenLabs API Key
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(".env.local"))
KEY = os.getenv("ELEVENLABS_API_KEY")


# !Using Model for text output to voice for simulating doctor's reply