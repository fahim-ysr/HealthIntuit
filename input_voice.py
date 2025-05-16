# Importing Modules
# pip install pyaudio
# pip install ffmpeg
# pip install speech recognition
# pip install pydub

import logging
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO


# Setting up audio recorder
logging.basicConfig(level= logging.INFO, format= '%(asctime)s - %(levelname)s - %(message)s')

# This function records audio from microphone and saves it as an MP3 file
def record(path, timeout= 20, phrase_time_limit=None):
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
            
            # Stores the MP3 in the path
            audio_segment.export(path, format= "mp3", bitrate= "128k")

    except Exception as e:
        # In case of errors
        logging.error(f"Error occured: {e}")

record(path= "sample_voice.mp3")


# Setting up speech-to-text SST model for transcription