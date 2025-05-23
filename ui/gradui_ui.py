# Importing modules
import gradio as gd
from typing import Callable, Tuple, Any


def create_interface(process_function: Callable) -> gd.Blocks:
    """Creates Gradio UI"""
    

    def handle_submission(name: str, audio_path: str, image_path: str) -> Tuple[str, str, Any, str, str]:
        """Handle form submission with error handling"""
        try:
            result = process_function(name, audio_path, image_path)
            return (
                result["transcription"],
                result["diagnosis"],
                result["voice_response"],
                result["prescription_text"],
                result["prescription_file"]
            )
        except Exception as e:
            raise gd.Error(f"Analysis failed: {str(e)}")
    

    def enable_inputs(name: str) -> Tuple[gd.update, gd.update]:
        """Enable/Disable inputs based on name entry"""
        is_enabled = bool(name and name.strip())
        return (
            gd.update(interactive=is_enabled),
            gd.update(interactive=is_enabled)
        )
    
    with gd.Blocks(theme=gd.themes.Ocean()) as interface:   #Theme: Ocean
        # Headers (Title and disclaimer)
        gd.Markdown(
            "</br>"
            "<h1 style='font-size:2.5em; text-align:center; margin-bottom: 0.5em;'>"
            "⚕️ HealthIntuit: Your AI Medical Assistant</h1>"
            "<p style='text-align:center; color: #666;'>For Educational Use Only</p>"
        )
        
        # Name input box
        name_box = gd.Textbox(
            label="Full Name (required)",
            placeholder="Enter your full name here"
        )
        
        # Main UI
        with gd.Row():
            # Input column
            with gd.Column(scale=2):
                audio_input = gd.Audio(
                    sources=["microphone"],
                    type="filepath",
                    label="Describe your concern (voice)",
                    interactive=False
                )
                image_input = gd.Image(
                    type="filepath",
                    label="Upload a relevant image",
                    interactive=False
                )
            
            # Output column
            with gd.Column(scale=2):
                stt_output = gd.Textbox(label="Transcribed Patient Query")
                doctors_response = gd.Textbox(label="Doctor's Analysis")
                voice_output = gd.Audio(label="Doctor's Voice Response", type="numpy")
                prescription_output = gd.Textbox(label="Prescription", lines=8)
                download_btn = gd.File(label="Download Prescription", file_count="single")
        
        # Submit button
        submit_btn = gd.Button("Analyze", variant="primary")
        
        # Event handlers
        name_box.change(
            enable_inputs,
            inputs=name_box,
            outputs=[audio_input, image_input]
        )
        
        submit_btn.click(
            handle_submission,
            inputs=[name_box, audio_input, image_input],
            outputs=[stt_output, doctors_response, voice_output, prescription_output, download_btn]
        )
    
    return interface
