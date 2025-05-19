# Importing modules
import re

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