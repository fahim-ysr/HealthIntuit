# Importing Modules
from typing import Tuple, Dict, Any
from config.languages import get_language_manager
from groq import Groq
import json

class EmergencyDetectionService:
    """AI-powered emergency detection using contextual analysis"""
    

    def __init__(self, config):
        self.lang_manager = get_language_manager()
        self.config = config
    

    def detect_emergency(self, transcription: str, diagnosis: str) -> Tuple[bool, str, Dict[str, Any]]:
        """AI-powered emergency detection with contextual analysis"""
        try:
            # Creates comprehensive emergency analysis prompt
            emergency_prompt = self._create_emergency_analysis_prompt(transcription, diagnosis)
            
            # Gets AI analysis
            ai_analysis = self._get_ai_emergency_analysis(emergency_prompt)
            
            # Parses AI response
            emergency_data = self._parse_ai_response(ai_analysis)
            
            is_emergency = emergency_data.get("is_emergency", False)
            emergency_message = ""
            
            if is_emergency:
                emergency_message = self._generate_emergency_message(emergency_data)
            
            return is_emergency, emergency_message, emergency_data
            
        except Exception as e:
            # Fallback to conservative approach on error
            return False, "", {"error": str(e)}
    

    def _create_emergency_analysis_prompt(self, transcription: str, diagnosis: str) -> str:
        """Create comprehensive prompt for AI emergency analysis"""
        current_lang = self.lang_manager.current_language
        
        if current_lang == "fr":
            return f"""Vous êtes un médecin urgentiste expérimenté. Analysez les informations suivantes pour déterminer s'il s'agit d'une urgence médicale nécessitant un appel immédiat au 911.

            TRANSCRIPTION DU PATIENT: "{transcription}"
            DIAGNOSTIC AI: "{diagnosis}"

            Analysez le contexte complet, la gravité des symptômes, l'urgence temporelle et les facteurs de risque. Répondez UNIQUEMENT en JSON avec cette structure exacte:

            {{
                "is_emergency": true/false,
                "confidence_score": 0-100,
                "emergency_type": "cardiac/stroke/respiratory/trauma/poisoning/allergic/mental_health/none",
                "severity_level": "mild/moderate/severe/critical",
                "reasoning": "explication détaillée de votre décision",
                "time_sensitivity": "immediate/urgent/non_urgent",
                "red_flags": ["liste des signaux d'alarme détectés"],
                "recommendation": "action recommandée"
            }}

            Critères d'urgence:
            - Symptômes menaçant le pronostic vital
            - Douleur thoracique avec signes cardiaques
            - Difficultés respiratoires sévères
            - Signes d'AVC
            - Traumatismes graves
            - Réactions allergiques sévères
            - Idées suicidaires actives

            Soyez conservateur mais précis. Ne déclarez une urgence que si les symptômes nécessitent vraiment une intervention immédiate.
            """

        else:  # English
            return f"""You are an experienced emergency physician. Analyze the following information to determine if this is a medical emergency requiring immediate 911 call.

            PATIENT TRANSCRIPTION: "{transcription}"
            AI DIAGNOSIS: "{diagnosis}"

            Analyze the complete context, symptom severity, time sensitivity, and risk factors. Respond ONLY in JSON with this exact structure:

            {{
                "is_emergency": true/false,
                "confidence_score": 0-100,
                "emergency_type": "cardiac/stroke/respiratory/trauma/poisoning/allergic/mental_health/none",
                "severity_level": "mild/moderate/severe/critical",
                "reasoning": "detailed explanation of your decision",
                "time_sensitivity": "immediate/urgent/non_urgent",
                "red_flags": ["list of detected warning signs"],
                "recommendation": "recommended action"
            }}

            Emergency criteria:
            - Life-threatening symptoms
            - Chest pain with cardiac signs
            - Severe breathing difficulties
            - Stroke symptoms
            - Major trauma
            - Severe allergic reactions
            - Active suicidal ideation

            Be conservative but precise. Only declare emergency if symptoms truly require immediate intervention.
            """
    

    def _get_ai_emergency_analysis(self, prompt: str) -> str:
        """Gets AI analysis using Groq"""
        try:
            client = Groq(api_key=self.config.GROQ_API_KEY)
            
            response = client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                model=self.config.LLM_MODEL,
                temperature=0.1,  # Low temperature for consistent medical decisions
                max_tokens=800
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"AI emergency analysis failed: {str(e)}")
    

    def _parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """Parses AI JSON response with error handling"""
        try:
            # Clean response and extract JSON
            cleaned_response = ai_response.strip()

            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:-3]

            elif cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:-3]
            
            return json.loads(cleaned_response)
            
        except json.JSONDecodeError as e:
            # Fallback parsing for malformed JSON
            return self._fallback_parse(ai_response)
    
    def _fallback_parse(self, response: str) -> Dict[str, Any]:
        """Fallback parsing when JSON fails"""

        # Conservative fallback - looks for explicit emergency indicators
        response_lower = response.lower()
        
        emergency_indicators = [
            "is_emergency\": true",
            "\"is_emergency\":true", 
            "emergency: true",
            "call 911",
            "immediate medical attention"
        ]
        
        is_emergency = any(indicator in response_lower for indicator in emergency_indicators)
        
        return {
            "is_emergency": is_emergency,
            "confidence_score": 50,
            "emergency_type": "unknown",
            "severity_level": "moderate",
            "reasoning": "Fallback analysis due to parsing error",
            "time_sensitivity": "urgent" if is_emergency else "non_urgent",
            "red_flags": [],
            "recommendation": "Seek immediate medical attention" if is_emergency else "Monitor symptoms"
        }
    
    def _generate_emergency_message(self, emergency_data: Dict[str, Any]) -> str:
        """Generates contextual emergency message"""
        current_lang = self.lang_manager.current_language
        emergency_type = emergency_data.get("emergency_type", "unknown")
        reasoning = emergency_data.get("reasoning", "")
        
        # For French
        if current_lang == "fr":
            return f"""
            🚨 URGENCE MÉDICALE DÉTECTÉE 🚨

            Type d'urgence: {emergency_type.upper()}
            Niveau de confiance: {emergency_data.get('confidence_score', 0)}%

            {reasoning}

            ⚠️ APPELEZ LE 911 IMMÉDIATEMENT ⚠️

            Actions immédiates:
            - Ne conduisez pas vous-même
            - Appelez une ambulance maintenant
            - Restez calme et suivez les instructions du répartiteur

            Cette application est uniquement à des fins éducatives et ne remplace pas les soins médicaux d'urgence professionnels."""
                    
        else:  # English
            return f"""
            🚨 MEDICAL EMERGENCY DETECTED 🚨

            Emergency Type: {emergency_type.upper()}
            Confidence Level: {emergency_data.get('confidence_score', 0)}%

            {reasoning}

            ⚠️ CALL 911 IMMEDIATELY ⚠️

            Immediate Actions:
            - Do not drive yourself
            - Call an ambulance now
            - Stay calm and follow dispatcher instructions

            This application is for educational purposes only and does not replace professional emergency medical care.
            """
