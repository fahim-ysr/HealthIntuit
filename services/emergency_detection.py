# Importing Modules
from typing import List, Dict, Tuple
from config.languages import get_language_manager


class EmergencyDetectionService:
    """Detects emergency symptoms and recommends immediate medical attention"""
    
    def __init__(self):
        self.lang_manager = get_language_manager()
        self.emergency_keywords = self._load_emergency_keywords()
    
    def _load_emergency_keywords(self) -> Dict[str, List[str]]:
        """Loads emergency keywords in EN and FR"""
        return {
            
            "en": {
                "cardiac": ["chest pain", "heart attack", "cardiac arrest", "crushing chest pain", 
                          "left arm pain", "jaw pain", "shortness of breath with chest pain"],
                "stroke": ["sudden weakness", "face drooping", "arm weakness", "speech difficulty",
                         "sudden confusion", "sudden severe headache", "vision loss"],
                "respiratory": ["can't breathe", "difficulty breathing", "choking", "severe asthma"],
                "trauma": ["severe bleeding", "head injury", "unconscious", "severe burn",
                         "broken bone protruding", "car accident"],
                "poisoning": ["overdose", "poisoning", "swallowed poison", "chemical exposure"],
                "allergic": ["severe allergic reaction", "anaphylaxis", "throat swelling", "hives with breathing"],
                "mental_health": ["suicidal thoughts", "want to hurt myself", "suicide attempt"]
            },

            "fr": {
                "cardiac": ["douleur thoracique", "crise cardiaque", "arrêt cardiaque", "douleur écrasante à la poitrine",
                          "douleur au bras gauche", "douleur à la mâchoire", "essoufflement avec douleur thoracique"],
                "stroke": ["faiblesse soudaine", "affaissement du visage", "faiblesse du bras", "difficulté d'élocution",
                         "confusion soudaine", "mal de tête sévère soudain", "perte de vision"],
                "respiratory": ["ne peut pas respirer", "difficulté à respirer", "étouffement", "asthme sévère"],
                "trauma": ["saignement sévère", "blessure à la tête", "inconscient", "brûlure sévère",
                         "os cassé qui dépasse", "accident de voiture"],
                "poisoning": ["surdose", "empoisonnement", "poison avalé", "exposition chimique"],
                "allergic": ["réaction allergique sévère", "anaphylaxie", "gonflement de la gorge", "urticaire avec respiration"],
                "mental_health": ["pensées suicidaires", "veux me faire du mal", "tentative de suicide"]
            }
        }
    
    def detect_emergency(self, transcription: str, diagnosis: str) -> Tuple[bool, str, List[str]]:
        """Detects if case requires emergency intervention"""
        current_lang = self.lang_manager.current_language
        keywords = self.emergency_keywords.get(current_lang, self.emergency_keywords["en"])
        
        detected_emergencies = []
        emergency_found = False
        
        # Combine transcription and diagnosis for analysis
        full_text = f"{transcription.lower()} {diagnosis.lower()}"
        
        # Check for emergency keywords
        for category, keyword_list in keywords.items():
            for keyword in keyword_list:
                if keyword.lower() in full_text:
                    detected_emergencies.append(category)
                    emergency_found = True
                    break
        
        # Generate emergency message
        emergency_message = self._generate_emergency_message(detected_emergencies)
        
        return emergency_found, emergency_message, detected_emergencies
    
    def _generate_emergency_message(self, emergencies: List[str]) -> str:
        """Generates appropriate emergency message"""
        if not emergencies:
            return ""
        
        current_lang = self.lang_manager.current_language
        
        if current_lang == "fr":
            return """
            🚨 URGENCE MÉDICALE DÉTECTÉE 🚨

            Vos symptômes suggèrent une urgence médicale qui nécessite une attention immédiate.

            ⚠️ APPELEZ LE 911 IMMÉDIATEMENT ⚠️

            Ne conduisez pas vous-même - appelez une ambulance ou demandez à quelqu'un de vous conduire aux urgences maintenant.

            Cette application est uniquement à des fins éducatives et ne remplace pas les soins médicaux d'urgence professionnels.
            """
                    
        else:  # English
            return """
            🚨 MEDICAL EMERGENCY DETECTED 🚨

            Your symptoms suggest a medical emergency that requires immediate attention.

            ⚠️ CALL 911 IMMEDIATELY ⚠️

            Do not drive yourself - call an ambulance or have someone drive you to the emergency room now.

            This application is for educational purposes only and does not replace professional emergency medical care.
            """
