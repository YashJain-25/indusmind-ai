import os
import requests
import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Read DeepSeek Key from Vercel
API_KEY = os.environ.get("DEEPSEEK_API_KEY")

@app.get("/api/main")
async def health():
    return {
        "status": "Orion Online", 
        "engine": "DeepSeek-V3",
        "key_present": bool(API_KEY)
    }

@app.post("/api/main")
async def orchestrate(request: Request):
    try:
        body = await request.json()
        user_query = body.get("query", "")

        if not API_KEY:
            return {"agent": "System", "message": "Critical: DEEPSEEK_API_KEY missing in Vercel Env."}

        # DeepSeek API Endpoint (OpenAI Compatible)
        url = "https://api.deepseek.com/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }

        # Orion Orchestration Logic
        q = user_query.lower()
        agent = "Cortex™ (Copilot)"
        if any(x in q for x in ["fail", "repair", "history"]):
            agent = "Sentinel™ (Predictive Maint)"
        elif any(x in q for x in ["audit", "comply", "safety", "oisd"]):
            agent = "Guardian™ (Compliance Intelligence)"

        # DeepSeek Payload
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": f"You are Orion, ForgeMind AI. Operating Agent: {agent}. Provide high-density industrial technical analysis."},
                {"role": "user", "content": user_query}
            ],
            "stream": False
        }

        # Call DeepSeek API
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        data = response.json()

        if "error" in data:
            return {"agent": "System", "message": f"DeepSeek Error: {data['error']['message']}"}

        ai_msg = data['choices'][0]['message']['content']
        return {"agent": agent, "message": ai_msg}

    except Exception as e:
        return {"agent": "System", "message": f"Backend Exception: {str(e)}"}
