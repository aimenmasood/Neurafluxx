import os
import json
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Initialize Google client for embeddings (new google-genai SDK)
_genai_client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
)

# Load pre-built vectorstore — numpy array + JSON documents
_base_dir = Path(__file__).resolve().parent.parent
_vectorstore_dir = _base_dir / "vectorstore"

_embeddings = np.load(str(_vectorstore_dir / "embeddings.npy"))   # shape: (N, 768)
with open(str(_vectorstore_dir / "documents.json"), encoding="utf-8") as f:
    _documents = json.load(f)

EMBED_MODEL = "models/gemini-embedding-001"


def _cosine_similarity(query_vec, doc_matrix):
    """Fast cosine similarity between query vector and all doc embeddings."""
    norms = np.linalg.norm(doc_matrix, axis=1) * np.linalg.norm(query_vec) + 1e-8
    return np.dot(doc_matrix, query_vec) / norms


def retrieve(query: str, top_k: int = 5) -> str:
    try:
        # Embed the query using Google API (new SDK)
        result = _genai_client.models.embed_content(
            model=EMBED_MODEL,
            contents=query
        )
        query_vec = np.array(result.embeddings[0].values, dtype=np.float32)

        # Cosine similarity search
        similarities = _cosine_similarity(query_vec, _embeddings)
        top_indices = np.argsort(similarities)[::-1][:top_k]
        top_docs = [_documents[i] for i in top_indices]

        context = '\n\n---\n\n'.join(top_docs)
        print(f"[DEBUG] Retrieved {len(top_docs)} chunks (top similarity: {similarities[top_indices[0]]:.3f})")
        return context

    except Exception as e:
        print(f"[RETRIEVER ERROR] {str(e)}")
        return ''