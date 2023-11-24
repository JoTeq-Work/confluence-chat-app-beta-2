from typing import Annotated

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from confluence_functions import confluence_functions
from dependencies import Conversation, chat_completion_with_function_execution, speech_to_text

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

templates = Jinja2Templates(directory="templates")

# confai_system_message = """
#     You are a friendly AI Confluence Liaison, a helpful assistant that communicates with Confluence Rest API.\
#     When a user request to create a space, you are to ask the user for a space name \
#     Always thank the user after they have provided the space name. \
#     Move on to the next step and ask the user if they would like to create a page in the space. \
#     If the user says yes or request to create a page, ask the user to provide content for the page for the page to be created. \
#     Thank the user for providing content for the page.
#     """
confai_system_message = """
You are a friendly AI Confluence Liaison, a helpful assistant that helps users create spaces and pages. \
    Use the phrase "create space" as a trigger to ask the user for a space name to create a space. \
        Listen to the space name provided by the user and save it as `space_name`. \
    Always thank the user after they have provided the space name. \

Ask the user to create a page for the space. \
    Use the phrase "create page" as a trigger to ask the user for the title of the page.\
    DO NOT assume the content of the page. Ask the user for content for the page.
"""
confai_conversation = Conversation()
confai_conversation.add_message("system", confai_system_message)


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@router.post("/", response_class=HTMLResponse)
async def confluence_chat(request: Request):
    input = speech_to_text()
    confai_conversation.add_message("user", input.strip())
    chat_response = chat_completion_with_function_execution(
        confai_conversation.conversation_history, functions=confluence_functions
    )
    print("Chat response:", chat_response)
    assistant_message = chat_response["choices"][0]["message"]["content"]
    
    return templates.TemplateResponse("chat.html", {"request": request, "assistant_message": assistant_message})


# @router.post("/test")
# async def test_speech_to_text():
#     input = speech_to_text()
#     return input.strip()