from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the MongoDB URI from the .env file
uri = os.getenv("uri")
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
class database:
    def __init__(self):
        self.db = client["hackathon"]
        self.collection = self.db["helprequest"]
    
    def insertInfo(username,address,phone,priority,description,title,self):
        new_request = {
            "username":username,
            "address":address,
            "phone":phone,
            "priority":priority,
            "description":description,
            "title":title
        }
        insert_result = self.collection.insert_one(new_request)
    def selectInfo(self):
        all_documents = self.collection.find()
    


try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")

except Exception as e:
    print(e)