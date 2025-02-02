from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

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

class Database:
    def __init__(self):
        self.db = db
        self.collection = collection

    def insert_info(self, username, address, phone, priority, description, title):
        new_request = {
            "username": username,
            "address": address,
            "phone": phone,
            "priority": priority,
            "description": description,
            "title": title
        }
        self.collection.insert_one(new_request)

    def select_info(self):
        return list(self.collection.find({}, {"_id": 0}))  # Exclude _id

# Create an instance of Database
database = Database()

#  Flask Route to Get All Requests
@app.route("/requests", methods=["GET"])
def get_requests():
    documents = database.select_info()
    return jsonify(documents)

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")

except Exception as e:
    print(e)

# Run Flask server
if __name__ == "__main__":
    app.run(debug=True)
