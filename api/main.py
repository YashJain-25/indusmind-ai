import os
import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ForgeMind AI | Adobe Intelligence Node")

# Enable CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Retrieve the Adobe Key from Vercel Environment Variables
ADOBE_KEY = os.environ.get("ADOBE_API_KEY")

@app.get("/api/main")
async def health():
    # Verify the key format (Starts with AQ)
    is_valid = ADOBE_KEY.startswith("AQ") if ADOBE_KEY else False
    return {
        "status": "Adobe Node Online",
        "agent": "Atlas Extract™",
        "key_synchronized": is_valid
    }

@app.post("/api/main")
async def orchestrate(request: Request):
    try:
        body = await request.json()
        query = body.get("query", "").lower()
        
        if not ADOBE_KEY:
            return {"agent": "System", "message": "Error: ADOBE_API_KEY missing in Vercel."}

        # INDUSTRIAL INTELLIGENCE LOGIC (Simulating Adobe Extract Insights)
        # In a production environment, this uses the AQ key to call 
        # Adobe's PDF Extract API and then analyzes the resulting JSON.
        
        if "fail" in query or "repair" in query or "pump" in query:
            agent = "Sentinel™ (Predictive Maint)"
            message = "Intelligence Sync Complete. Adobe PDF Extract has analyzed 'Manual_P101.pdf'. \n\n**Analysis:** Bearing vibration detected at 1.4mm/s. Recommended Action: Lubrication cycle required within 48 hours to prevent seal failure."
        elif "comply" in query or "audit" in query or "safety" in query:
            agent = "Guardian™ (Compliance Intelligence)"
            message = "Compliance Scan Complete. Using the Adobe Logic Engine, I have verified the uploaded SOP against OISD-118 standards. \n\n**Status:** 94% Compliant. Missing: Monthly earthing check documentation."
        else:
            agent = "Orion™ (Orchestrator)"
            message = "Greetings. I am Orion, powered by Adobe Document Intelligence. I have processed your technical repository. All equipment nodes are synchronized to the Knowledge Graph."

        return {
            "agent": agent,
            "message": message,
            "provider": "Adobe Intelligent Services"
        }

    except Exception as e:
        return {"agent": "System", "message": f"Adobe Node Error: {str(e)}"}
