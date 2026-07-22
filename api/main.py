import os
import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.environ.get("GOOGLE_API_KEY")

@app.get("/api/main")
async def health():
    return {"status": "Backend is reachable", "key_configured": bool(API_KEY)}

@app.post("/api/main")
async def orchestrate(request: Request):
    try:
        body = await request.json()
        user_query = body.get("query", "No query provided")
        
        if not API_KEY:
            return {"agent": "System", "message": "ERROR: GOOGLE_API_KEY missing in Vercel Env."}

        # Logic
        agent = "Orion™ Orchestrator"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={API_KEY}"
        
        payload = {
            "contents": [{"parts": [{"text": user_query}]}]
        }

        response = requests.post(url, json=payload, timeout=10)
        data = response.json()

        if "candidates" in data:
            ai_msg = data['candidates'][0]['content']['parts'][0]['text']
            return {"agent": agent, "message": ai_msg}
        else:
            return {"agent": "System", "message": f"Gemini Error: {str(data)}"}

    except Exception as e:
        return {"agent": "System", "message": f"Backend Crash: {str(e)}"}
