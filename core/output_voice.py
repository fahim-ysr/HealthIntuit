# Importing Modules
import os
import elevenlabs
from gtts import gTTS
from elevenlabs.client import ElevenLabs
import subprocess
from pydub import AudioSegment
import platform
from config.settings import get_config


def _is_docker_env() -> bool:
    """Checks if running inside Docker container"""
    return (
        os.path.exists('/.dockerenv') or 
        os.getenv('DOCKER_CONTAINER') == 'true' or
        os.getenv('GRADIO_SERVER_NAME') == '0.0.0.0'
    )


def _play_audio_locally(path: str):
    """Plays audio locally (only for local development)"""

    try:
        # Converting MP3 to WAV for autoplay
        wav_path= path.replace(".mp3", ".wav")
        audio_segment= AudioSegment.from_mp3(path)
        audio_segment.export(wav_path, format= "wav")

        # Setting up autoplay upon calling the function
        os_name = platform.system()

        # Autoplay compatibility for Windows
        if os_name == "Windows":
            subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{wav_path}").PlaySync();'])
            os.remove(wav_path)
        
        # Autoplay compatibility for Linux
        if os_name == "Linux":
            subprocess.run(['aplay', wav_path])
            os.remove(wav_path)
    
    except Exception as e:
        print(f"Local audio playback error: {e}")
        



# !Setting up Text-to-Speech Model (Substitute of Elevenlabs)

def text_to_speech(response, path, lang="en"):
    audio_obj = gTTS(
        text= response,
        lang= lang,
        # For Canadian Accent
        tld='ca' if lang == "en" else "com" ,
        slow= False
    )

    # Saving audio object to the file path
    audio_obj.save(path)

    # Autoplays the doctor's voice if not in Docker
    if not _is_docker_env():
        _play_audio_locally(path)


# !Setting up Text-to-Speech model using ElevenLabs api

# Import ElevenLabs API Key
from dotenv import load_dotenv
from pathlib import Path

env_file = Path(".env.local")
if env_file.exists():
    load_dotenv(env_file)

KEY = os.getenv("ELEVENLABS_API_KEY")

def text_to_speech_elevenlabs(response, path, lang= "en"):
    client= ElevenLabs(api_key= KEY)
    config = get_config()

    # voice_map= {
    #     "en": "Jessica",
    #     "fr": "Freya"
    # }

    # audio= client.generate(
    #     text= response,
    #     # voice= "Freya",
    #     voice= voice_map.get(lang, "Jessica"),
    #     output_format= "mp3_44100_128",
    #     # Currently using the most lifelike model with rich emotional expression
    #     model= "eleven_turbo_v2"
    # )

    voice_id_map = {
        "en": "cgSgspJ2msm6clMCkdW9",
        "fr": "K7gx0ylJdff0yjM2uVQS"
    }

    # Gets voice ID for current language
    voice_id = voice_id_map.get(lang, voice_id_map["en"])

    try:
        # Premium API call with voice settings
        audio = client.generate(
            text=response,
            voice=voice_id,  # Use voice ID instead of name
            model="eleven_multilingual_v2",  # Premium multilingual model
            voice_settings={
                "stability": 0.75,
                "similarity_boost": 0.85,
                "style": 0.50,
                "use_speaker_boost": True
            },
            output_format="mp3_44100_128"
        )
        
        # Save the audio
        elevenlabs.save(audio, path)
        
    except Exception as e:
        print(f"ElevenLabs Premium TTS error: {e}")
        
        # Fallback to regular gTTS
        print("Falling back to gTTS...")
        text_to_speech(response, path, lang)
        return
    
    # Autoplays the doctor's voice if not in Docker
    if not _is_docker_env():
        _play_audio_locally(path)


# # *Testing the text_to_speech_elevenlabs
# text = "Hello, testing, 1, 2, 3, 4, 5."
# text_to_speech_elevenlabs(text, path= "elabs_testing_autoplay.mp3")