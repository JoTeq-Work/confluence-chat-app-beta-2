import os
import json
import requests
import speech_recognition as sr
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv, find_dotenv
from tenacity import retry, wait_random_exponential, stop_after_attempt


GPT_MODEL = "gpt-3.5-turbo-0613"

_ = load_dotenv(find_dotenv()) # read local .env
openai_key = os.environ["OPENAI_API_KEY"]


# Confluence REST API Utilities
CONFLUENCE_SITE = "https://joteqwork.atlassian.net"
API_TOKEN = "ATATT3xFfGF0V8Q_NZyy-pish4RnWjg8FylqTnxYMhDp2YWJn4Bbyh6S_w1R-7iFm2w8-uQCSs_8lzBot2EvT_bZ8JlYX7FxfLzHoM__BWLCx3z_RpEv9sK0vK22YzpA9zykgewsBRzluf9aI_57mfLRUQO58aEqgY62xXUG3NHvizxvDEaeJmA=4E7B8FF5"
AUTH = HTTPBasicAuth("joteqwork@gmail.com", API_TOKEN)


r = sr.Recognizer()
def speech_to_text():   
    """This function converts speech to text"""
    with sr.Microphone() as source:
        print("Say something")
        audio_input = r.listen(source)
    
    try:
        text_input = r.recognize_whisper(audio_input, language="english")
        print("Input:", text_input)
        return text_input
    except sr.UnknownValueError:
        return "Whisper could not understand audio"
    except sr.RequestError as e:
        return "Could not request results from Whisper"
    

def call_create_space_api(space_name):
    """
    This function calls the Confluence Create Space REST API
    """
    url = f"{CONFLUENCE_SITE}/wiki/rest/api/space"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
        }

    name_len = len(space_name)
    if name_len <= 3:
        space_key = space_name
    else:
        space_key = f"{space_name[0]}{space_name[-2:]}"

    payload = json.dumps({
        "key": space_key.lower(),
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
        print(f"Confluence Create Page API request failed with status code {response.status_code}")
        print(f"Response content: {response.content}")

    return response



def call_create_page_api(title, content, space_id):
    url = f"{CONFLUENCE_SITE}/wiki/api/v2/pages"
    headers = {
      "Accept": "application/json",
      "Content-Type": "application/json"
    }
    
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
        print(f"Confluence Create Page API request failed with status code {response.status_code}")
        print(f"Respnse content: {response.content}")

    return response


@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, functions=None, model=GPT_MODEL):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_key}",
    }
    json_data = {"model": model, "messages": messages}
    if functions is not None:
        json_data.update({"functions": functions})
        print("chat completion request, will try now")
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
        )
        print(response.json())
        return response
    except Exception as e:
        return f"Unable to generate ChatCompletion response. Exception: {e}"
    
class Conversation:
    def __init__(self):
        self.conversation_history = []

    def add_message(self, role, content):
        message = {"role": role, "content": content}
        self.conversation_history.append(message)
        
        
def chat_completion_with_function_execution(messages, functions=[None]):
    """This function makes a ChatCompletion API call with the option of adding functions"""
    print("Started process")
    response = chat_completion_request(messages, functions)
    print("First response", response.json()["choices"][0])
    full_message = response.json()["choices"][0]
    if full_message["finish_reason"] == "function_call":
        print("Calling function")
        return call_confluence_rest_api_function(messages, full_message)
    else:
        print("Function not called")
        return response.json()


class Space:
    def __init__(self):
        self.space = []
        
    def get_space_id(self):
        return self.space[0]
    
    def set_spade_id(self, space_id):
        self.space.clear()
        self.space.append(space_id)        
    
    
space = Space()
def call_confluence_rest_api_function(messages, full_message):
    """
    Function calling function which executes function calls when the model believes it is necessary.
    Currently extended by adding clauses to this if statement.
    """

    if full_message["message"]["function_call"]["name"] == "call_create_space_api":
        try:
            parsed_output = json.loads(
                full_message["message"]["function_call"]["arguments"]
            )
            print("call_confluence_rest_api_function parsed out:", parsed_output)
            results = call_create_space_api(parsed_output["space_name"])
            id = results.json()['id']
            print("id", id)
            
            
            space.set_spade_id(id)
            space_id = space.get_space_id()
            print("space id", space_id)           
            
        except Exception as e:
            return f"Unable to generate ChatCompletion response. Exception: {e}"
          
        messages.append(
            {
                "role": "function",
                "name": full_message["message"]["function_call"]["name"],
                "content": str(results),
            }
        )
        try:
            response = chat_completion_request(messages)
            return response.json()
        except Exception as e:
            print("space error")
            raise Exception("Function chat request failed")
    elif full_message["message"]["function_call"]["name"] == "call_create_page_api":    
        try:
            parsed_output = json.loads(
            full_message["message"]["function_call"]["arguments"]
            )
            print("parsed_output:", parsed_output)
            space_id = space.get_space_id()
            print(space_id)
            results = call_create_page_api(parsed_output["title"], parsed_output["content"], space_id)
        except Exception as e:
            print("page error")
            return f"Unable to generate ChatCompletion response. Exception: {e}"
            
        messages.append(
            {
                "role": "function",
                "name": full_message["message"]["function_call"]["name"],
                "content": str(results),
            }
        )
        try:
            response = chat_completion_request(messages)
            return response.json()
        except Exception as e:
            raise Exception("Function chat request failed")
    else:
        raise Exception("Function does not exist and cannot be called")



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