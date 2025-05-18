# Importing modules
from fundamentals.py import *
from input_voice.py import *
from output_voice.py import *
import os
import gradio as gd


#Importing models
sst_model = "whisper-large-v3-turbo"    # Speech-to-text model
tts_model = "meta-llama/llama-4-scout-17b-16e-instruct"     # Text-to-speech model


# This function processes data from the fundamentals, input_voice and output_voice files
def main_functionality(image_path, audio_path):
    
    # Setting up the Speech To Text for extracting query (Patient's Input)
    stt_output = speech_to_text(
        model= sst_model,
        path= audio_file,
        api_key= KEY
    )

    # Setting up image and query Input (Patient's Input)
    if image_path:
        response = analyze_image_and_query(
            encoded_image= encoded_image,
            query= stt_output,
            model= tts_model
        )
    else:
        response= "Need image to analyze!"

    # Setting up Speech To Text (Doctor's Response)
    doctor_voice = text_to_speech_elevenlabs(
        response= "",
        path= ""
    )


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
        gd.Audio("Sample_Output.mp3")
    ],

    title= "HealthIntuit: Your AI Medical Assistant"
)

ui.launch(debug= True)