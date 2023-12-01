import logging
from pathlib import Path
from typing import Annotated
from markupsafe import Markup

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from confluence_functions import confluence_functions
from dependencies import Conversation, chat_completion_with_function_execution, speech_to_text, text_to_speech

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

templates = Jinja2Templates(directory="templates")
# space_details = "https://joteqwork.atlassian.net/wiki/spaces/Data/overview"
confai_system_message = "\
    You are a friendly AI Confluence Liaison, a helpful assistant. \
    This is your job description:\
    - Create Space. \
    - Create Page. \
    - Generate HTML links. \
    Use the phrase 'create space' as a trigger to ask the user for a space name to create a space. \
    Always Say 'TrackMatrix confirms: The new Confluence Space is now ready to use' after the space has been created. \
    DO NOT REMOVE THE HTML ANCHOR TAGS. INCLUDE THE HTML ANCHOR TAGS IN THE OUTPUT\
    After creating the space, provide the confirmation message with the HTML anchor tag:\
    USE THE <a> {space_html_link} </a> \
    \
Ask the user to create a page for the space. \
    Use the phrase 'create page' as a trigger to ask the user for the title of the page and the content of the page. \
    DO NOT assume the content of the page. \
    Always Say 'TrackMatrix confirms: The new Confluence Page is now ready to use' after the page has been created. \
    DO NOT REMOVE THE HTML ANCHOR TAGS. INCLUDE THE HTML ANCHOR TAGS IN THE OUTPUT\
    After creating the page, provide the confirmation message with the HTML anchor tag:\
    USE THE <a> {page_html_link} </a>\
"

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
    logger.info("Chat response:", chat_response)
    assistant_message = chat_response["choices"][0]["message"]["content"]
    assistant_message_html = Markup(assistant_message)
    text_to_speech(assistant_message)
    speech_file_path = "../static/chat_app/files/ai_output.mp3"
    
    return templates.TemplateResponse(
        "chat.html", 
        {"request": request, "assistant_message": assistant_message_html, "speech_file_path": speech_file_path}
        )


# @router.post("/test")
# async def test_speech_to_text():
#     input = speech_to_text()
#     return input.strip()