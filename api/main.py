import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn

from api.engine import generate_response

load_dotenv()

app = FastAPI(title="Neuraflux Chatbot API")

# Load allowed origins from environment variable, default to * for Railway
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"]
)

class ChatRequest(BaseModel):
    query: str

@app.get("/")
def health_check():
    return {"status": "ok", "message": "NeuraFlux Chatbot API is running."}

@app.post("/chat")
def chat(request: ChatRequest):
    response = generate_response(request.query)
    return {"response": response}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port)