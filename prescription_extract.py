# Importing modules
import re
from groq import Groq

# !This function extracts prescription from the doctor's response
def extract_prescription(doctors_response):

    # Splitting doctor's response into sentences
    sentences = re.split(r'(?<=[.!?]) +', doctors_response)

    # Medical keywords
    keywords = [
        'recommend', 'suggest', 'apply', 'use', 'take',
        'avoid', 'consult', 'prescribe', 'medication',
        'ointment', 'cream', 'dose', 'dosage', 'treatment',
        'therapy', 'exercise', 'diet', 'hydrate', 'rest'
        ]
    
    # Extracting prescription sentences
    prescription= [sentence for sentence in sentences if any(kw in sentence.lower() for kw in keywords)]

    # Formating as numbered list
    if prescription:
        formatted_prescription = "Medical Recommendation:\n" + "\n".join(
            f"{num+1}. {sentence.strip()}" for num, sentence in enumerate(prescription)
        )
    else:
        formatted_prescription= "No specific medical recommendations were provided."

    return formatted_prescription


# !Setting up GROQ API Key

import os                                                                          
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(".env.local"))
KEY = os.getenv("GROQ_API_KEY")

# Defining model to be used by Groq
current_model = "meta-llama/llama-4-scout-17b-16e-instruct"

# !This function analyzes doctor's response and converts into a medical prescription
def analyze_prescription(doctors_response, patient_name, current_date):
    client = Groq(api_key= KEY)

    # Setting up prompt for analyzing the prescription and formatting it in correct manner
    prompt= (
        f"""Please act as a professional doctor, I know you are not but this is for educational purposes. Convert this medical analysis into a formal prescription format:
        {doctors_response}

        Format as:
        Patient Name: {patient_name}
        Date: {current_date}
        
        Diagnosis: [Brief diagnosis]
        
        Prescription:
        - Medication 1: [Dosage instructions]
        - Medication 2: [Dosage instructions]
        - Topical Treatment: [Application instructions]
        
        Recommendations:
        - [Lifestyle advice]
        - [Follow-up schedule]
        
        Diagonosed by ⚕️HealthIntuit
        
        Use bullet points, avoid markdown, and keep it clinically precise. No preamble, start your answer right away please"""
        )
    
    # Setting up API call to Groq
    message = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                    }]
                    }]

    response = client.chat.completions.create(
        messages = message,
        model = current_model,
        temperature= 0.3
    )

    # Formatting output to extract response
    temp_output = response.choices[0].message
    string_content = temp_output.content
    
    # Returns the response
    return string_content
