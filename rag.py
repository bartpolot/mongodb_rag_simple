#!/usr/bin/env python3
import time
import os
import certifi


from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from termcolor import colored

import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession
from VertexEmbedding import EmbeddingPredictionClient


def get_mongodb_client() -> MongoClient:
    uri = os.getenv("MONGODB_URI")
    mongo_client = MongoClient(uri, tlsCAFile=certifi.where(), server_api=ServerApi('1'))
    try:
        mongo_client.admin.command('ping')
    except Exception as e:
        print(e)
        return None
    return mongo_client

def get_ctx(mongo_client: MongoClient, username: str, prompt: str) -> str:
    embedding = embeddings.get_embedding(text=prompt).text_embedding
    vector_query = {
        "$vectorSearch": {
            "index": "vector_index",
            "path": "embedding",
            "filter": {"username": username},
            "queryVector": embedding,
            "numCandidates": 100,
            "limit": 5
        }
    }
    documents = file_collection.aggregate([vector_query])
    ctx = "".join([f"{doc["ctx"]}\n" for doc in documents])
    return ctx

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
mongo_client = get_mongodb_client()
file_collection = mongo_client.get_database(os.getenv("MONGODB_DB_NAME")).get_collection("ctx")
embeddings = EmbeddingPredictionClient(project=project_id)
chat = model.start_chat()
###################### Boilerplate end ######################

username = input("Username: ")
# Get input from user in a loop until Ctrl+D is pressed
while True:
    try:
        prompt = input(colored(username + ": ", color="red", attrs=["bold"]))
        context = get_ctx(mongo_client, username, prompt)
        print(colored(f"  Context:\n{context}", "light_green"))
        chat_message = f"Context:\n{context}\nQuestion: {prompt}"
        response = show_chat_response(chat, chat_message)
    except EOFError:
        print("\nGoodbye!")
        break
