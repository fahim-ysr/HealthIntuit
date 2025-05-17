# Importing Modules
# pip install pyaudio
# pip install ffmpeg
# pip install speech recognition
# pip install pydub

import logging
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO
import os


# Explicitly setting the full path to FFmpeg executables (To avoid errors)
# Installed FFmpeg locally from source website

ffmpeg_path = r"C:\ffmpeg\bin\ffmpeg.exe"

if os.path.exists(ffmpeg_path):
    AudioSegment.converter = ffmpeg_path
    AudioSegment.ffmpeg = ffmpeg_path
    AudioSegment.ffprobe = r"C:\ffmpeg\bin\ffprobe.exe"
else:
    print(f"FFmpeg not found at {ffmpeg_path}. Please check the path.")


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

# Calling the function
record(path= "patient_request.mp3")


# !Setting up speech-to-text SST model for transcription