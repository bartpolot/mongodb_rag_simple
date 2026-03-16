# RAG Demo using Vertex AI 

A small demo of **Retrieval-Augmented Generation (RAG)** using **Google Vertex AI** (Gemini) and **MongoDB** for vector search. Context documents are embedded with Vertex’s multimodal embedding model and stored in MongoDB; the RAG chat retrieves relevant context by user (**multitenant**) and uses it when answering.

Same principle can work with other providers like Voyage AI, AWS Bedrock, Claude or OpenAI. Adjust vector lenght accordingly.

## Files

| Main File | Description |
|------|-------------|
| **chatbot.py** | Simple LLM chat: interactive loop using a system instruction from env. No RAG. The LLM will have no user-related context. |
| **rag.py** | RAG chat: same as above but fetches context from MongoDB via vector search (by username + query embedding), then sends that context with each user message to the LLM. |

 Helper File | Description |
|------|-------------|
| **addctx.py** | Adds context to the DB: prompts for a username and text, embeds the text with Vertex, and inserts into the `extra_ctx` collection. |
| **genctx.py** | Generates sample context: uses Faker to create fake usernames and sentences, embeds them, and inserts into the `ctx` collection (for testing RAG). |
| **VertexEmbedding.py** | Google's wrapper around Vertex AI Prediction Service for embeddings: text, image, and video via `multimodalembedding@001`  |
| **index_definition.txt** | MongoDB Atlas vector index spec: 1408-dimension cosine index on `embedding` and a filter on `username`. |
| **requirements.txt** | Python dependencies (e.g. `google-cloud-aiplatform`, `pymongo`, `python-dotenv`, `termcolor`). |
| **prompts.txt** | Example prompts per user (e.g. for “bart”, “alice”) for trying the chat with and without RAG. |
| **sample_data.json** | Example context data per user (e.g. for “bart”, “alice”) for the RAG chat. |
| **.env.example** | Example environment variables; copy to `.env` and fill in your values. |

## Setup

1. Copy `.env.example` to `.env` and set your values:
   - `GCP_PROJECT` — your Google Cloud project ID
   - `GCP_REGION` — e.g. `europe-west1`
   - `MODEL_NAME` — Model name, like `gemini-2.5-flash`
   - `VERTEX_SYSTEM_INSTRUCTION_1` — system prompt for the chat, the default works ok but feel free to play with it
   - `MONGODB_URI` — MongoDB Atlas connection string
   - `MONGODB_DB_NAME` — database name (e.g. `users`)

2. Create the vector index in MongoDB Atlas using the schema in **index_definition.txt** (index name used in code: `vector_index`).

3. Install dependencies: `pip install -r requirements.txt`

4. Populate database. Run at least one of the following:

   a) Ready data: import the sample data `mongoimport --uri="mongodb+srv://YOURCLUSTER.mongodb.net/" --username=YOURUSER --db=YOURDB --collection=ctx sample_data.json`

   b) Custom data:  run `addctx.py` to add your own context for a few users. Include details to ask about later.

5. Optional: run `genctx.py` for fake context, to increase the size of the collection and the index

6. Run the RAG chat: `python rag.py` (or `python chatbot.py` for the plain chat). Ask the questions in **prompts.txt** (when using sample data) or your own.
