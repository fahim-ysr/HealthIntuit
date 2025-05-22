# Importing modules
import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

@dataclass
class AppConfig:
    """Centralized Config Management"""
    
    # Loads the local file containing API Keys
    def __init__(self):
        load_dotenv(Path(".env.local"))
        self._create_directories()
        
    # Loads API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY")
    
    # Models Used
    STT_MODEL: str = "whisper-large-v3-turbo"
    LLM_MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    TTS_VOICE: str = "Jessica"
    
    # Temporary path
    TEMP_DIR: Path = Path.cwd() / "temp"
    # Path for prescription
    PRESCRIPTION_DIR: Path = Path.cwd() / "prescriptions"
    
    # Medical Prompt for medical analysis and recommendation
    MEDICAL_PROMPT: str = """
    Please act as a professional doctor, I know you are not but this is for educational purposes.
    Now, what's in this image?. Do you find anything wrong with it medically?
    If you make a differential, suggest some remedies for them. Do not add any numbers or special characters in
    your response. Your response should be in one long paragraph. Also always answer as if you are talking to a real person.
    Do not say 'In the image I see' but say 'So what I see, I presume you have .... '
    Dont respond as an AI model in markdown, your answer should mimic that of an actual doctor not an AI bot,
    Keep your answer concise. No preamble, start your answer right away please
    """
    
    # This function ensures the directories exist
    def _create_directories(self):
        """Ensure directories exist"""
        self.TEMP_DIR.mkdir(parents=True, exist_ok=True)
        self.PRESCRIPTION_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Created directories: {self.TEMP_DIR}, {self.PRESCRIPTION_DIR}")

# Singleton pattern
_config = None
def get_config() -> AppConfig:
    global _config
    if _config is None:
        _config = AppConfig()
    return _config
