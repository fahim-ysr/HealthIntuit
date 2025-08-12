from typing import List, Dict, Any, Tuple
from datetime import datetime
import re
from groq import Groq
from config.settings import get_config
from config.languages import get_language_manager


class QueryGenerator():
    """Generates contextual medical search queries from patient's data"""


    def __init__(self):
        self.config = get_config
        self.lang_manager = get_language_manager
        self.client = Groq(api_key=self.config.GROQ_API_KEY)


    def generate_medical_queries(self, transcription:str, diagnosis:str, patient_data: Dict[str, str] = None) -> Dict[str, List[str]]:
        """Generates medical queries and returns categorized queries for different medical contexts"""

        try:
            # Extracts medical entities
            medical_entities = self.extract_medical_entities(transcription, diagnosis)

            # Generates query
            query_categories = {
                "primary_condition": self.generate_primary_condition_queries(medical_entities),
                "differential_diagnosis": self.generate_differential_queries(medical_entities),
                "treatment_guidelines": self.generate_treatment_queries(medical_entities),
                "regional_context": self.generate_regional_queries(medical_entities, patient_data),
                "temporal_context": self.generate_temporal_queries(medical_entities)
            }

            # Adds image-specific queries if visual symptoms detected
            if self.has_visual_symptoms(medical_entities):
                query_categories["visual_diagnostics"] = self.generate_visual_diagnosis_queries(medical_entities)
            
            return query_categories
        
        except Exception as e:
            raise Exception(f"Query generation failed: {str(e)}")


    def extract_medical_entities(self, transcription: str, diagnosis: str) -> Dict[str, Any]:
        """Extract medical entities using AI"""
        current_lang = self.lang_manager.current_language
        
        if current_lang == "fr":
            extraction_prompt = f"""
            Analysez le texte médical suivant et extrayez les entités médicales clés.
            
            TRANSCRIPTION DU PATIENT: "{transcription}"
            DIAGNOSTIC IA: "{diagnosis}"
            
            Extrayez et structurez les informations suivantes en JSON:
            {{
                "symptoms": ["liste des symptômes mentionnés"],
                "body_parts": ["parties du corps affectées"],
                "severity_indicators": ["mots indiquant la gravité"],
                "temporal_keywords": ["mots temporels comme 'récent', 'chronique'"],
                "primary_condition": "condition principale probable",
                "associated_conditions": ["conditions associées possibles"],
                "visual_symptoms": ["symptômes visuels comme éruption, rougeur"],
                "functional_impact": ["impact sur les activités quotidiennes"]
            }}
            
            Répondez uniquement en JSON valide.
            """
        else:
            extraction_prompt = f"""
            Analyze the following medical text and extract key medical entities.
            
            PATIENT TRANSCRIPTION: "{transcription}"
            AI DIAGNOSIS: "{diagnosis}"
            
            Extract and structure the following information in JSON:
            {{
                "symptoms": ["list of mentioned symptoms"],
                "body_parts": ["affected body parts"],
                "severity_indicators": ["words indicating severity"],
                "temporal_keywords": ["temporal words like 'recent', 'chronic'"],
                "primary_condition": "likely primary condition",
                "associated_conditions": ["possible associated conditions"],
                "visual_symptoms": ["visual symptoms like rash, redness"],
                "functional_impact": ["impact on daily activities"]
            }}
            
            Respond only with valid JSON.
            """
        
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": extraction_prompt}],
                model=self.config.LLM_MODEL,
                temperature=0.1,
                max_tokens=800
            )
            
            import json
            entities_text = response.choices[0].message.content.strip()
            
            # Cleaning JSON response
            if entities_text.startswith("```json"):
                entities_text = entities_text[7:-3]
            elif entities_text.startswith("```"):
                entities_text = entities_text[3:-3]
            
            return json.loads(entities_text)
            
        except Exception as e:
            # Fallbacks to basic entity extraction
            return self.fallback_entity_extraction(transcription, diagnosis)


    def generate_primary_condition_queries(self, entities: Dict[str, Any]) -> List[str]:
        """Generates queries on the primary condition"""
        queries = []
        primary_condition = entities.get("primary_condition", "")
        symptoms = entities.get("symptoms", [])
        current_year = datetime.now().year
        
        if primary_condition and primary_condition != "unknown":
            queries.extend([
                f"{primary_condition} clinical diagnosis {current_year}",
                f"{primary_condition} diagnostic criteria latest guidelines",
                f"{primary_condition} evidence-based treatment protocols"
            ])
        
        # Symptom-based queries
        if len(symptoms) >= 2:
            symptom_combination = " + ".join(symptoms[:3])
            queries.extend([
                f"{symptom_combination} differential diagnosis",
                f"{symptom_combination} clinical presentation",
                f"{symptom_combination} diagnostic workup"
            ])

        return queries


    def generate_differential_queries(self, entities: Dict[str, Any]) -> List[str]:
        """Generates queries for differential diagnosis"""
        queries = []
        symptoms = entities.get("symptoms", [])
        body_parts = entities.get("body_parts", [])
        associated_conditions = entities.get("associated_conditions", [])
        
        # Multi-symptom differential queries
        if len(symptoms) >= 2:
            for i in range(len(symptoms)-1):
                query = f"{symptoms[i]} vs {symptoms[i+1]} differential diagnosis"
                queries.append(query)
        
        # Body part specific differentials
        for body_part in body_parts:
            if symptoms:
                queries.append(f"{body_part} {symptoms[0]} differential diagnosis 2025")
        
        # Associated condition queries
        for condition in associated_conditions:
            queries.append(f"{condition} clinical features diagnostic criteria")
        
        return queries


    def generate_treatment_queries(self, entities: Dict[str, Any]) -> List[str]:
        """Generates treatment queries"""
        queries = []
        primary_condition = entities.get("primary_condition", "")
        symptoms = entities.get("symptoms", [])
        
        if primary_condition and primary_condition != "unknown":
            queries.extend([
                f"{primary_condition} first-line treatment guidelines",
                f"{primary_condition} management protocol Canada",
                f"{primary_condition} pharmacological therapy recommendations"
            ])
        
        # Symptom-specific treatment
        for symptom in symptoms[:2]:  # Focus on top 2 symptoms
            queries.extend([
                f"{symptom} treatment options evidence-based",
                f"{symptom} management clinical guidelines"
            ])
        
        return queries
    

    def generate_regional_queries(self, entities: Dict[str, Any], patient_data: Dict[str, str] = None) -> List[str]:
        """Generates region-specific queries"""
        queries = []
        primary_condition = entities.get("primary_condition", "")
        region = "Canada"
        
        if primary_condition and primary_condition != "unknown":
            queries.extend([
                f"{primary_condition} prevalence Canada {datetime.datetime.now().year}",
                f"{primary_condition} epidemiology Canadian population",
                f"{primary_condition} treatment guidelines Canada health"
            ])


    def generate_visual_diagnosis_queries(self, entities: Dict[str, Any]) -> List[str]:
        """Generates queries for visual diagnostic criteria"""
        queries = []
        visual_symptoms = entities.get("visual_symptoms", [])
        primary_condition = entities.get("primary_condition", "")
        
        for visual_symptom in visual_symptoms:
            queries.extend([
                f"{visual_symptom} visual diagnostic criteria",
                f"{visual_symptom} clinical photography comparison",
                f"{visual_symptom} differential visual diagnosis"
            ])
        
        if primary_condition and primary_condition != "unknown":
            queries.extend([
                f"{primary_condition} visual appearance clinical images",
                f"{primary_condition} morphology diagnostic features"
            ])
        
        return queries
    

    def fallback_entity_extraction(self, transcription: str, diagnosis: str) -> Dict[str, Any]:
        """Alternative entity extraction method using pattern matching"""
        text = f"{transcription} {diagnosis}".lower()
        
        # Basic symptom patterns
        common_symptoms = [
            "pain", "ache", "swelling", "redness", "itching", "burning", 
            "rash", "spots", "bumps", "fever", "nausea", "headache"
        ]
        
        body_parts = [
            "head", "face", "neck", "chest", "back", "arm", "leg", 
            "hand", "foot", "skin", "eye", "ear", "throat"
        ]
        
        found_symptoms = [symptom for symptom in common_symptoms if symptom in text]
        found_body_parts = [part for part in body_parts if part in text]
        
        return {
            "symptoms": found_symptoms,
            "body_parts": found_body_parts,
            "severity_indicators": [],
            "temporal_keywords": [],
            "primary_condition": "unknown",
            "associated_conditions": [],
            "visual_symptoms": [],
            "functional_impact": []
        }
    

    def generate_temporal_queries(self, entities: Dict[str, Any]) -> List[str]:
        """Generates time-sensitive queries"""
        queries = []
        primary_condition = entities.get("primary_condition", "")
        current_year = datetime.now().year
        current_month = datetime.now().strftime("%B")
        
        if primary_condition and primary_condition != "unknown":
            queries.extend([
                f"{primary_condition} recent outbreaks {current_year}",
                f"{primary_condition} seasonal patterns {current_month}",
                f"{primary_condition} latest research {current_year}",
                f"{primary_condition} emerging treatments {current_year}"
            ])

        # Recent guideline updates
        queries.append(f"medical guidelines updates {current_year} {primary_condition}")
        
        return queries
    

    def has_visual_symptoms(self, entities: Dict[str, Any]) -> bool:
        """Checks if condition has visual diagnostic components"""
        visual_keywords = [
            "rash", "redness", "swelling", "spots", "bumps", "lesions",
            "discoloration", "bruising", "eruption", "patch"
        ]
        
        symptoms = entities.get("symptoms", [])
        visual_symptoms = entities.get("visual_symptoms", [])
        
        return any(keyword in " ".join(symptoms + visual_symptoms).lower() 
                  for keyword in visual_keywords)
    
    
    def get_current_season(self) -> str:
        """Gets current season for context"""
        month = datetime.now().month
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "fall"


    def format_queries_for_search(self, query_categories: Dict[str, List[str]]) -> List[str]:
        """Formats queries for external search APIs"""
        prioritized_queries = []
        
        # Priority order for query categories
        priority_order = [
            "primary_condition",
            "differential_diagnosis", 
            "treatment_guidelines",
            "visual_diagnostics",
            "regional_context",
            "temporal_context"
        ]
        
        for category in priority_order:
            if category in query_categories:
                # Takes top 3 queries from each category
                prioritized_queries.extend(query_categories[category][:3])
        
        # Removes duplicate while preserving order
        seen = set()
        unique_queries = []
        for query in prioritized_queries:
            if query.lower() not in seen:
                seen.add(query.lower())
                unique_queries.append(query)
        
        return unique_queries[:15]  # Limit to top 15 queries