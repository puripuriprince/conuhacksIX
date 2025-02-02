from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
import Database
from bson import ObjectId 
import subprocess
import threading

# Noms des fichiers Python à exécuter
file1 = "aiDispatcher.py"
import schedule
import time
import os


# def run_script():
#     print("Exécution du script d'analyse des urgences...")
#     os.system("python aiDispatcher.py")  # Exécuter script.py

# # Planifier l'exécution toutes les 20 secondes
# schedule.every(20).seconds.do(run_script())

# def appel_script():
#     subprocess.run(["python","-Xfrozen_modules=off", file1])  # Exécute le premier script
#     threading.Timer(10, appel_script()).start()

#run_script()

# Load environment variables
load_dotenv()

# MongoDB connection
uri = os.getenv("uri")
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["hackathon"]
collection = db["helprequest"]

# Flask setup
app = Flask(__name__)
CORS(app)

def insert_info(address, phone, priority, description,title,category):
    new_request = {
        #"username": username,
        "address": address,
        "phone": phone,
        "priority": priority,
        "description": description,
        "title": title,
        "category": category
    }
    collection.insert_one(new_request)

def select_info():
    documents = list(collection.find({}))
    
    # Convert _id to string and priority to int
    for doc in documents:
        doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
        
        # Ensure priority is an integer (if it's stored as a string)
        if "priority" in doc:
            try:
                doc["priority"] = int(doc["priority"])  # Convert string to int
            except ValueError:
                doc["priority"] = 1  # Default high value if conversion fails
    
    # Now sort by priority (ascending order)
    documents.sort(key=lambda x: x["priority"])  
    
    return documents

# Create an instance of Database
database = Database

#  Flask Route to Get All Requests
@app.route("/requests", methods=["GET"])
def get_requests():
    documents = database.select_info()
    return jsonify(documents)


# DELETE request to remove an item by _id
@app.route("/requests/<string:item_id>", methods=["DELETE"])
def delete_request(item_id):
    try:
        result = collection.delete_one({"_id": ObjectId(item_id)})
        if result.deleted_count > 0:
            return jsonify({"message": "Item deleted successfully"}), 200
        else:
            return jsonify({"error": "Item not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")

except Exception as e:
    print(e)

# Run Flask server
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False,port=8000)
