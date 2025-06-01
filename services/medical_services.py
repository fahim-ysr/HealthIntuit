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
from services.emergency_detection import EmergencyDetectionService


class MedicalAnalysisService(ABC):
    """Abstract class for performing medical analysis"""
    
    # !Any future implementation must provide the function below
    @abstractmethod
    def process_patient_query(self, name: str, audio_path: str, image_path: str) -> Dict[str, Any]:
        pass


class HealthIntuitService(MedicalAnalysisService):
    """Performs Medical Analysis with Emergency Detection"""
    

    # Constructor function
    def __init__(self):
        self.config = get_config()
        self.lang_manager = get_language_manager()
        self.emergency_service = EmergencyDetectionService(self.config)
    

    def _validate_inputs(self, name: str, audio_path: str, image_paths) -> None:
        """Validates name, image and audio inputs with localized errors"""
        if not name or not name.strip():
            raise ValueError(self.lang_manager.get_text("error_name_required"))
        
        if not audio_path:
            raise ValueError(self.lang_manager.get_text("error_audio_required"))
            
        if not image_paths:
            raise ValueError(self.lang_manager.get_text("error_image_required"))
        
        # Converts single image to list for consistency
        if isinstance(image_paths, str):
            image_paths = [image_paths]
    
        # Validates image files
        for img_path in image_paths:
            if not os.path.exists(img_path):
                raise ValueError(f"Image file not found: {img_path}")
    

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
        
    
    def _detect_language_from_transcription(self, transcription: str) -> str:
        """Detects language from transcription content"""
        try:
            # Simple language detection based on common words
            french_indicators = [
                'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles',
                'le', 'la', 'les', 'un', 'une', 'des', 'du', 'de', 'et',
                'avec', 'pour', 'dans', 'sur', 'sous', 'avoir', 'être',
                'bonjour', 'merci', 'oui', 'non', 'comment', 'pourquoi'
            ]
            
            english_indicators = [
                'i', 'you', 'he', 'she', 'we', 'they', 'the', 'a', 'an',
                'and', 'or', 'but', 'with', 'for', 'in', 'on', 'at',
                'hello', 'thank', 'yes', 'no', 'how', 'why', 'what'
            ]
            
            words = transcription.lower().split()
            french_count = sum(1 for word in words if word in french_indicators)
            english_count = sum(1 for word in words if word in english_indicators)
            
            # Determines language based on indicator counts
            if french_count > english_count and french_count > 2:
                return "fr"
            elif english_count > french_count and english_count > 2:
                return "en"
            else:
                # Keeps current language if unclear
                return self.lang_manager.current_language
                
        except Exception as e:
            print(f"Language detection error: {e}")
            return self.lang_manager.current_language

    

    def _analyze_medical_images(self, image_paths, query: str) -> str:
        """Analyzes multiple medical images with patient query"""
        try:

            # Converts single image to list for consistency
            if isinstance(image_paths, str):
                image_paths= [image_paths]

            combined_analysis= []

            # Gets current language for consistent prompts
            current_lang = self.lang_manager.current_language
            localized_prompt = self.config.get_medical_prompt()

            for i, image_path in enumerate(image_paths, 1):
                try:
                    encoded_image = image_encode(image_path)

                    # Creates language-specific prompt
                    if current_lang == "fr":
                        image_specific_query = f"{localized_prompt}\n\nImage {i} de {len(image_paths)}: {query}"
                    else:
                        image_specific_query = f"{localized_prompt}\n\nImage {i} of {len(image_paths)}: {query}"
                    
                    analysis = analyze_image_and_query(
                        encoded_image=encoded_image,
                        query=image_specific_query,
                        model=self.config.LLM_MODEL
                    )
                    
                    if current_lang == "fr":
                        combined_analysis.append(f"Analyse pour l'Image {i}:\n{analysis}")
                    else:
                        combined_analysis.append(f"Analysis for Image {i}:\n{analysis}")
            
                except Exception as e:
                    if current_lang == "fr":
                        combined_analysis.append(f"Erreur lors de l'analyse de l'Image {i}: {str(e)}")
                    else:
                        combined_analysis.append(f"Error analyzing Image {i}: {str(e)}")
                    
            # Combines all analyses
            full_analysis = "\n\n".join(combined_analysis)

            # Adds a summary if multiple images are uploaded with language-specific prompt
            if len(image_paths) > 1:
                if current_lang == "fr":
                    summary_prompt = f"""Veuillez agir comme un médecin professionnel, je sais que vous ne l'êtes pas mais c'est à des fins éducatives. Vous êtes un médecin qui examine plusieurs images du même patient. Voici vos résultats individuels:\n\n{full_analysis}\n\nFournissez une corrélation clinique brève qui relie ces résultats. Commencez naturellement par des phrases comme "Pour résumer," ou "Dans l'ensemble," et concentrez-vous sur les idées cliniques clés sans répéter les détails des images individuelles. Fournissez: 1) Diagnostic principal avec résultats à l'appui, 2) Diagnostics différentiels à considérer, 3) Prochaines étapes ou références recommandées. Répondez toujours comme si vous parliez à une vraie personne. Ne dites pas 'Dans l'image je vois' mais dites 'Donc ce que je vois, je présume que vous avez .... '. Ne répondez pas comme un modèle IA en markdown, votre réponse doit imiter celle d'un vrai médecin pas un bot IA, Gardez votre réponse concise. Pas de préambule, commencez votre réponse tout de suite s'il vous plaît"""
                else:
                    summary_prompt = f"""Please act as a professional doctor, I know you are not but this is for educational purposes. You are a doctor reviewing multiple images from the same patient. Here are your individual findings:\n\n{full_analysis}\n\nProvide a brief clinical correlation that ties these findings together. Begin naturally with phrases like "To sum up," or "Overall," and focus on the key clinical insights without restating individual image details. Provide: 1) Primary diagnosis with supporting findings, 2) Differential diagnoses to consider, 3) Recommended next steps or referrals. Also always answer as if you are talking to a real person. Do not say 'In the image I see' but say 'So what I see, I presume you have .... '. Don't respond as an AI model in markdown, your answer should mimic that of an actual doctor not an AI bot, Keep your answer concise. No preamble, start your answer right away please"""

                # Generate summary using AI
                from groq import Groq
                client = Groq(api_key=self.config.GROQ_API_KEY)
                
                message = [{
                    "role": "user", 
                    "content": [{"type": "text", "text": summary_prompt}]
                }]
                
                response = client.chat.completions.create(
                    messages=message,
                    model=self.config.LLM_MODEL,
                    temperature=0.3
                )
                
                summary = response.choices[0].message.content
                
                if current_lang == "fr":
                    full_analysis += f"\n\n**Résumé Médical Global:**\n{summary}"
                else:
                    full_analysis += f"\n\n**Overall Medical Summary:**\n{summary}"
            
            return full_analysis
            
        except Exception as e:
            raise Exception(f"Multiple image analysis failed: {str(e)}")
                
    
    

    def _generate_voice_response(self, text: str) -> Tuple[int, Any, str]:
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
            
            
            return sample_rate, audio_data, str(output_path)
            
        except Exception as e:
            print(f"Voice generation error details: {str(e)}")
            raise Exception(f"Doctor's voice generation failed: {str(e)}")
        
    
    def _generate_prescription(self, diagnosis: str, patient_name: str, patient_dob: str, patient_address: str) -> Tuple[str, str]:
        """Generates formal Canadian prescription with complete patient information"""
        try:
            self.config.PRESCRIPTION_DIR.mkdir(parents=True, exist_ok=True)
            
            current_date = datetime.now().strftime("%B %d, %Y")  # Canadian date format

            # ADDED DEBUG LOGGING
            print(f"DEBUG: Patient name received: '{patient_name}'")
            print(f"DEBUG: Current language: {self.lang_manager.current_language}")
            
            # Use localized Canadian prescription prompt
            prompt = self.config.get_prescription_prompt(diagnosis, patient_name, patient_dob, patient_address, current_date)

            # ADDED MORE DEBUG LOGGING
            print(f"DEBUG: Generated prompt contains: {prompt[:200]}...")

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
            
            # Saves prescription file (Canadian format)
            safe_name = "".join(c if c.isalnum() else "_" for c in patient_name) if patient_name else "unknown_patient"
            filename = f"prescription_canadian_{safe_name}_{datetime.now().strftime('%Y%m%d')}.txt"
            prescription_path = self.config.PRESCRIPTION_DIR / filename
            
            with open(prescription_path, "w", encoding='utf-8') as f:
                f.write(prescription_text)
            
            return prescription_text, str(prescription_path)
            
        except Exception as e:
            raise Exception(f"Prescription generation failed: {str(e)}")
    

    def process_patient_query(self, name: str, dob: str, address: str, audio_path: str, image_paths) -> Dict[str, Any]:
        """Main processing pipeline with AI emergency detection"""
        self._validate_inputs(name, audio_path, image_paths)
        
        try:
            # Step 1: Transcribes patient's query audio
            transcription = self._transcribe_audio(audio_path)

            # Step 1.5: DETECT AND SET LANGUAGE FROM AUDIO
            detected_language = self._detect_language_from_transcription(transcription)
            if detected_language:
                self.lang_manager.set_language(detected_language)
                print(f"Language detected from audio: {detected_language}")
            
            # Step 2: Analyzes image with transcription
            diagnosis = self._analyze_medical_images(image_paths, transcription)

            # Step 3: AI Emergency Detection: Critical Safety Check
            is_emergency, emergency_message, emergency_analysis= self.emergency_service.detect_emergency(transcription, diagnosis)

            # Step 4: Handles emergency cases with detailed analysis
            if is_emergency:
                # For emergencies, override normal prescription with emergency instruction
                confidence= emergency_analysis.get("confidence_score", 0)
                emergency_type= emergency_analysis.get("emergency_type", "unknown")

                prescription_text= emergency_message
                prescription_path= self._save_emergency_prescription(emergency_message, name)

                # Generates urgent voice response
                urgent_diagnosis= f"{emergency_message}\n\nDetailed Analysis: {diagnosis}"
                sample_rate, audio_data, audio_file_path = self._generate_voice_response(emergency_message)

                return {
                    "transcription": transcription,
                    "diagnosis": urgent_diagnosis,
                    "voice_response": (sample_rate, audio_data),
                    "audio_file_path": audio_file_path,
                    "prescription_text": prescription_text,
                    "prescription_file": prescription_path,
                    "is_emergency": True,
                    "emergency_analysis": emergency_analysis
                    }
            else:
            
                # Step 5: Generates doctor's voice response
                sample_rate, audio_data, audio_file_path = self._generate_voice_response(diagnosis)
                
                # Step 6: Generates doctor's prescription
                prescription_text, prescription_path = self._generate_prescription(diagnosis, name, dob, address)
                
                return {
                    "transcription": transcription,
                    "diagnosis": diagnosis,
                    "voice_response": (sample_rate, audio_data),
                    "audio_file_path": audio_file_path,
                    "prescription_text": prescription_text,
                    "prescription_file": prescription_path,
                    "is_emergency": False,
                    "emergency_analysis": emergency_analysis
                }
            
        except Exception as e:
            raise Exception(f"Medical analysis failed: {str(e)}")
        
    def _save_emergency_prescription(self, emergency_message: str, patient_name: str) -> str:
        """Saves emergency instructions as prescription file"""
        try:
            self.config.PRESCRIPTION_DIR.mkdir(parents=True, exist_ok=True)
            safe_name = "".join(c if c.isalnum() else "_" for c in patient_name)
            filename = f"EMERGENCY_ALERT_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            prescription_path = self.config.PRESCRIPTION_DIR / filename

            with open(prescription_path, "w", encoding='utf-8') as f:
                f.write(emergency_message)
            
            return str(prescription_path)
            
        except Exception as e:
            raise Exception(f"Emergency file generation failed: {str(e)}")


