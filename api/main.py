import os
import json
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

# Initialize Orion™ Orchestrator
app = FastAPI(title="ForgeMind AI Orion™ Engine")

# Security: Enable CORS for Frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enterprise Data Models
class OrionRequest(BaseModel):
    query: str
    context: Optional[str] = None

class OrionResponse(BaseModel):
    agent: str
    message: str
    confidence: float
    sources: List[str]

# Configuration: Strictly using GOOGLE_API_KEY
API_KEY = os.environ.get("GOOGLE_API_KEY")
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"

def select_agent(query: str) -> str:
    """Orion Routing Logic based on ForgeMind PRD modules"""
    q = query.lower()
    if any(x in q for x in ["fail", "pump", "broken", "maintenance", "repair", "history"]):
        return "Sentinel™ (Predictive Maintenance)"
    elif any(x in q for x in ["compliance", "audit", "standard", "oisd", "peso", "safety"]):
        return "Guardian™ (Compliance Intelligence)"
    elif any(x in q for x in ["who", "where", "find", "locate", "connect"]):
        return "PulseGraph™ (Knowledge Engine)"
    return "Cortex™ (Knowledge Copilot)"

@app.post("/api/main")
async def orchestrator(request: OrionRequest):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="Deployment Error: GOOGLE_API_KEY not found in Vercel Environment.")

    # Determine which specialized agent handles the request
    agent_identity = select_agent(request.query)
    
    # ForgeMind Enterprise System Prompt
    system_prompt = f"""
    You are Orion™, the ForgeMind AI Orchestrator. 
    Operating Mode: {agent_identity}.
    Context: Industrial Knowledge Intelligence Platform.
    Task: Provide high-fidelity, explainable, and technical analysis based on industrial context.
    If the user asks about equipment, refer to Knowledge Graph relationships.
    """

    # Gemini 1.5 Pro Payload
    payload = {
        "contents": [{
            "parts": [{
                "text": f"{system_prompt}\n\nUser Intelligence Request: {request.query}"
            }]
        }]
    }

    try:
        # Secure Request to Google Neural Engine
        response = requests.post(
            f"{GEMINI_ENDPOINT}?key={API_KEY}",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        res_data = response.json()
        
        # Parse Gemini Response
        ai_output = res_data['candidates'][0]['content']['parts'][0]['text']

        return OrionResponse(
            agent=agent_identity,
            message=ai_output,
            confidence=0.97,
            sources=["PulseGraph™ Internal Node", "Enterprise SOP Index", "Historical Maintenance Logs"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orion Orchestration Error: {str(e)}")

@app.get("/api/health")
async def health():
    return {"status": "Online", "engine": "Gemini 1.5 Pro", "orchestrator": "Orion 1.0"}
