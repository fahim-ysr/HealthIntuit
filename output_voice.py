# Importing Modules
import os
import elevenlabs
from gtts import gTTS
from elevenlabs.client import ElevenLabs
import subprocess
from pydub import AudioSegment
import platform


# !Setting up Text-to-Speech model using ElevenLabs api

# Import ElevenLabs API Key
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(".env.local"))
KEY = os.getenv("ELEVENLABS_API_KEY")

def text_to_speech_elevenlabs(response, path):
    client= ElevenLabs(api_key= KEY)
    audio= client.generate(
        text= response,
        # voice= "Freya",
        voice= "Jessica",
        output_format= "mp3_44100_128",
        # Currently using the most lifelike model with rich emotional expression
        model= "eleven_turbo_v2"
    )
    
    # Saves the audio in the file path
    elevenlabs.save(audio, path)

    # Converting MP3 to WAV for autoplay
    wav_path= path.replace(".mp3", ".wav")
    audio_segment= AudioSegment.from_mp3(path)
    audio_segment.export(wav_path, format= "wav")

    # Setting up autoplay upon calling the function
    os_name = platform.system()
    try:
        # Autoplay compatibility for Windows
        if os_name == "Windows":
            subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{wav_path}").PlaySync();'])
            os.remove(wav_path)
        
        # Autoplay compatibility for Linux
        if os_name == "Linux":
            subprocess.run(['aplay', wav_path])
    
    except Exception as e:
        print(f"An error has occured: {e}")


# # *Testing the text_to_speech_elevenlabs
# text = "Hello, testing, 1, 2, 3, 4, 5."
# text_to_speech_elevenlabs(text, path= "elabs_testing_autoplay.mp3")