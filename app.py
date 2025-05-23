# Importing modules
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
        """Launch the application"""
        interface = create_interface(
            process_function=self.medical_service.process_patient_query
        )
        interface.launch(debug=True)

if __name__ == "__main__":
    app = HealthIntuitApp()
    app.run()
