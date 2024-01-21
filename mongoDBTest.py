from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Get the mongo_uri and db_name
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

# Create a MongoDB client
client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]  # Replace with your database name

# Define your query parameters
path_name = "Red Teaming"
module_name = "Red Team Fundamentals"
room_name = "redteamfundamentals"
task_number = 1  # Replace with your task number
question_number = 1  # Replace with your question number

# Fetch the document
doc = db.paths.find_one({
    "path name": path_name
})

if doc is not None:
    # Find the specific module, room, task, and question within the document
    for module in doc.get("modules", []):
        if module.get("module name") == module_name:
            for room in module.get("rooms", []):
                if room.get("room name") == room_name:
                    for task in room.get("tasks", []):
                        if task.get("task number") == task_number:
                            for question in task.get("questions", []):
                                if question.get("question number") == question_number:
                                    print(question)
else:
    print("No document found with the specified path name.")
