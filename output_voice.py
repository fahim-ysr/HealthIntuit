# Importing Modules
import os
import elevenlabs
from gtts import gTTS
from elevenlabs.client import ElevenLabs
import subprocess
from pydub import AudioSegment


# !Setting up Text-to-Speech Model

def text_to_speech(response, path):
    language= "en"
    audio_obj = gTTS(
        text= response,
        lang= language,
        # For Canadian Accent
        tld='ca',
        slow= False
    )

    # Saving audio object to the file path
    audio_obj.save(path)


# # *Testing
# text = "Hello, testing, 1, 2, 3, 4, 5."
# text_to_speech(response= text, path= "tts_testing.mp3")


# !Using Model for text output to voice for simulating doctor's reply

# Import ElevenLabs API Key
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(".env.local"))
KEY = os.getenv("ELEVENLABS_API_KEY")

def text_to_speech_elevenlabs(response, path):
    client= ElevenLabs(api_key= KEY)
    audio= client.generate(
        text= response,
        voice= "Freya",
        # voice= "Matilda",
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
    try:
        subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{wav_path}").PlaySync();'])
        os.remove(wav_path)
    
    except Exception as e:
        print(f"An error has occured: {e}")


# # *Testing the text_to_speech_elevenlabs
# text = "Hello, testing, 1, 2, 3, 4, 5."
# text_to_speech_elevenlabs(text, path= "elabs_testing_autoplay.mp3")