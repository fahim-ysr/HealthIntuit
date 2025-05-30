# Import your existing modules
import gradio as gd
import os
from pathlib import Path
from ui.gradui_ui import create_interface
from services.medical_services import HealthIntuitService

def main():
    """Main deployment function for HealthIntuit"""
    
    # Check if API keys are available (they'll be set as secrets in HF Spaces)
    groq_key = os.getenv("GROQ_API_KEY")
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
    
    if not groq_key or not elevenlabs_key:
        print("Warning: API keys not found in environment variables")
    
    # Initialize the medical service
    medical_service = HealthIntuitService()
    
    # Create the interface
    interface = create_interface(
        process_function=medical_service.process_patient_query
    )
    
    # Launch with deployment settings
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=False
    )

if __name__ == "__main__":
    main()
