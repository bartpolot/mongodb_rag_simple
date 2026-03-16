#!/usr/bin/env python3
import time
import os

from dotenv import load_dotenv

import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession

def show_chat_response(chat: ChatSession, prompt: str) -> str:
    text_response = []
    responses = chat.send_message(prompt, stream=True)
    print(f"Google: ", end="")
    for chunk in responses:
        text_response.append(chunk.text)
        print(chunk.text, end="")
    print("\n")
    return "".join(text_response)

###################### Boilerplate init ######################
load_dotenv(override=True)
project_id = os.getenv("GCP_PROJECT")
region_id = os.getenv("GCP_REGION")
model_name = os.getenv("MODEL_NAME", "gemini-2.5-flash")
vertexai.init(project=project_id, location=region_id)
model = GenerativeModel(model_name=model_name,
                        system_instruction=[os.getenv("VERTEX_SYSTEM_INSTRUCTION_1"),])
chat = model.start_chat()
###################### Boilerplate end ######################

# Get input from user in a loop until Ctrl+D is pressed
while True:
    try:
        prompt = input("You: ")
        response = show_chat_response(chat, prompt)
    except EOFError:
        print("\nGoodbye!")
        break
