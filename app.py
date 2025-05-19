# Importing modules
from fundamentals import image_encode, analyze_image_and_query
from input_voice import record, speech_to_text, KEY
from output_voice import text_to_speech_elevenlabs, text_to_speech
import os
import gradio as gd
from pydub import AudioSegment


# !Importing STT and TTS models

sst_model = "whisper-large-v3-turbo"    # Speech-to-text model
tts_model = "meta-llama/llama-4-scout-17b-16e-instruct"     # Text-to-speech model


# !Setting up the prompt
prompt= (
    """
    Please act as a professional doctor, I know you are not but this is for educational purposes.
    Now, what's in this image?. Do you find anything wrong with it medically?
    If you make a differential, suggest some remedies for them. Do not add any numbers or special characters in
    your response. Your response should be in one long paragraph. Also always answer as if you are talking to a real person.
    Do not say 'In the image I see' but say 'So what I see, I presume you have .... '
    Dont respond as an AI model in markdown, your answer should mimic that of an actual doctor not an AI bot,
    Keep your answer concise. No preamble, start your answer right away please
    """
    )


# !Configuring main functionality of UI from the other files

# This function processes data from the fundamentals, input_voice and output_voice files
def main_functionality(audio_path, image_path):
    
    # Setting up the Speech To Text for extracting query (Patient's Input)
    stt_output = speech_to_text(
        model= sst_model,
        path= audio_path,   # Arg 2
        api_key= KEY
    )

    # Setting up image and query Input (Patient's Input)
    if image_path:
        doctors_response = analyze_image_and_query(
            encoded_image= image_encode(image_path),    #Arg 1
            query= prompt+stt_output,
            model= tts_model
        )
    else:
        doctors_response= "Needs image and voice to analyze!"

    # Setting up Speech To Text (Doctor's Response)
    output_path= "doctors_response.mp3"
    
    # doctors_voice = text_to_speech_elevenlabs(
    #     response= doctors_response,
    #     path= output_path
    # )

    # Substitute
    doctors_voice = text_to_speech(
        response= doctors_response,
        path= output_path
    )

    # Reads the audio file as a tuple (sample_rate, data)
    import numpy as np
    from scipy.io import wavfile

    # Converts MP3 to WAV for Scipy
    temp_wav = "temp.wav"
    audio_segment= AudioSegment.from_mp3(output_path)
    audio_segment.export(temp_wav, format= "wav")

    # Reading the WAV
    sample_rate, audio_data = wavfile.read(temp_wav)
    os.remove(temp_wav)


    # return stt_output, doctors_response, doctors_voice
    return stt_output, doctors_response, (sample_rate, audio_data)


# !UI Setup

ui = gd.Interface(
    fn= main_functionality,
    inputs= [
        # Setting up audio and image source
        gd.Audio(sources= ["microphone"], type= "filepath"),
        gd.Image(type= "filepath")
    ],

    outputs= [
        gd.Textbox(label= "Speech To Text"),
        gd.Textbox(label= "Doctor's Response"),
        gd.Audio(label= "Doctor's Voice", type= "numpy")
    ],

    title= "⚕️HealthIntuit: Your AI Medical Assistant",
    theme= gd.themes.Ocean(),
    allow_flagging= "never"
)

ui.launch(debug= True)