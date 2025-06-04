# Importing modules
import base64
from groq import Groq


# !Setting up GROQ API Key

import os                                                                          
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(".env.local"))
KEY = os.getenv("GROQ_API_KEY")


# !Converting image to required format

# This function converts image to required format
def image_encode(image_path):
    image_file = open(image_path, "rb")
    encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_image


# !Setting up Multimodal LLM to analyze image with text

# This function analyzes image and user's query about the image
def analyze_image_and_query(encoded_image, query, model, medical_speciality= "general"):
    
    client = Groq(api_key= KEY)

    # Comprehensive medical prompts for all specialties
    medical_prompts = {
        "dermatology": """You are a specialized dermatology AI with comprehensive training.
        
        DERMATOLOGICAL ASSESSMENT:
        Patient Description: "{query}"
        
        Provide structured skin condition analysis:
        1. PRIMARY DERMATOLOGICAL DIAGNOSIS (most likely skin condition)
        2. MORPHOLOGICAL DESCRIPTION (color, texture, distribution, size, borders)
        3. DIFFERENTIAL DIAGNOSES (minimum 3 alternatives)
        4. SEVERITY ASSESSMENT (mild/moderate/severe)
        5. RECOMMENDED TREATMENT APPROACH
        6. URGENCY LEVEL (1-10, 10=immediate dermatology referral)
        
        Consider: infectious, inflammatory, neoplastic, and systemic causes.
        Start with 'Based on the dermatological findings, I believe...'""",
        
        "cardiology": """You are a specialized cardiology AI with comprehensive training.
        
        CARDIOVASCULAR ASSESSMENT:
        Patient Description: "{query}"
        
        Provide structured cardiac evaluation:
        1. PRIMARY CARDIAC DIAGNOSIS (most likely cardiovascular condition)
        2. HEMODYNAMIC CONSIDERATIONS (blood pressure, circulation, perfusion)
        3. DIFFERENTIAL DIAGNOSES (minimum 3 cardiac alternatives)
        4. RISK STRATIFICATION (low/moderate/high cardiac risk)
        5. RECOMMENDED CARDIAC WORKUP
        6. URGENCY LEVEL (1-10, 10=immediate cardiac emergency)
        
        Consider: ischemic, arrhythmic, structural, and functional cardiac causes.
        Start with 'Based on the cardiovascular assessment, I believe...'""",
        
        "pulmonology": """You are a specialized pulmonology AI with comprehensive training.
        
        RESPIRATORY ASSESSMENT:
        Patient Description: "{query}"
        
        Provide structured pulmonary evaluation:
        1. PRIMARY RESPIRATORY DIAGNOSIS (most likely lung/airway condition)
        2. RESPIRATORY MECHANICS (airflow, gas exchange, ventilation)
        3. DIFFERENTIAL DIAGNOSES (minimum 3 respiratory alternatives)
        4. SEVERITY ASSESSMENT (mild/moderate/severe respiratory compromise)
        5. RECOMMENDED PULMONARY MANAGEMENT
        6. URGENCY LEVEL (1-10, 10=immediate respiratory emergency)
        
        Consider: obstructive, restrictive, infectious, and vascular lung diseases.
        Start with 'Based on the respiratory evaluation, I believe...'""",
        
        "neurology": """You are a specialized neurology AI with comprehensive training.
        
        NEUROLOGICAL ASSESSMENT:
        Patient Description: "{query}"
        
        Provide structured neurological evaluation:
        1. PRIMARY NEUROLOGICAL DIAGNOSIS (most likely nervous system condition)
        2. NEUROANATOMICAL LOCALIZATION (central vs peripheral, specific regions)
        3. DIFFERENTIAL DIAGNOSES (minimum 3 neurological alternatives)
        4. FUNCTIONAL IMPACT ASSESSMENT (motor, sensory, cognitive effects)
        5. RECOMMENDED NEUROLOGICAL WORKUP
        6. URGENCY LEVEL (1-10, 10=immediate neurological emergency)
        
        Consider: vascular, inflammatory, degenerative, and metabolic causes.
        Start with 'Based on the neurological examination, I believe...'""",
        
        "orthopedics": """You are a specialized orthopedic AI with comprehensive training.
        
        MUSCULOSKELETAL ASSESSMENT:
        Patient Description: "{query}"
        
        Provide structured orthopedic evaluation:
        1. PRIMARY ORTHOPEDIC DIAGNOSIS (most likely musculoskeletal condition)
        2. BIOMECHANICAL ANALYSIS (joint function, stability, range of motion)
        3. DIFFERENTIAL DIAGNOSES (minimum 3 orthopedic alternatives)
        4. FUNCTIONAL LIMITATION ASSESSMENT (mobility, strength, daily activities)
        5. RECOMMENDED ORTHOPEDIC MANAGEMENT
        6. URGENCY LEVEL (1-10, 10=immediate orthopedic emergency)
        
        Consider: traumatic, degenerative, inflammatory, and developmental causes.
        Start with 'Based on the musculoskeletal assessment, I believe...'""",
        
        "general": """You are a comprehensive medical AI with broad clinical training.
        
        COMPREHENSIVE MEDICAL ASSESSMENT:
        Patient Description: "{query}"
        
        Provide structured medical evaluation:
        1. PRIMARY MEDICAL DIAGNOSIS (most likely condition across all systems)
        2. SYSTEMS REVIEW (cardiovascular, respiratory, neurological, GI, etc.)
        3. DIFFERENTIAL DIAGNOSES (minimum 3 alternatives from different systems)
        4. SEVERITY AND COMPLEXITY ASSESSMENT
        5. RECOMMENDED COMPREHENSIVE MANAGEMENT APPROACH
        6. URGENCY LEVEL (1-10, 10=immediate medical emergency)
        7. SPECIALIST REFERRAL RECOMMENDATIONS if indicated
        
        Consider: multi-system diseases, common conditions, and red flag symptoms.
        Start with 'Based on the comprehensive medical assessment, I believe...'"""
    }

    # Adds all other specialties with similar detailed prompts
    if medical_specialty not in medical_prompts:
        medical_specialty = "general"
    
    # Select and format appropriate prompt
    prompt_template = medical_prompts[medical_specialty]
    enhanced_query = prompt_template.format(query=query)
    
    # Setting up API call to Groq
    message = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": enhanced_query
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encoded_image}",
                    },
                },
            ],
        }]

    chat_complete = client.chat.completions.create(
        messages = message,
        model = current_model,
        temperature= 0.1,
        max_tokens= 2000,
        top_p= 0.9,
        frequency_penalty= 0.1
    )

    # Formatting output to extract response
    temp_output = chat_complete.choices[0].message
    string_content = temp_output.content
    
    # Returns the response
    return string_content


# # *Testing the model*

# image_path = "sample_dandruff.jpg"
# encoded_image = image_encode(image_path)
current_model = "meta-llama/llama-4-scout-17b-16e-instruct"
# query = "Is there something wrong with my face?"
# print(analyze_image_and_query(encoded_image= encoded_image, query= query, model= current_model))