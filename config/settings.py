# Importing modules
import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict
from config.languages import get_language_manager

@dataclass
class AppConfig:
    """Centralized Config Management"""
    
    # ElevenLabs TTS (using voice_id)
    ELEVENLABS_VOICES: Dict[str, Dict[str, str]] = field(default_factory=lambda: {
        "en": {
            "voice_id": "cgSgspJ2msm6clMCkdW9",
            "name": "Jessica"
        },
        "fr": {
            "voice_id": "K7gx0ylJdff0yjM2uVQS",
            "name": "Jeanne Mance - Female teacher, E-learning, Informative"
        }
    })
    
    # Audio settings for premium (using default_factory)
    ELEVENLABS_SETTINGS: Dict[str, any] = field(default_factory=lambda: {
        "stability": 0.75,
        "similarity_boost": 0.85,
        "style": 0.50,
        "use_speaker_boost": True
    })

    # Loads the local file containing API Keys
    def __init__(self):
        env_file = Path(".env.local")
        if env_file.exists():
            load_dotenv(env_file)

        self._create_directories()
        self.lang_manager = get_language_manager()
        
    # Loads API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    
    # Models Used
    STT_MODEL: str = "whisper-large-v3-turbo"
    LLM_MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    
    # Premium model for better quality
    ELEVENLABS_MODEL: str = "eleven_multilingual_v2"
    
    # Temporary path
    TEMP_DIR: Path = Path.cwd() / "temp"
    # Path for prescription
    PRESCRIPTION_DIR: Path = Path.cwd() / "prescriptions"

    def get_medical_prompt(self) -> str:
        """Gets medical prompt for medical analysis and recommendation"""
        return self.lang_manager.get_text("medical_prompt")

    def get_prescription_prompt(self, diagnosis: str, patient_name: str, patient_dob: str, patient_address: str, current_date: str) -> str:
        """Gets prescription prompt"""
        template = self.lang_manager.get_text("prescription_prompt")
        return template.format(
            diagnosis= diagnosis,
            patient_name= patient_name,
            patient_dob= patient_dob,
            patient_address= patient_address,
            current_date= current_date
        )

    # This function ensures the directories exist
    def _create_directories(self):
        """Ensures directories exist"""
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
