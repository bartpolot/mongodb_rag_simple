
#!/usr/bin/env python3
import time
import os
import faker
import random

from dotenv import load_dotenv

from VertexEmbedding import EmbeddingPredictionClient
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


def get_mongodb_client() -> MongoClient:
    # Create a new client and connect to the server
    mongo_client = MongoClient(os.getenv("MONGODB_URI"), server_api=ServerApi('1'))
    try:
        print("Connecting to MongoDB Atlas...")
        start = time.time()
        mongo_client.admin.command('ping')
        end = time.time()
        print(f"Connected to MongoDB in {end - start:.2f}s")
    except Exception as e:
        print(e)
        return None
    return mongo_client

load_dotenv()
project_id = os.getenv("GCP_PROJECT")
embeddings = EmbeddingPredictionClient(project=project_id)
mongo_client = get_mongodb_client()
ctx_collection = mongo_client.get_database(os.getenv("MONGODB_DB_NAME")).get_collection("ctx")

faker = faker.Faker()
c = 0
while True:
    user = faker.word()
    for _ in range(random.randint(1, 8)):
        try:
            ctx = faker.sentence()
            doc = {}
            doc["username"] = user
            doc["ctx"] = ctx
            doc["embedding"] = embeddings.get_embedding(text=ctx).text_embedding
            ctx_collection.insert_one(doc)
            c = c + 1
        except KeyboardInterrupt:
            print("\nGoodbye!")
            exit(0)
    print(f"Inserted {c} documents for {user}")