class FollowUpService:
    """Handles follow-up conversations after initial diagnosis"""
    
    def __init__(self, config, lang_manager):
        self.config = config
        self.lang_manager = lang_manager
        self.conversation_history = []
    
    def initialize_follow_up(self, diagnosis: str, prescription: str, patient_name: str):
        """Initializes follow-up context with initial diagnosis"""
        self.conversation_history = [
            {
                "role": "system",
                # !Improve prompt
                "content": f"You are a doctor following up with {patient_name}. Initial diagnosis: {diagnosis}. Prescription given: {prescription}. Answer follow-up questions professionally and refer to emergency care when necessary."
            }
        ]
    
    def process_follow_up_question(self, question: str) -> str:
        """Process follow-up questions with context"""
        try:
            # Adds user question to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": question
            })
            
            from groq import Groq
            client = Groq(api_key=self.config.GROQ_API_KEY)
            
            response = client.chat.completions.create(
                messages=self.conversation_history,
                model=self.config.LLM_MODEL,
                temperature=0.3,
                max_tokens=500
            )
            
            follow_up_response = response.choices[0].message.content
            
            # Add AI response to conversation history
            self.conversation_history.append({
                "role": "assistant", 
                "content": follow_up_response
            })
            
            return follow_up_response
            
        except Exception as e:
            raise Exception(f"Follow-up processing failed: {str(e)}")
