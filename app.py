# Importing modules
from fundamentals import image_encode, analyze_image_and_query
from input_voice import record, speech_to_text, KEY
from output_voice import text_to_speech_elevenlabs, text_to_speech
from prescription_extract import extract_prescription, analyze_prescription
import os
import gradio as gd
from pydub import AudioSegment
from datetime import datetime


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
def main_functionality(name, audio_path, image_path):

    # Doesn't allow to pass without name input
    if not name:
        raise gd.Error("Please enter your full name first!")
    
    # Gets the current date and time
    current_date= datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
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

    # Extracting Prescription
    # prescription_text= extract_prescription(doctors_response)
    
    prescription_text= analyze_prescription(doctors_response= doctors_response, patient_name= name, current_date=current_date)
    prescription_path= "prescription.txt"
    with open(prescription_path, "w") as p:
        p.write(prescription_text)


    # return stt_output, doctors_response, doctors_voice
    return stt_output, doctors_response, (sample_rate, audio_data), prescription_text, prescription_path

# !UI Setup
with gd.Blocks(theme=gd.themes.Ocean()) as demo:
    gd.Markdown(
        "<h1 style='font-size:2.5em; text-align:center; margin-bottom: 0.5em;'>⚕️ HealthIntuit: Your AI Medical Assistant</h1>" \
        "</br>"
    )

    # Full Name at the top
    name_box = gd.Textbox(label="Full Name (required)", placeholder="Enter your full name here")

    # Two columns below: inputs (left), outputs (right)
    with gd.Row():

        with gd.Column(scale=2):
            audio_input = gd.Audio(sources=["microphone"], type="filepath", label="Describe your concern (voice)", interactive=False)
            image_input = gd.Image(type="filepath", label="Upload a relevant image", interactive=False)

        with gd.Column(scale=2):
            stt_output = gd.Textbox(label="Transcribed Patient Query")
            doctors_response = gd.Textbox(label="Doctor's Analysis")
            voice_output = gd.Audio(label="Doctor's Voice Response", type="numpy")
            prescription_output = gd.Textbox(label="Prescription", lines=8)
            download_btn = gd.File(label="Download Prescription", file_count="single")

    # Submit button at the bottom
    submit_btn = gd.Button("Analyze", variant="primary")

    # Enable inputs only if name is entered
    def enable_inputs(name):
        is_enabled = bool(name.strip())
        return gd.update(interactive=is_enabled), gd.update(interactive=is_enabled)
    name_box.change(enable_inputs, inputs=name_box, outputs=[audio_input, image_input])

    # Submit button triggers main functionality
    submit_btn.click(
        fn=main_functionality,
        inputs=[name_box, audio_input, image_input],
        outputs=[stt_output, doctors_response, voice_output, prescription_output, download_btn]
    )

demo.launch(debug=True)
