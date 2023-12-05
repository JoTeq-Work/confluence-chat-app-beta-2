import os
import json
import logging
import requests
from pathlib import Path
from openai import OpenAI
from pydub.playback import play
from utils import get_spaces_details, save_to_json_file, read_from_json_file, get_space_id
import speech_recognition as sr
from playsound import playsound
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv, find_dotenv
from tenacity import retry, wait_random_exponential, stop_after_attempt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GPT_MODEL = "gpt-3.5-turbo-0613"

_ = load_dotenv(find_dotenv()) # read local .env

# Declare API keys
openai_key = os.environ["OPENAI_API_KEY"]
ATLASSIAN_API_TOKEN = os.environ["ATLASSIAN_API_TOKEN"]


client = OpenAI(
    api_key=openai_key
)

# Confluence REST API Utilities
CONFLUENCE_SITE = "https://joteqwork.atlassian.net"
API_TOKEN = ATLASSIAN_API_TOKEN
AUTH = HTTPBasicAuth("joteqwork@gmail.com", API_TOKEN)


def speech_to_text():   
    r = sr.Recognizer() 
    with sr.Microphone() as source:
        logger.info("Say something...")
        audio = r.listen(source)
        
    try:
        text = r.recognize_whisper(audio, language="english")
        logger.info(f"Recognized speech: {text}")
        return text
    except sr.UnknownValueError:
        logger.warning("Speech recognition could not understand audio")
        return None
    except sr.RequestError as e:
        logger.error("Could not request results from speech recognition API: %s", e)
        return None
    

def text_to_speech(text):
    if not text:
        return
    
    speech_file_path = "static/chat_app/files/ai_output.mp3"
    # speech_file_path = Path("static/chat_app/files") / "ai_output.mp3"
    try:
        response = client.audio.speech.create(
        model="tts-1",
        voice="shimmer",
        input=text
        )
        response.stream_to_file(speech_file_path)
        # playsound(speech_file_path)
       
    except Exception as e:
        logger.error("Error generating speech: %s", e)


def call_create_space_api(space_name):
    """
    This function calls the Confluence Create Space REST API
    """
    url = f"{CONFLUENCE_SITE}/wiki/rest/api/space"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
        }

    # name_len = len(space_name)
    # if name_len <= 3:
    #     space_key = space_name
    # else:
    #     space_key = f"{space_name[0]}{space_name[-2:]}"
    
    # space_key = space_name

    payload = json.dumps({
        "key": space_name,
        "name": space_name,
        "description": {
            "plain": {
                "value": "A new space created",
                "representation": "plain"
            }
        },
        "metadata":{}
    })

    try:
        response = requests.request(
        "POST",
        url,
        data=payload,
        headers=headers,
        auth=AUTH
        )
    except Exception as e:
        logger.error("Error with calling Confluence Create Space API: %s", e)
        # print(f"Confluence Create Page API request failed with status code {response.status_code}")
        # print(f"Response content: {response.content}")
        
        
    results = {
            "space_id": response.json()["id"],
            "space_key": response.json()["key"],
            "space_name": response.json()["name"],
            "space_html_link": f'<a href="{response.json()["_links"]["base"] + response.json()["_links"]["webui"]}" target="_blank">{response.json()["name"]}<a/>'
            }        

    return json.dumps(results)


def call_get_spaces_api():
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
    
    spaces_in_confluence = get_spaces_details(spaces_res)
    
    save_to_json_file(spaces_in_confluence, "spaces_in_confluence")
        
    return json.dumps(spaces_in_confluence)


def call_create_page_api(space_name, title, content):
    url = f"{CONFLUENCE_SITE}/wiki/api/v2/pages"
    headers = {
      "Accept": "application/json",
      "Content-Type": "application/json"
    }
    
    spaces_in_confluence = read_from_json_file("spaces_in_confluence")
    space_id = get_space_id(spaces_in_confluence, space_name)
    
    payload = json.dumps({
        "spaceId": space_id,
        "status": "current",
        "title": title,
        "body": {
            "representation": "storage",
            "value": content
            }
        })
    
    try:
        response = requests.request(
        "POST",
        url,
        data=payload,
        headers=headers,
        auth=AUTH
        )  
    except Exception as e:
        logger.error("Error with calling Confluence Create Page API: %s", e)
        # print(f"Confluence Create Page API request failed with status code {response.status_code}")
        # print(f"Respnse content: {response.content}")
        
    results = {
        "page_id": response.json()["id"],
        "page_title": response.json()["title"],
        "page_html_link": f'<a href="{CONFLUENCE_SITE}/wiki{response.json()["_links"]["webui"]}" target="_blank">{response.json()["title"]}</a>',
        "space_id": response.json()['spaceId']
    }

    return json.dumps(results)

    

@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, functions=None, model=GPT_MODEL):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_key}",
    }
    json_data = {"model": model, "messages": messages}
    if functions is not None:
        json_data.update({"functions": functions})
        logger.info("chat completion request, will try now")
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
        )
        logger.info(response.json())
        return response
    except Exception as e:
        logger.error("Unable to generate ChatCompletion response. Exception: %s", e)
    
class Conversation:
    def __init__(self):
        self.conversation_history = []

    def add_message(self, role, content):
        message = {"role": role, "content": content}
        self.conversation_history.append(message)
        
        
