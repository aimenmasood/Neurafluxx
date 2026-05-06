import os
import chromadb
from pathlib import Path

# Use env var or resolve absolute path relative to this file to avoid
# Railway working-directory issues with relative paths like './chroma_db'
_base_dir = Path(__file__).resolve().parent.parent
_chroma_path = os.getenv("CHROMA_PERSIST_DIR", str(_base_dir / "chroma_db"))
_collection_name = os.getenv("CHROMA_COLLECTION_NAME", "neuraflux_kb")

# Initialize the client ONCE outside the function (Singleton Pattern)
# This prevents the "hanging" issue because the DB stays open and ready.
client = chromadb.PersistentClient(path=_chroma_path)
collection = client.get_collection(_collection_name)

def retrieve(query):
    try:
        # n_results is your 'k'. 5 is perfect for your document size.
        results = collection.query(
            query_texts=[query], 
            n_results=5
        )
        
        if results['documents'] and len(results['documents'][0]) > 0:
            # We join the top 5 most relevant chunks
            documents = results['documents'][0]
            context = '\n\n---\n\n'.join(documents)
            
            print(f"[DEBUG] Successfully retrieved {len(documents)} chunks.")
            return context
            
        return ''
    except Exception as e:
        print(f"[RETRIEVER ERROR] {str(e)}")
        return ''