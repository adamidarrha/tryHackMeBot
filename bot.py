import json
import random
import time
from pymongo import MongoClient
import requests
from dotenv import load_dotenv
import os
import argparse
from colorama import init, Fore, Style
init(autoreset=True)


# Load .env file
load_dotenv()

FOLDER_NAME = "answers"

# Get the mongo_uri and db_name
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

#get authorization cookies and other ones from env file
_ga_z8d4wl3d4p = os.getenv('_GA_Z8D4WL3D4P')
_ga = os.getenv('_GA')
awsalb = os.getenv('AWSALB')
awsalbcors = os.getenv('AWSALBCORS')
_csrf = os.getenv('_CSRF')
connect_sid = os.getenv('CONNECT.SID')
intercom_device_id_pgpbhph6 = os.getenv('INTERCOM-DEVICE-ID-PGPBHPH6')
logged_in_hint = os.getenv('LOGGED-IN-HINT')
cookieconsent_status = os.getenv('COOKIECONSENT_STATUS')
intercom_session_pgpbhph6 = os.getenv('INTERCOM-SESSION-PGPBHPH6')

#get other headers for stealthiness
user_agent = os.getenv('USER-AGENT')
accept = os.getenv('ACCEPT')
accept_language = os.getenv('ACCEPT-LANGUAGE')
accept_encoding = os.getenv('ACCEPT-ENCODING')
csrf_token = os.getenv('CSRF-TOKEN')
x_requested_with = os.getenv('X-REQUESTED-WITH')
dnt = os.getenv('DNT')
referer = os.getenv('REFERER')
sec_fetch_dest = os.getenv('SEC-FETCH-DEST')
sec_fetch_mode = os.getenv('SEC-FETCH-MODE')
sec_fetch_site = os.getenv('SEC-FETCH-SITE')
sec_gpc = os.getenv('SEC-GPC')
if_none_match = os.getenv('IF-NONE-MATCH')
te = os.getenv('TE')

GET_PATHS_URL = "https://tryhackme.com/api/content/hacktivities"
GET_MODULES_URL = "https://tryhackme.com/paths/single/"
GET_ROOM_URL = "https://tryhackme.com/api/tasks/"

HEADERS = {"Cookie": f"_ga_Z8D4WL3D4P={_ga_z8d4wl3d4p}; _ga={_ga}; AWSALB={awsalb}; AWSALBCORS={awsalbcors}; _csrf={_csrf}; connect.sid={connect_sid}; intercom-device-id-pgpbhph6={intercom_device_id_pgpbhph6}; logged-in-hint={logged_in_hint}; cookieconsent_status={cookieconsent_status}; intercom-session-pgpbhph6={intercom_session_pgpbhph6}",
            "User-Agent": user_agent,
            "Accept": accept,
            "Accept-Language": accept_language,
            "Accept-Encoding": accept_encoding,
            "X-Requested-With": x_requested_with,
            "DNT": dnt,
            "Referer": referer,
            "Sec-Fetch-Dest": sec_fetch_dest,
            "Sec-Fetch-Mode": sec_fetch_mode,
            "Sec-Fetch-Site": sec_fetch_site,
            "Sec-GPC": sec_gpc,
            "If-None-Match": if_none_match,
            "Te": te
            }

min_delay_between_modules = 1
max_delay_between_modules = 5
min_delay_between_rooms = 1
max_delay_between_rooms = 5

