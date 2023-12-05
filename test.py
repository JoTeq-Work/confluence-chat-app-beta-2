import json
import logging
import requests
import speech_recognition as sr
from dependencies import space, CONFLUENCE_SITE, API_TOKEN, AUTH

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

r = sr.Recognizer()
def speech_to_text():   
    with sr.Microphone() as source:
        print("Say something")
        audio_input = r.listen(source)
    
    try:
        text_input = r.recognize_whisper(audio_input, language="english")
        return text_input
    except sr.UnknownValueError:
        return "Whisper could not understand audio"
    except sr.RequestError as e:
        return "Could not request results from Whisper"
    
# input = speech_to_text()
# print(input)
# print(space.get_space_id())

def get_spaces_api():
    url = f"{CONFLUENCE_SITE}/wiki/api/v2/spaces"
    headers = {
        "Accept": "application/json"
    }
    
    try:
        response = requests.request(
            "GET",
            url,
            headers=headers,
            auth=AUTH
        )
    except Exception as e:
        logger.error("Error with calling Confluence Create Space API: %s", e)
        
    spaces_res = response.json()['results']
    
    spaces_det = get_spaces_details(spaces_res)
        
    return spaces_det


def get_spaces_details(spaces_results):    
    spaces = []
    spaces_in_conf = []
    
    for space_result in spaces_results:    
        space_name = space_result['name']
        space_id = space_result['id']
        spaces.append(space_name)
        space_details = {
            "space_id": space_id,
            "space_name": space_name,
        }
        
        spaces_in_conf.append(space_details)
    spaces_in_conf.append({"spaces": spaces})
    return spaces_in_conf
    
# print(spaces)
# print(spaces_in_conf)
# spaces = get_spaces_api()
# spaces_results = spaces['results']
# print(get_spaces(spaces_results))
# spaces = get_spaces_api()

# with open("spaces_in_confluence.json", "w") as outfile:
#     json.dump(spaces, outfile)
    
with open('spaces_in_confluence.json', 'r') as openfile:
    
    # Reading from json file
    json_object = json.load(openfile)

def get_space_id(json_object: dict, requested_space: str):
    space_id = None
    for res in json_object[:-1]:
        if res['space_name'] == requested_space:
            space_id = res['space_id']
            return space_id
    
space_id = get_space_id(json_object, "testtwo") 
print(space_id)