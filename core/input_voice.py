# Importing Modules
import httpx
import logging
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO
import os
from groq import Groq


# # Explicitly setting the full path to FFmpeg executables (To avoid errors)
# # Installed FFmpeg locally from source website

# ffmpeg_path = r"C:\ffmpeg\bin\ffmpeg.exe"

# if os.path.exists(ffmpeg_path):
#     AudioSegment.converter = ffmpeg_path
#     AudioSegment.ffmpeg = ffmpeg_path
#     AudioSegment.ffprobe = r"C:\ffmpeg\bin\ffprobe.exe"
# else:
#     print(f"FFmpeg not found at {ffmpeg_path}. Please check the path.")


# !Setting up audio recorder (Configuration)
logging.basicConfig(level= logging.INFO, format= '%(asctime)s - %(levelname)s - %(message)s')

# This function records audio from microphone and saves it as an MP3 file
def record(path, timeout= 20, phrase_time_limit=None):
    # timeout: The maximum time to wait for the phrase to start
    # phrase_time_limit: Time to allow user to ask questions

    rec = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            logging.info("Adjusting for ambient noise...")
            rec.adjust_for_ambient_noise(source, duration=1)
            logging.info("Start speaking now...")

            # Records the audio
            audio_data = rec.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            logging.info("Recording complete.")

            # Converts the recorded audio to MP3
            wav_data = audio_data.get_wav_data()
            audio_segment = AudioSegment.from_wav(BytesIO(wav_data))
            
            # Saves the MP3 in the path
            audio_segment.export(path, format= "mp3", bitrate= "128k")
            # Chose bitrate as 128k for least filesize without loss of quality
            
            logging.info(f"Audio saved to {path}")

    # Error Handling
    except Exception as e:
        logging.error(f"Error occured! {e}")

audio_file = "patient_request.mp3"


# # *Testing*
# record(path= audio_file)


# !Setting up speech-to-text SST model for transcription

# Importing GROQ API Key
                                                                         
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path("../.env.local"))
current_model = "whisper-large-v3-turbo"


def speech_to_text(model, path, api_key, language="en"):

    # Debugging to check if API key is loaded
    api_key = os.getenv("GROQ_API_KEY")
    print(f"DEBUG: API key loaded: {'Yes' if api_key else 'No'}")
    print(f"DEBUG: API key length: {len(api_key) if api_key else 0}")

    if not api_key or api_key.strip() == "":
        raise Exception("GROQ_API_KEY is missing or empty. Please check your .env.local file.")
    
    try:

        # Setting up Groq client
        client = Groq(api_key= api_key)

        # Encoding the file for transcription in binary
        audio_file = open(path, "rb")

        # Setting up transcription end point
        transcription = client.audio.transcriptions.create(
            model = current_model,
            file= audio_file,
            language=language
        )

        # Returns the extracted transcription of the audio file
        return transcription.text
    
    except Exception as e:
        # raise Exception(f"API key usage failed during voice input stage: {str(e)}")
        print(f"Normal connection failed: {e}")
        print("Trying with SSL verification disabled...")

        # Fallback with SSL disabled
        client = Groq(
            api_key= api_key,
            http_client= httpx.Client(verify= False)
        )

        with open(audio_file, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file= file,
                model= model,
                response_format= "text"
            )
        
        return transcription


# # *Testing*

# # Importing OpenAI Whisper
# current_model = "whisper-large-v3-turbo"
# print(speech_to_text(model= current_model, path= audio_file, api_key= KEY))