def chat_completion_with_function_execution(messages, functions=[None]):
    """This function makes a ChatCompletion API call with the option of adding functions"""
    logger.info("Started process")
    response = chat_completion_request(messages, functions)
    logger.info("First response", response.json()["choices"][0])
    full_message = response.json()["choices"][0]
    if full_message["finish_reason"] == "function_call":
        logger.info("Calling function")
        return call_confluence_rest_api_function(messages, full_message)
    else:
        logger.warning("Function not called")
        return response.json()


class Space:
    def __init__(self):
        self.space = []
        
    def get_space_id(self):
        return self.space[0]
    
    def set_space_id(self, space_id):
        self.space.clear()
        self.space.append(space_id)     
    
    
space = Space()
def call_confluence_rest_api_function(messages, full_message):
    """
    Function calling function which executes function calls when the model believes it is necessary.
    Currently extended by adding clauses to this if statement.
    """
    global space

    if full_message["message"]["function_call"]["name"] == "call_create_space_api":
        try:
            parsed_output = json.loads(
                full_message["message"]["function_call"]["arguments"]
            )
            print(parsed_output)
            logger.info("call_confluence_rest_api_function parsed out:", parsed_output)
            space_results = call_create_space_api(parsed_output["space_name"])
            print(space_results)
            # logger.info("Create space results:", results)
            # print("Create space json info:", results.json())
            id = space_results['space_id']
            logger.info("id", id)
            space.set_space_id(id)
            space_id = space.get_space_id()
            # logger.info("space id", space_id)   
            # res = {
            #     "space_id": results.json()['id'],
            #     "space_key": results.json()['key'],
            #     "space_name": results.json()['name'],
            #     "space_link": f"{CONFLUENCE_SITE}/wiki/spaces/{results.json()['key']}"
            # }        
            # print(res["space_link"], f"{results.json()['_links']['base']}{results.json()['_links']['webui']}")
            
        except Exception as e:
            logger.error("Space error. Unable to generate ChatCompletion response: %s", e)
            # return f"Unable to generate ChatCompletion response. Exception: {e}"
          
        messages.append(
            {
                "role": "function",
                "name": full_message["message"]["function_call"]["name"],
                "content": space_results,
            }
        )
        try:
            response = chat_completion_request(messages)
            return response.json()
        except Exception as e:
            logger.error("Function chat request failed: %s", e)
            # raise Exception("Function chat request failed")
            
    elif full_message["message"]["function_call"]["name"] == "call_get_spaces_api":
        try:
            spaces_in_confluence = call_get_spaces_api()
            logger.info("Spaces in Confleunce", spaces_in_confluence) 
        except Exception as e:
            logger.error(
                "Getting Spaces Error!\n",
                "Function: call_confluence_rest_api_function\n",
                "Unable to generate ChatCompletion response: %s", e
                )
        
        messages.append(
            {
                "role": "function",
                "name": full_message["message"]["function_call"]["name"],
                "content": spaces_in_confluence,
            }
        )        
        try:
            response = chat_completion_request(messages)
            return response.json()
        except Exception as e:
            logger.error(
                "Getting Spaces Error!\n",
                "Function: call_confluence_rest_api_function\n",
                "Function chat request failed: %s", e
                )
            
    elif full_message["message"]["function_call"]["name"] == "call_create_page_api":    
        try:
            parsed_output = json.loads(
            full_message["message"]["function_call"]["arguments"]
            )
            # logger.info("parsed_output:", parsed_output)
            # space_id = space.get_space_id()
            
            # logger.info(space_id)
            
            page_results = call_create_page_api(parsed_output["space_name"], parsed_output["title"], parsed_output["content"])
            print("Page Results", page_results)
            page_id = page_results['page_id']
            print("Page id", page_id)
        except Exception as e:
            logger.error("Page error. Unable to generate ChatCompletion response: %s", e)
            # print("page error")
            # return f"Unable to generate ChatCompletion response. Exception: {e}"
            
        messages.append(
            {
                "role": "function",
                "name": full_message["message"]["function_call"]["name"],
                "content": page_results,
            }
        )
        try:
            response = chat_completion_request(messages)
            return response.json()
        except Exception as e:
            logger.error("Function chat request failed: %s", e)
            # raise Exception("Function chat request failed")
            
    else:
        logger.warning("Function does not exist and cannot be called: %s", e)
        # raise Exception("Function does not exist and cannot be called")



def main():
    # Start with a system message
    confai_system_message = """
    You are a friendly AI Confluence Liaison, a helpful assistant that communicates with Confluence Rest API.\
    You create spaces and pages in Confluence for users via the Confluence Rest API. \
    When a user request to create a space, you are to ask the user for a space name \
    Always thank the user after they have provided the space name. \
    After space has been successfully created, ask the user if they would like to create a page in the space. \
    If the user says yes or request to create a page, ask the user to provide content for the page for the page to be created.
    """
    confai_conversation = Conversation()
    confai_conversation.add_message("system", confai_system_message)
    
    # while True:
    #     user_input = input("User: ")
    #     confai_conversation.add_message("user", user_input)
    #     chat_response = chat_completion_with_function_execution(
    #         confai_conversation.conversation_history, functions=confluence_functions
    #     )
    #     assistant_message = chat_response["choices"][0]["message"]["content"]
    #     print("Assistant: ", assistant_message)
    
    
if __name__ == "__main__":
    main()
