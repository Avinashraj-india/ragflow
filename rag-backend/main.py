from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from rag_engine import RAGEngine
from google.oauth2 import id_token
from google.auth.transport import requests
import jwt
import os

app = FastAPI()
rag = RAGEngine()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    query: str
    llm: str  # 'openai', 'gemini', 'ollama'

@app.post("/ask")
def ask_question(payload: Question):
    print(f"Received Query: {payload.query}, LLM: {payload.llm}")
    try:
        response = rag.query(payload.query, payload.llm)
        return {"response": response}
    except Exception as e:
        print("Error in /ask:", str(e))
        return {"error": str(e)}


@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    try:
        rag.add_document(file)
        return {"status": "uploaded and indexed"}
    except Exception as e:
        print("Error in /ask:", str(e))
        return {"error": str(e)}

class GoogleAuth(BaseModel):
    token: str

@app.post("/auth/google")
def google_auth(payload: GoogleAuth):
    try:
        # Verify Google token
        idinfo = id_token.verify_oauth2_token(
            payload.token, 
            requests.Request(), 
            "443599365399-ahk30e024d6v8rnut75r0m8vj700vetq.apps.googleusercontent.com"
        )
        
        # Create your app token
        user_data = {
            "google_id": idinfo['sub'],
            "email": idinfo['email'],
            "name": idinfo['name']
        }
        
        app_token = jwt.encode(user_data, "your-secret-key", algorithm="HS256")
        
        return {"token": app_token, "user": user_data}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")