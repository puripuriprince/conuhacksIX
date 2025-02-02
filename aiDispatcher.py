import re
import csv
from dotenv import load_dotenv
import os
import requests
import json
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import server

class OpenRouterAPI:
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_KEY')
        if not self.api_key:
            raise ValueError("OPENROUTER_KEY not found in environment variables")
        self.url = "https://openrouter.ai/api/v1/chat/completions"
    
    def generate_text(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/your-repo",  # Update with your actual site
            "X-Title": "AI Voice Assistant"
        }
        
        payload = {
            "model": "deepseek/deepseek-v3",  # Using DeepSeek v3 model
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(self.url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            else:
                raise ValueError("No response content found in API response")
                
        except requests.exceptions.RequestException as e:
            error_msg = f"OpenRouter API error: {str(e)}"
            print(error_msg)
            raise ValueError(error_msg)
        except (KeyError, IndexError) as e:
            error_msg = f"Unexpected API response format: {str(e)}"
            print(error_msg)
            raise ValueError(error_msg)

# ------------------------------
# Main Voice Assistant that integrates all modules
# ------------------------------
class Assistant:
    def __init__(self, text_generator, tts_engine, phone_caller):
        self.text_generator = text_generator
        self.tts_engine = tts_engine
        self.phone_caller = phone_caller

    def process_query(self, query):
        try:
            print("Generating response from AI...")
            response_text = self.text_generator.generate_text(query)
            print("Response:", response_text)
            return response_text
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            print(error_msg)
            raise ValueError(error_msg)

   
def main():
    api = OpenRouterAPI()
    assistant = Assistant(api)
    # S'occupe d'aller chercher les infos importantes
    def extraire_premiere_ligne(reader):
        next(reader)  # Ignorer l'en-tête
        first_row = next(reader)  # Lire la première ligne de données
        return first_row  # Retourner la ligne sous forme de liste

    def validate_phone_number(phone_number):
        pattern = r"^\d{10}$"
        return phone_number if re.match(pattern, phone_number) else None  # Retourne le numéro ou None

    # Ouvrir le fichier dans le même bloc
    with open("911.csv", mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)  # Créer le lecteur CSV
        liste_var = extraire_premiere_ligne(reader)  # Lire la première ligne après l'en-tête

    location = liste_var[0]
    phone = liste_var[1]
    situation = liste_var[2]

    if(validate_phone_number(phone)):
        print()
    else:
        if(phone[0] == 1):
            phone.pop(0)

    def classifier_ordre_urgence(situation):
        prompt = """You're a 911 dispatcher, here is the situation, class it from 1 to 5 on a level of urgency, respond only with the number
        = """ + situation
        response = assistant.process_query(prompt)

        print("Réponse de DeepSeek:", response)


    classifier_ordre_urgence(situation)
    
main()