class JSONRequester:
    def __init__(self, mongo_uri, db_name):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]

    def get_json_response(self, url, headers=None):
        """
        Makes an HTTP GET request to the specified URL with optional headers
        and returns the JSON response.

        :param url: URL to which the request is sent
        :param headers: Optional HTTP headers to send with the request
        :return: JSON response as a Python dictionary or an error message
        """
        headers = headers if headers else {}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Check for HTTP errors
            return response.json()  # Return the JSON response
        except requests.exceptions.HTTPError as errh:
            return {"error": "HTTP Error", "message": str(errh)}
        except requests.exceptions.ConnectionError as errc:
            return {"error": "Connection Error", "message": str(errc)}
        except requests.exceptions.Timeout as errt:
            return {"error": "Timeout Error", "message": str(errt)}
        except requests.exceptions.RequestException as err:
            return {"error": "Request Error", "message": str(err)}
        except ValueError:
            # This catches the case where the response is not valid JSON
            return {"error": "Invalid JSON in response"}

    def print_processing_message(level, message, is_success=True):
        symbols = ["✓", "→", "•"]
        indent = "    " * level
        color = Fore.GREEN if is_success else Fore.YELLOW
        symbol = symbols[min(level, len(symbols) - 1)]
        print(f"{color}{indent}{symbol} {message}")
    
    def print_delay_time(self, delay_seconds):
        if delay_seconds >= 3600:
            # Convert to hours if delay is 3600 seconds or more
            delay = delay_seconds / 3600
            unit = "hours"
            color = Fore.BLUE
        elif delay_seconds >= 60:
            # Convert to minutes if delay is 60 seconds or more
            delay = delay_seconds / 60
            unit = "minutes"
            color = Fore.GREEN
        else:
            # Keep in seconds for delays less than 60 seconds
            delay = delay_seconds
            unit = "seconds"
            color = Fore.RED

        print(f"{color}Total delay time: {delay:.2f} {unit}")

    def module_delay(self):
        #wait for 15 to 30 seconds before making another request
        time.sleep(random.uniform(min_delay_between_modules, max_delay_between_modules))

    def room_delay(self):
        # Wait for a random number of seconds between 15 and 30 before making another request
        time.sleep(random.uniform(min_delay_between_rooms, max_delay_between_rooms))

    def get_question_db(self, path_name, module_name, room_name, task_number, question_number):

        # Fetch the document
        doc = self.db.paths.find_one({
            "path name": path_name
        })

        if doc is not None:
            for module in doc.get("modules", []):
                if module.get("module name") == module_name:
                    for room in module.get("rooms", []):
                        if room.get("room name") == room_name:
                            for task in room.get("tasks", []):
                                if task.get("task number") == task_number:
                                    for question in task.get("questions", []):
                                        if question.get("question number") == question_number:
                                            return question
        else:
            print("No document found with the specified path name.")

    def process_paths(self, paths):
        if 'error' in paths:
            return paths

        all_path_names = []

        total_delay_time = 0

        for path in paths.get("paths", []):
            path_data = {
                "path name": path.get("title"),
                "number of modules": path.get("taskNo"),
                "number of rooms": path.get("rooms"),
                "hours to finish": path.get("hours"),
                "modules": []  # Initialize modules as empty list
            }

            # Update or insert path details in MongoDB
            self.db.paths.update_one(
                {"path name": path_data["path name"]},  # Filter
                {"$set": path_data},  # Update
                upsert=True  # Options
            )

            total_delay_time += path_data.get("number of modules") * max_delay_between_modules
            total_delay_time += path_data.get("number of rooms") * max_delay_between_rooms

            # Collect path names for further processing
            all_path_names.append(path_data["path name"])
        
        self.print_delay_time(total_delay_time)

        # Return a list of path names for further processing
        return all_path_names

    def process_modules_for_path(self,path_name, modules_response):
        if 'error' in modules_response:
            return modules_response
        
        self.print_processing_message(0, f"processing path: {path_name}")

        for module in modules_response.get("tasks", []):
            self.print_processing_message(1, f"    -Processing module: {module.get('title')}")
            
            module_data = {
                "module name": module.get("title"),
                "time": module.get("time"),
                #get room names and pass it to room details to get room information
                "rooms": [self.process_room_details(path_name, module.get("title"), room.get("code")) for room in module.get("rooms", [])]
            }            

            with open(os.path.join(FOLDER_NAME, f"{module_data.get('module name')}.json"), "w") as f:
                json.dump(module_data, f, indent=4)

            # Find the path document
            path_doc = self.db.paths.find_one({"path name": path_name})

            # Find the index of the module in the modules array
            module_index = next((index for (index, d) in enumerate(path_doc["modules"]) if d["module name"] == module_data["module name"]), None)

            if module_index is not None:
                # If the module exists, update it
                self.db.paths.update_one(
                    {"path name": path_name, "modules.module name": module_data["module name"]},
                    {"$set": {"modules.$": module_data}}
                )
            else:
                # If the module doesn't exist, append it to the modules array
                self.db.paths.update_one(
                    {"path name": path_name},
                    {"$push": {"modules": module_data}}
                )

    def process_room_details(self, path_name, module_name, room_name):
        
        self.print_processing_message(2, f"        - Processing room: {room_name}")

        room_response = self.get_json_response(GET_ROOM_URL + room_name, HEADERS)
        if 'error' in room_response:
            return room_response
        
        processed_room_data = self.process_response(path_name, module_name, room_name, room_response)

        #wait between room get calls
        self.room_delay()

        return processed_room_data

    def process_response(self, path_name, module_name, room_name, response):
        """
        Processes the JSON response to extract specific fields and organize data.

        :param response: JSON response as a Python dictionary
        :return: A dictionary containing the processed data
        """
        processed_data = {
            "room name": room_name,
            "totalTasks": response.get("totalTasks", 0),
            "tasks": []
        }

        for task in response.get("data", []):
            task_data = {
                "task name": task.get("taskTitle"),
                "task number": task.get("taskNo"),
                "questions": [],
                "numberOfQuestions": len(task.get("tasksInfo", []))
            }

            for question in task.get("tasksInfo", []):

                #check if this question is not answered
                if not question.get("correct", False):
                    #if it isn't then check the database if it exists
                    previous_question_data = self.get_question_db(path_name, module_name, room_name, task_data.get("task number"), question.get("questionNo"))
                    if previous_question_data is not None:
                        #if it exists then we just let the previous question data 
                        question_data = {
                            "question": previous_question_data.get("question"),
                            "question number": previous_question_data.get("question number"),
                            "is already answered": previous_question_data.get("is already answered"),
                            "submission": previous_question_data.get("submission", None),
                            "noAnswer": previous_question_data.get("noAnswer", False)
                        }
                        task_data["questions"].append(question_data)
                        continue
                
                #we add the new question_data if the previous one doesn't exist or if it's correct
                question_data = {
                    "question": question.get("question"),
                    "question number": question.get("questionNo"),
                    "is already answered": question.get("correct"),
                    "submission": question.get("submission", None),
                    "noAnswer": question.get("noAnswer", False)
                }
                task_data["questions"].append(question_data)

            processed_data["tasks"].append(task_data)

        return processed_data
    
    # def store_data(self, processed_data, path_name, module_name, room_name):
    #     """
    #     Stores the structured data in MongoDB with path, module, and room hierarchy.

    #     :param processed_data: Data processed from the JSON response
    #     :param path_name: The name of the path
    #     :param module_name: The name of the module
    #     :param room_name: The name of the room
    #     """
        
    #     path = self.db['paths'].find_one({"name": path_name})
    #     if not path:
    #         path = {"name": path_name, "modules": {}}
    #         self.db['paths'].insert_one(path)

    #     # Fetch or create the module within the path
    #     module = path['modules'].get(module_name, {"rooms": {}})
        
    #     # Fetch or create the room within the module
    #     room = module['rooms'].get(room_name, {"tasks": {}, "totalTasks": 0})

    #     room['totalTasks'] = processed_data['totalTasks']
    #     for task in processed_data['tasks']:
    #         task_number = str(task['task']['taskNo'])
    #         room['tasks'][task_number] = {
    #             "numberOfQuestions": task['numberOfQuestions'],
    #             "questions": {}
    #         }
    #         for question in task['questions']:
    #             q_num = str(question['question'])
    #             room['tasks'][task_number]['questions'][q_num] = {
    #                 "submission": question['submission'],
    #                 "noAnswer": question['noAnswer']
    #             }

    #     # Update the room within the module, and the module within the path
    #     self.db['paths'].update_one({"name": path_name}, {"$set": {"modules." + module_name + ".rooms." + room_name: room}})

    def main(self, user_path_name, module_name, room_name):
        paths = self.get_json_response(GET_PATHS_URL)
        all_path_names = self.process_paths(paths)

        for path_name in all_path_names:
            #in url the path names dont have spaces and are all lowercase
            url_path_name = path_name.lower().replace(" ", "")

            modules = self.get_json_response(GET_MODULES_URL + url_path_name, HEADERS)
            self.process_modules_for_path(path_name, modules)

            #delay between module get calls
            self.module_delay()

if __name__ == "__main__":

    # Create the parser
    parser = argparse.ArgumentParser(description='tryHackMe room solution getter just give it the path name and it will get all the questions and answers for you')

    # Add arguments
    parser.add_argument('-p', '--path_name', type=str, help='Name of the path (optional)', required=False)
    parser.add_argument('-m', '--module_name', type=str, help='Name of the module (optional)', required=False)
    parser.add_argument('-r', '--room_name', type=str, help='Name of the room (optional)', required=False)

    # Parse arguments
    args = parser.parse_args()

    # Use the arguments in your application
    path_name = args.path_name
    module_name = args.module_name
    room_name = args.room_name

    requester = JSONRequester(MONGO_URI, MONGO_DB_NAME)

    requester.main(path_name, module_name, room_name)