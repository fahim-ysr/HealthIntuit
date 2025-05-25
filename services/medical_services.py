# Importing modules
from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any
from datetime import datetime
import os
from scipy.io import wavfile
from pydub import AudioSegment
from config.settings import get_config
from groq import Groq
from core.fundamentals import image_encode, analyze_image_and_query
from core.input_voice import speech_to_text
from core.output_voice import text_to_speech, text_to_speech_elevenlabs
from config.languages import get_language_manager


class MedicalAnalysisService(ABC):
    """Abstract class for performing medical analysis"""
    
    # !Any future implementation must provide the function below
    @abstractmethod
    def process_patient_query(self, name: str, audio_path: str, image_path: str) -> Dict[str, Any]:
        pass


class HealthIntuitService(MedicalAnalysisService):
    """Performs Medical Analysis"""
    

    # Constructor function
    def __init__(self):
        self.config = get_config()
        self.lang_manager = get_language_manager()
    

    def _validate_inputs(self, name: str, audio_path: str, image_path: str) -> None:
        """Validates name, image and audio inputs with localized errors"""
        if not name or not name.strip():
            raise ValueError(self.lang_manager.get_text("error_name_required"))
        
        if not audio_path:
            raise ValueError(self.lang_manager.get_text("error_audio_required"))
            
        if not image_path:
            raise ValueError(self.lang_manager.get_text("error_image_required"))
    

    def _transcribe_audio(self, audio_path: str) -> str:
        """Transcribes patient's voice to text (Speech-To-Text) in current language"""
        try:
            # Gets current language from language manager
            current_lang = self.lang_manager.current_language

            return speech_to_text(
                model= self.config.STT_MODEL,
                path= audio_path,
                api_key= self.config.GROQ_API_KEY,
                language= current_lang
            )
        except Exception as e:
            raise Exception(f"Patient's audio transcription failed: {str(e)}")
    

    def _analyze_medical_image(self, image_path: str, query: str) -> str:
        """Analyzes medical image with patient query using localized prompt"""
        try:
            encoded_image = image_encode(image_path)
            localized_prompt = self.config.get_medical_prompt()
            full_query = f"{localized_prompt}\n{query}"
            
            return analyze_image_and_query(
                encoded_image=encoded_image,
                query=full_query,
                model=self.config.LLM_MODEL
            )
        except Exception as e:
            raise Exception(f"Image analysis failed: {str(e)}")
    
    

    def _generate_voice_response(self, text: str) -> Tuple[int, Any]:
        """Generates voice response from text (Text-To-Speech)"""
        try:
            # Ensures temp directory exists
            self.config.TEMP_DIR.mkdir(parents=True, exist_ok=True)

            output_path = self.config.TEMP_DIR / "doctors_response.mp3"

            # Gets current language
            current_lang = self.lang_manager.current_language
            
            # Generates TTS
            text_to_speech(response=text, path=str(output_path), lang=current_lang)    # General TTS
            # text_to_speech_elevenlabs(response=text, path=str(output_path), lang= current_lang)   # ElevenLabs TTS
            
            # Verifies file was created
            if not output_path.exists():
                raise FileNotFoundError(f"TTS failed to create file: {output_path}")
            
            # Converts audio to numpy array for Gradio
            temp_wav = self.config.TEMP_DIR / "temp.wav"
            audio_segment = AudioSegment.from_mp3(str(output_path))
            audio_segment.export(str(temp_wav), format="wav")
            
            sample_rate, audio_data = wavfile.read(str(temp_wav))
            
            # Cleanup
            if temp_wav.exists():
                os.remove(str(temp_wav))
            if output_path.exists():
                os.remove(str(output_path))
            
            return sample_rate, audio_data
            
        except Exception as e:
            print(f"Voice generation error details: {str(e)}")
            raise Exception(f"Doctor's voice generation failed: {str(e)}")
        
    
    def _generate_prescription(self, diagnosis: str, patient_name: str) -> Tuple[str, str]:
        """Generates formal prescription with localized prompt"""
        try:
            self.config.PRESCRIPTION_DIR.mkdir(parents=True, exist_ok=True)
            
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Uses localized prescription prompt
            prompt = self.config.get_prescription_prompt(diagnosis, patient_name, current_date)

            client = Groq(api_key=self.config.GROQ_API_KEY)

            message = [{
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }]

            response = client.chat.completions.create(
                messages=message,
                model=self.config.LLM_MODEL,
                temperature=0.3
            )

            prescription_text = response.choices[0].message.content
            
            # Saves prescription file
            safe_name = "".join(c if c.isalnum() else "_" for c in patient_name)
            filename = f"prescription_{safe_name}_{datetime.now().strftime('%Y%m%d')}.txt"
            prescription_path = self.config.PRESCRIPTION_DIR / filename
            
            with open(prescription_path, "w", encoding='utf-8') as f:
                f.write(prescription_text)
            
            return prescription_text, str(prescription_path)
            
        except Exception as e:
            raise Exception(f"Prescription generation failed: {str(e)}")
    

    def process_patient_query(self, name: str, audio_path: str, image_path: str) -> Dict[str, Any]:
        """Main processing pipeline"""
        self._validate_inputs(name, audio_path, image_path)
        
        try:
            # Step 1: Transcribes patient's query audio
            transcription = self._transcribe_audio(audio_path)
            
            # Step 2: Analyzes image with transcription
            diagnosis = self._analyze_medical_image(image_path, transcription)
            
            # Step 3: Generates doctor's voice response
            sample_rate, audio_data = self._generate_voice_response(diagnosis)
            
            # Step 4: Generates doctor's prescription
            prescription_text, prescription_path = self._generate_prescription(diagnosis, name)
            
            return {
                "transcription": transcription,
                "diagnosis": diagnosis,
                "voice_response": (sample_rate, audio_data),
                "prescription_text": prescription_text,
                "prescription_file": prescription_path
            }
            
        except Exception as e:
            raise Exception(f"Medical analysis failed: {str(e)}")