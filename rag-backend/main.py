from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from rag_engine import RAGEngine

app = FastAPI()
rag = RAGEngine()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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