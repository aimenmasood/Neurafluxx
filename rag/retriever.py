import chromadb

# Initialize the client ONCE outside the function (Singleton Pattern)
# This prevents the "hanging" issue because the DB stays open and ready.
client = chromadb.PersistentClient(path='./chroma_db')
collection = client.get_collection('neuraflux_kb')

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