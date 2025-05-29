from fastapi import FastAPI, Query
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
import pickle

app = FastAPI()

model = SentenceTransformer('all-MiniLM-L6-v2')


INDEX_PATH = "vectorstore/news_index.faiss"
DOCS_PATH = "vectorstore/docs.pkl"


if os.path.exists(INDEX_PATH) and os.path.exists(DOCS_PATH):
    index = faiss.read_index(INDEX_PATH)
    with open(DOCS_PATH, "rb") as f:
        documents = pickle.load(f)
else:
    index = faiss.IndexFlatL2(384)  
    documents = []

@app.get("/ping")
def ping():
    return {"message": "Retriever Agent is ready"}

@app.post("/index/")
def add_documents(docs: list[str]):
    global documents, index
    embeddings = model.encode(docs)
    index.add(np.array(embeddings))
    documents.extend(docs)

    
    faiss.write_index(index, INDEX_PATH)
    with open(DOCS_PATH, "wb") as f:
        pickle.dump(documents, f)

    return {"message": f"{len(docs)} documents indexed."}

@app.get("/retrieve/")
def retrieve_documents(query: str = Query(..., description="User query like 'TSMC earnings'"), top_k: int = 3):
    global documents, index
    if len(documents) == 0:
        return {"error": "No documents indexed yet."}

    q_embedding = model.encode([query])
    distances, indices = index.search(np.array(q_embedding), top_k)
    
    results = [documents[i] for i in indices[0]]
    return {
        "query": query,
        "top_k": top_k,
        "results": results
    }
