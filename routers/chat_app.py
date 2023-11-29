import logging
from pathlib import Path
from typing import Annotated

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

confai_system_message = """
You are a friendly AI Confluence Liaison, a helpful assistant that helps users create spaces and pages. \
    Use the phrase "create space" as a trigger to ask the user for a space name to create a space. \
        Listen to the space name provided by the user and save it as `space_name`. \
        Always Say "TrackMatrix confirms: The new Confluence Space is now ready to use" after the space has been created. \

Ask the user to create a page for the space. \
    Use the phrase "create page" as a trigger to ask the user for the title of the page. \
    DO NOT assume the content of the page. Ask the user for content for the page. \
    Always Say "TrackMatrix confirms: The new Confluence Page is now ready to use" after the page has been created.
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
    logger.info("Chat response:", chat_response)
    assistant_message = chat_response["choices"][0]["message"]["content"]
    text_to_speech(assistant_message)
    speech_file_path = "../static/chat_app/files/ai_output.mp3"
    
    return templates.TemplateResponse(
        "chat.html", 
        {"request": request, "assistant_message": assistant_message, "speech_file_path": speech_file_path}
        )


# @router.post("/test")
# async def test_speech_to_text():
#     input = speech_to_text()
#     return input.strip()