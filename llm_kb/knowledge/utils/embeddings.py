import os
import numpy as np

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_openai_embeddings(texts, model="text-embedding-3-small"):
    import openai
    openai.api_key = OPENAI_API_KEY
    # texts: list of strings
    resp = openai.Embedding.create(input=texts, model=model)
    return [item["embedding"] for item in resp["data"]]

# fallback
def get_local_embeddings(texts, model_name="sentence-transformers/all-MiniLM-L6-v2"):
    from sentence_transformers import SentenceTransformer
    sb = SentenceTransformer(model_name)
    emb = sb.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return [e.tolist() for e in emb]
