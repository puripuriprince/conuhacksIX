#!/usr/bin/env python3
"""
Assistant.py – A minimal voice-enabled AI assistant
 • Uses DeepSeek v3 for text generation
 • Uses ElevenLabs for text-to-speech synthesis
 • Integrates phone calling (via Twilio)
"""
import time
import csv
import os
import re
import sys
import json
import requests
from dotenv import load_dotenv
import Database

# Load environment variables
load_dotenv()

# ------------------------------
# OpenRouter API for Text Generation
# ------------------------------
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
            "HTTP-Referer": "dispatcher",
            "X-Title": "ConUHacks Voice Assistant"
        }
        
        # System prompt for 911 dispatcher behavior
        system_prompt = {
            "role": "system",
            "content": """You are a professional emergency evaluator, you resume information so the dispatcher can easily understand the situation. Follow the rules i ask in each prompts"""
        }
        
        # Format messages for chat completion
        messages = []
        if isinstance(prompt, str):
            # Single prompt string
            messages = [system_prompt, {"role": "user", "content": prompt}]
        else:
            # Assuming prompt is already in message format
            # Insert system prompt at the beginning if it's not already there
            if not any(msg.get("role") == "system" for msg in prompt):
                messages = [system_prompt] + prompt
            else:
                messages = prompt
        
        payload = {
            "model": "openai/gpt-3.5-turbo",  # Using GPT-3.5 for faster responses
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            print(f"\nSending request to OpenRouter API...")
            print(f"Messages: {json.dumps(messages, indent=2)}")
            
            response = requests.post(self.url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            print(f"OpenRouter API Response: {json.dumps(data, indent=2)}")
            
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
class VoiceAssistant:
    def __init__(self, text_generator):
        self.text_generator = text_generator

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

    def handle_interaction(self, prompt):
        # Basic interactive loop (could be easily extended to voice input)
        response_text = self.process_query(prompt)
        return response_text



# ------------------------------
# Main Execution
# ------------------------------
def main():
    database = Database
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

    def recuperer_info(situation):
         # Le rang de la situation
        prompt_category = """Class the situation in one of these category : Police Emergencies, Firefighter Emergencies, Medical Emergencies, Unknown  respond only with the name of the category and nothing else :
        Police Emergencies 🚔
1. Urgent (Immediate danger, requires immediate police intervention)
"Someone is trying to break into my house right now!"
"I just heard gunshots in the street!"
"A person with a weapon is threatening someone in a store!"
"A woman is being assaulted right in front of me!"
2. Moderate (Concerning situation requiring a police response, but not immediately life-threatening)
"A fight just broke out in front of a bar, and people are getting aggressive."
"A suspicious car has been parked in front of my house for hours, and someone inside seems to be watching me."
"My neighbor is yelling and breaking things, I’m worried someone might get hurt."
"I saw someone trying to open multiple car doors in the parking lot."
3. Low Severity (Not urgent, can be reported later)
"I noticed someone spray-painted graffiti on a nearby wall."
"My bicycle was stolen overnight, and I’d like to file a report."
"There are people hanging around my neighborhood late at night, it makes me uneasy."
"I received a suspicious phone call that seemed like a scam attempt."
4. Undetermined (Lack of details or unclear situation)
"Something strange is happening in front of my house."
"I’m not sure, but something feels off in my building."
"A group of people is talking loudly outside, and I have a bad feeling."
"I think someone might be following me, but I’m not sure."

Firefighter Emergencies 🚒🔥
1. Urgent (Immediate danger, requires immediate firefighter intervention)
"My kitchen is on fire, and the flames are spreading!"
"A building across the street is on fire, and the smoke is getting thick!"
"A wildfire is spreading quickly toward houses!"
"There was an explosion in a warehouse, and people might still be inside!"
2. Moderate (Potential risk, requiring quick firefighter response)
"I saw some teenagers starting a fire in an empty lot, and it could spread."
"A power pole caught fire after a storm, and there are sparks."
"A neighbor’s chimney is emitting thick black smoke, more than usual."
"There’s a gas leak in my building, but I can’t smell a strong odor yet."
3. Low Severity (Not urgent, but might require follow-up or monitoring)
"I noticed a faint smell of something burning in my building, but I don’t see smoke or flames."
"There’s a wasp nest under my roof, and I’m wondering if the firefighters can help."
"A tree fell on the road after a storm, but it’s not completely blocking traffic."
"I saw a small pile of smoldering ashes in the park, and I put water on it, but it could reignite."
4. Undetermined (Lack of details or unclear situation)
"I think I see smoke somewhere, but I’m not sure where it’s coming from."
"I hear a fire alarm going off in my neighborhood, but I don’t see anything."
"Someone shouted ‘fire’ in the street, but I don’t see flames."
"It feels unusually hot in my house, but I can’t find the source."

Medical Emergencies 🚑
1. Urgent (Immediate danger, requires immediate medical intervention)
"My father collapsed and isn’t breathing!"
"I’m having sudden, intense chest pain, and I can’t breathe properly!"
"Someone was in a car accident, they’re bleeding heavily and not moving!"
"A child swallowed something and is choking!"
2. Moderate (Concerning medical condition requiring urgent care but not life-threatening)
"I have had a high fever and severe muscle pain for three days."
"I have had sharp stomach pain for hours."
"I twisted my ankle while running, and it’s swollen. I can’t walk properly."
"My child has vomited multiple times today and seems very weak."
3. Low Severity (Non-urgent medical concerns, can be managed with basic care or a scheduled appointment)
"I have a small cut on my finger, but it has stopped bleeding."
"I’ve had a cold for a few days and need advice on what to take."
"My child has a small bruise on their knee after falling but is walking fine."
"I have mild back pain after lifting something, but it gets better with rest."
4. Undetermined (Lack of details or unclear situation)
"I don’t feel well."
"There’s a problem, but I don’t know what to do."
"Someone fell, but I don’t know if they are okay."
"I have pain somewhere, but it’s hard to describe."

"""    
        category = classifier_info_urgence(situation, prompt_category)
        # Le rang de la situation
        prompt_rang = """Class the situation from 1 to 4 on a level of urgency, 1 being the most urgent, respond only with the number and the number only.
        Police Emergencies 🚔
1. Urgent (Immediate danger, requires immediate police intervention)
"Someone is trying to break into my house right now!"
"I just heard gunshots in the street!"
"A person with a weapon is threatening someone in a store!"
"A woman is being assaulted right in front of me!"
2. Moderate (Concerning situation requiring a police response, but not immediately life-threatening)
"A fight just broke out in front of a bar, and people are getting aggressive."
"A suspicious car has been parked in front of my house for hours, and someone inside seems to be watching me."
"My neighbor is yelling and breaking things, I’m worried someone might get hurt."
"I saw someone trying to open multiple car doors in the parking lot."
3. Low Severity (Not urgent, can be reported later)
"I noticed someone spray-painted graffiti on a nearby wall."
"My bicycle was stolen overnight, and I’d like to file a report."
"There are people hanging around my neighborhood late at night, it makes me uneasy."
"I received a suspicious phone call that seemed like a scam attempt."
4. Undetermined (Lack of details or unclear situation)
"Something strange is happening in front of my house."
"I’m not sure, but something feels off in my building."
"A group of people is talking loudly outside, and I have a bad feeling."
"I think someone might be following me, but I’m not sure."

Firefighter Emergencies 🚒🔥
1. Urgent (Immediate danger, requires immediate firefighter intervention)
"My kitchen is on fire, and the flames are spreading!"
"A building across the street is on fire, and the smoke is getting thick!"
"A wildfire is spreading quickly toward houses!"
"There was an explosion in a warehouse, and people might still be inside!"
2. Moderate (Potential risk, requiring quick firefighter response)
"I saw some teenagers starting a fire in an empty lot, and it could spread."
"A power pole caught fire after a storm, and there are sparks."
"A neighbor’s chimney is emitting thick black smoke, more than usual."
"There’s a gas leak in my building, but I can’t smell a strong odor yet."
3. Low Severity (Not urgent, but might require follow-up or monitoring)
"I noticed a faint smell of something burning in my building, but I don’t see smoke or flames."
"There’s a wasp nest under my roof, and I’m wondering if the firefighters can help."
"A tree fell on the road after a storm, but it’s not completely blocking traffic."
"I saw a small pile of smoldering ashes in the park, and I put water on it, but it could reignite."
4. Undetermined (Lack of details or unclear situation)
"I think I see smoke somewhere, but I’m not sure where it’s coming from."
"I hear a fire alarm going off in my neighborhood, but I don’t see anything."
"Someone shouted ‘fire’ in the street, but I don’t see flames."
"It feels unusually hot in my house, but I can’t find the source."

Medical Emergencies 🚑
1. Urgent (Immediate danger, requires immediate medical intervention)
"My father collapsed and isn’t breathing!"
"I’m having sudden, intense chest pain, and I can’t breathe properly!"
"Someone was in a car accident, they’re bleeding heavily and not moving!"
"A child swallowed something and is choking!"
2. Moderate (Concerning medical condition requiring urgent care but not life-threatening)
"I have had a high fever and severe muscle pain for three days."
"I have had sharp stomach pain for hours."
"I twisted my ankle while running, and it’s swollen. I can’t walk properly."
"My child has vomited multiple times today and seems very weak."
3. Low Severity (Non-urgent medical concerns, can be managed with basic care or a scheduled appointment)
"I have a small cut on my finger, but it has stopped bleeding."
"I’ve had a cold for a few days and need advice on what to take."
"My child has a small bruise on their knee after falling but is walking fine."
"I have mild back pain after lifting something, but it gets better with rest."
4. Undetermined (Lack of details or unclear situation)
"I don’t feel well."
"There’s a problem, but I don’t know what to do."
"Someone fell, but I don’t know if they are okay."
"I have pain somewhere, but it’s hard to describe."

"""    
        rang = classifier_info_urgence(situation, prompt_rang)
        # Titre de la situation
        prompt_titre = """Given a description of an emergency situation, generate a short and clear title summarizing the main topic of the call. The title should be concise, informative, and immediately understandable at a glance."""
        titre = classifier_info_urgence(situation, prompt_titre)
        # Courte description de la situation
        prompt_resume = """Given a description of an emergency situation, generate a short summary of the situation. The summary should be brief (2-3 sentences) and provide a quick overview of the main events or issues."""
        descr = classifier_info_urgence(situation, prompt_resume)
        return [rang, descr, titre, category]

    def classifier_info_urgence(situation, prompt):
        try:
            # Instantiate the modules
            text_generator = OpenRouterAPI()  # Using OpenRouter for DeepSeek
            prompt = prompt + "situation : " + situation
            assistant = VoiceAssistant(text_generator)
            assistant.handle_interaction(situation)    
            time.sleep(5)      
        except ValueError as e:
            print(f"Error initializing assistant: {e}")
            sys.exit(1)

        response = assistant.handle_interaction(prompt)
        return response


    # Fonction pour traiter et supprimer la ligne après traitement
    def traiter_csv():
        liste_info = []
        with open("911.csv", mode='r+', encoding='utf-8') as file:
            reader = csv.reader(file)
            rows = list(reader)  # Lire toutes les lignes du fichier

            # Vérifier s'il y a des lignes à traiter
            if len(rows) <= 1:  # Si le fichier est vide (ou juste l'entête)
                print("Fichier vide ou plus de données à traiter.")
                return
            
            # Parcours chaque ligne après l'entête
        rows_to_keep = []  # Liste pour stocker les lignes non traitées

        if len(rows) <= 1:  # Ensure there is at least one row after the header
            print("No data to process.")
            return
        
        new_rows = [rows[0]]  # Keep header row
        print(rows)
        # Process the first data row (ignoring the header)
        for ligne in rows:  
            location = ligne[0]  # Localisation
            phone = ligne[1]  # Numéro de téléphone
            situation = ligne[2]  # Description de la situation

            # Traiter la situation
            array = recuperer_info(situation)  # Analyze the emergency
            database.insert_info(location, phone, array[0], array[1], array[2], array[3])

            


        # Réécrire le fichier sans la ligne traitée
        with open("911.csv", mode='w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)  # Écrire toutes les lignes restantes
        print(liste_info)

    # Lancer le traitement des lignes du CSV
    traiter_csv()



if __name__ == "__main__":
    main()