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
    
# space_id = get_space_id(json_object, "testtwo") 
# print(space_id)


def create_page_api(title, content):
    url = f"{CONFLUENCE_SITE}/wiki/api/v2/pages"
    headers = {
      "Accept": "application/json",
      "Content-Type": "application/json"
    }
    
    # spaces_in_confluence = read_from_json_file("spaces_in_confluence")
    # space_id = get_space_id(spaces_in_confluence, space_name)
    
    payload = json.dumps({
        "spaceId": 4423768,
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
        print(response)
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
    
    # save_to_json_file(results, "created_page")

    return json.dumps(results)

# create_page_api('Test7', 
#                      'To push code to a Git repository, you can follow these steps:\\n\\n1. Initialize a Git repository in the root directory of your project:\\n\\n<ac:structured-macro ac:name=\'code\'>\\n<ac:plain-text-body>\\n<![CDATA[\\n$ git init\\n]]>\\n</ac:plain-text-body>\\n</ac:structured-macro>\\n\\n2. Add the files you want to track to the staging area:\\n\\n<ac:structured-macro ac:name=\'code\'>\\n<ac:plain-text-body>\\n<![CDATA[\\n$ git add .\\n]]>\\n</ac:plain-text-body>\\n</ac:structured-macro>\\n\\n3. Commit the changes with a descriptive commit message:\\n\\n<ac:structured-macro ac:name=\'code\'>\\n<ac:plain-text-body>\\n<![CDATA[\\n$ git commit -m \'Initial commit\'\\n]]>\\n</ac:plain-text-body>\\n</ac:structured-macro>\\n\\n4. Create a remote repository on a Git hosting service such as GitHub or Bitbucket.\\n\\n5. Link the local repository to the remote repository:\\n\\n<ac:structured-macro ac:name=\'code\'>\\n<ac:plain-text-body>\\n<![CDATA[\\n$ git remote add origin <remote_repository_url>\\n]]>\\n</ac:plain-text-body>\\n</ac:structured-macro>\\n\\n6. Push the code to the remote repository:\\n\\n<ac:structured-macro ac:name=\'code\'>\\n<ac:plain-text-body>\\n<![CDATA[\\n$ git push -u origin master\\n]]>\\n</ac:plain-text-body>\\n</ac:structured-macro>\\n\\nThese are the basic steps to push code to a Git repository. Make sure to replace <remote_repository_url> with the actual URL of your remote repository."\n')

if __name__ == "__main__":
    create_page_api('Test1', 'To push code to a Git repository, you can follow these steps:\n\n1. Initialize a Git repository in the root directory of your project:\n\n<ac:structured-macro ac:name=\'code\'>\n\t<ac:plain-text-body>\n\t<![CDATA[\n$ git init\n]]>\n\t</ac:plain-text-body>\n\t</ac:structured-macro>\n\n2. Add the files you want to track to the staging area:\\n\\n<ac:structured-macro ac:name=\'code\'>\\n<ac:plain-text-body>\\n<![CDATA[\\n$ git add .\\n]]>\\n</ac:plain-text-body>\\n</ac:structured-macro>\\n\\n3. Commit the changes with a descriptive commit message:\\n\\n<ac:structured-macro ac:name=\'code\'>\\n<ac:plain-text-body>\\n<![CDATA[\\n$ git commit -m \'Initial commit\'\\n]]>\\n</ac:plain-text-body>\\n</ac:structured-macro>\\n\\n4. Create a remote repository on a Git hosting service such as GitHub or Bitbucket.\\n\\n5. Link the local repository to the remote repository:\\n\\n<ac:structured-macro ac:name=\'code\'>\\n<ac:plain-text-body>\\n<![CDATA[\\n$ git remote add origin <remote_repository_url>\\n]]>\\n</ac:plain-text-body>\\n</ac:structured-macro>\\n\\n6. Push the code to the remote repository:\\n\\n<ac:structured-macro ac:name=\'code\'>\\n<ac:plain-text-body>\\n<![CDATA[\\n$ git push -u origin master\\n]]>\\n</ac:plain-text-body>\\n</ac:structured-macro>\\n\\nThese are the basic steps to push code to a Git repository. Make sure to replace <remote_repository_url> with the actual URL of your remote repository."\n')
