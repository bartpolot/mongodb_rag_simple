# Vertex AI RAG Demo

A small demo of **Retrieval-Augmented Generation (RAG)** using **Google Vertex AI** (Gemini) and **MongoDB** for vector search. Context documents are embedded with Vertex’s multimodal embedding model and stored in MongoDB; the RAG chat retrieves relevant context by user and uses it when answering.

## Files

| File | Description |
|------|-------------|
| **chatbot.py** | Simple Vertex AI chat: interactive loop using Gemini and a system instruction from env. No RAG. |
| **rag.py** | RAG chat: same as above but fetches context from MongoDB via vector search (by username + query embedding), then sends that context with each user message to Gemini. |
| **addctx.py** | Adds context to the DB: prompts for a username and text, embeds the text with Vertex, and inserts into the `extra_ctx` collection. |
| **genctx.py** | Generates sample context: uses Faker to create fake usernames and sentences, embeds them, and inserts into the `ctx` collection (for testing RAG). |
| **VertexEmbedding.py** | Wrapper around Vertex AI Prediction Service for embeddings: text, image, and video via `multimodalembedding@001`. Used by the scripts above. |
| **index_definition.txt** | MongoDB Atlas vector index spec: 1408-dim cosine index on `embedding` and a filter on `username`. |
| **requirements.txt** | Python dependencies (e.g. `google-cloud-aiplatform`, `pymongo`, `python-dotenv`, `termcolor`). |
| **prompts.txt** | Example prompts per user (e.g. for “bart”, “alice”) for trying the RAG chat. |
| **.env.example** | Example environment variables; copy to `.env` and fill in your values. |

## Setup

1. Copy `.env.example` to `.env` and set your values:
   - `GCP_PROJECT` — your Google Cloud project ID
   - `GCP_REGION` — e.g. `europe-west1`
   - `MODEL_NAME` — optional, default `gemini-2.5-flash`
   - `VERTEX_SYSTEM_INSTRUCTION_1` — system prompt for the chat
   - `MONGODB_URI` — MongoDB Atlas connection string
   - `MONGODB_DB_NAME` — database name (e.g. `users`)

2. Create the vector index in MongoDB Atlas using the schema in **index_definition.txt** (index name used in code: `vector_index`).

3. Install dependencies: `pip install -r requirements.txt`

4. (Optional) Seed data: run `genctx.py` for fake context, or `addctx.py` to add your own.

5. Run the RAG chat: `python rag.py` (or `python chatbot.py` for the plain chat).
