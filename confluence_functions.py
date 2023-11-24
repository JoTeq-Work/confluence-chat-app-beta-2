confluence_functions = [
    {
        "name": "call_create_space_api",
        "description": "Use this function to create a space in Confluence",
        "parameters": {
            "type": "object",
            "properties": {
                "space_name": {
                    "type": "string",
                    "description": "User response is the name of the new space being created.",
                }
            }
        },
        "required": ["space_name"]
    },
    {
        "name": "call_create_page_api",
        "description": "Use this function to create a page in a user's Confluence space",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                  "type": "string",
                  "description": "User response is the title of the page." ,
                },
                "content": {
                    "type": "string",
                    "description": "User response is the content of the page.",
                }
            }
        },
        "required": ["title", "content"]
    }
]