# Importing modules
import gradio as gd
import os
from pathlib import Path
from services.medical_services import HealthIntuitService
from ui.gradui_ui import create_interface
from config.settings import get_config


class HealthIntuitApp:
    """Main Application Class"""
    

    # Constructor
    def __init__(self):
        self.config = get_config()
        self.medical_service = HealthIntuitService()
    

    def run(self):
        """Launchs the application with Docker-compatible settings"""
        interface = create_interface(
            process_function=self.medical_service.process_patient_query
        )
        
        # Check if running in Docker environment
        if self._is_docker_environment():
            # Docker deployment settings
            interface.launch(
                server_name="0.0.0.0",  # Essential for Docker
                server_port=7860,       # Standard port
                share=False,            # Don't use share links
                debug=False,            # Disable debug for production
                show_error=True,        # Show errors for troubleshooting
                favicon_path=None       # Avoid favicon issues
            )
            print("🐳 HealthIntuit running in Docker at http://localhost:7860")
        else:
            # Local development settings (your existing behavior)
            interface.launch(debug=True)
            print("🌞 Light mode (default): http://127.0.0.1:7860/?__theme=light")
            print("🌙 Dark mode: http://127.0.0.1:7860/?__theme=dark")
    

    def _is_docker_environment(self) -> bool:
        """Checks if running inside Docker container"""
        # Check for Docker-specific environment variables or files
        return (
            os.path.exists('/.dockerenv') or 
            os.getenv('DOCKER_CONTAINER') == 'true' or
            os.getenv('GRADIO_SERVER_NAME') == '0.0.0.0'
        )
    

    def check_api_keys(self) -> bool:
        """Validates if API keys are available"""
        groq_key = os.getenv("GROQ_API_KEY")
        elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
        
        if not groq_key:
            print("⚠️  Warning: GROQ_API_KEY not found in environment variables")
            return False
        if not elevenlabs_key:
            print("⚠️  Warning: ELEVENLABS_API_KEY not found in environment variables")
            return False
        
        print("✅ API keys found successfully")
        return True


if __name__ == "__main__":
    app = HealthIntuitApp()
    
    # Checks API keys before launching
    if app.check_api_keys():
        print("Launching ⚕️HealthIntuit...")
        app.run()
    else:
        print("❌ Cannot launch HealthIntuit without API keys")
        print("💡 For Docker: docker run -e GROQ_API_KEY=your_key -e ELEVENLABS_API_KEY=your_key ...")
