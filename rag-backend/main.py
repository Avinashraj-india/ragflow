from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from rag_engine import RAGEngine
from google.oauth2 import id_token
from google.auth.transport import requests
import jwt
import os
from database import init_db, create_user, get_user_by_google_id, get_user_by_email, verify_password, store_otp, verify_otp, update_password
from dotenv import load_dotenv
import smtplib
import random
from email.mime.text import MIMEText

load_dotenv()

app = FastAPI()
rag = RAGEngine()
init_db()  # Initialize database

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://frontend:80"],
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

class EmailAuth(BaseModel):
    email: str
    password: str

class SignUpData(BaseModel):
    name: str
    email: str
    password: str
    team: str

class ForgotPassword(BaseModel):
    email: str

class VerifyOTP(BaseModel):
    email: str
    otp: str
    new_password: str

@app.post("/auth/google")
def google_auth(payload: GoogleAuth):
    try:
        idinfo = id_token.verify_oauth2_token(
            payload.token, 
            requests.Request(), 
            "443599365399-ahk30e024d6v8rnut75r0m8vj700vetq.apps.googleusercontent.com"
        )
        
        google_id = idinfo['sub']
        email = idinfo['email']
        name = idinfo['name']
        
        # Check if user exists
        user = get_user_by_google_id(google_id)
        if not user:
            # Create new user
            create_user(email, name, google_id=google_id)
        
        app_token = jwt.encode({"email": email, "name": name}, "your-secret-key", algorithm="HS256")
        return {"token": app_token, "user": {"email": email, "name": name}}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/auth/login")
def email_login(payload: EmailAuth):
    if verify_password(payload.email, payload.password):
        user = get_user_by_email(payload.email)
        app_token = jwt.encode({"email": user[1], "name": user[2], "team": user[5]}, "your-secret-key", algorithm="HS256")
        return {"token": app_token, "user": {"email": user[1], "name": user[2], "team": user[5]}}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/auth/signup")
def email_signup(payload: SignUpData):
    if get_user_by_email(payload.email):
        raise HTTPException(status_code=400, detail="User already exists")
    
    user_id = create_user(payload.email, payload.name, password=payload.password, team=payload.team)
    if user_id:
        app_token = jwt.encode({"email": payload.email, "name": payload.name, "team": payload.team}, "your-secret-key", algorithm="HS256")
        return {"token": app_token, "user": {"email": payload.email, "name": payload.name, "team": payload.team}}
    raise HTTPException(status_code=400, detail="Failed to create user")

@app.get("/teams")
def get_teams():
    teams_str = os.getenv("TEAMS", "Engineering,Marketing,Sales,HR,Finance")
    teams = [team.strip() for team in teams_str.split(",")]
    return {"teams": teams}

@app.post("/auth/forgot-password")
def forgot_password(payload: ForgotPassword):
    user = get_user_by_email(payload.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    otp = str(random.randint(100000, 999999))
    store_otp(payload.email, otp)
    
    # Send email
    try:
        msg = MIMEText(f"Your password reset OTP is: {otp}. Valid for 10 minutes.")
        msg['Subject'] = 'Password Reset OTP'
        msg['From'] = os.getenv('EMAIL_USER')
        msg['To'] = payload.email
        
        server = smtplib.SMTP(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT')))
        server.starttls()
        server.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASSWORD'))
        server.send_message(msg)
        server.quit()
        
        return {"message": "OTP sent to email"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to send email")

@app.post("/auth/reset-password")
def reset_password(payload: VerifyOTP):
    if verify_otp(payload.email, payload.otp):
        if update_password(payload.email, payload.new_password):
            return {"message": "Password updated successfully"}
        raise HTTPException(status_code=400, detail="Failed to update password")
    raise HTTPException(status_code=400, detail="Invalid or expired OTP")