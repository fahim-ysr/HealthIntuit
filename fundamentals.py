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

image_path = "sample_dandruff.jpg"
encoded_image = image_encode(image_path)

# !Setting up Multimodal LLM to analyze image with text

def analyze_image_and_query(encoded_image, query, model):
    client = Groq(api_key= KEY)
    

    # Setting up API call to Groq
    message = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": query
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
        model = current_model
    )

    # Formatting output to extract response
    temp_output = chat_complete.choices[0].message
    string_content = temp_output.content
    
    # Returns the response
    return string_content


# Testing the model

current_model = "meta-llama/llama-4-scout-17b-16e-instruct"
query = "Is there something wrong with my face?"
print(analyze_image_and_query(encoded_image= encoded_image, query= query, model= current_model))