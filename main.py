
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import httpx
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

app = FastAPI(title="Article Analysis API")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ArticleRequest(BaseModel):
    email: str
    article_url: str

# Get n8n webhook URL from environment variables
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")

@app.post("/submit-article")
async def submit_article(request: ArticleRequest):
    # Validate inputs
    if not request.email or not request.article_url:
        raise HTTPException(status_code=400, detail="Email and article URL are required")
    
    # Generate session ID
    session_id = str(uuid.uuid4())
    
    # Prepare data to send to n8n
    payload = {
        "email": request.email,
        "article_url": request.article_url,
        "session_id": session_id
    }
    
    # Forward to n8n webhook
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(N8N_WEBHOOK_URL, json=payload, timeout=30)
            response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error forwarding to n8n: {str(e)}")
    
    return {
        "message": "Article submitted for processing", 
        "session_id": session_id,
        "status": "success"
    }

@app.get("/")
async def root():
    return {"message": "Article Analysis API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
