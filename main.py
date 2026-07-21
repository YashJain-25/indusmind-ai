import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
from pydantic import BaseModel

# 1. INITIALIZATION & SECURITY
# The API key is NOT hardcoded. It will be read from Vercel/System Env.
GEMINI_KEY = os.getenv("GOOGLE_API_KEY")
if not GEMINI_KEY:
    # Fallback for local testing if env is not set
    GEMINI_KEY = "REPLACE_WITH_YOUR_KEY_FOR_LOCAL_ONLY"

app = FastAPI(title="IndusMind AI Backend")

# Enable CORS for Vercel Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini 1.5 Pro
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    google_api_key=GEMINI_KEY,
    temperature=0.1
)

# 2. DEFINE THE AI AGENT STATE
class AgentState(TypedDict):
    query: str
    context: str
    history_data: str
    final_answer: str

# 3. DEFINE THE INTELLIGENCE NODES
def router(state: AgentState):
    """Decides if the query needs Knowledge Graph (History) or Vector RAG (Manuals)"""
    prompt = f"Analyze query: '{state['query']}'. Reply 'KG' for asset history/tags or 'DOC' for SOP/Manuals."
    decision = llm.invoke(prompt).content
    return "kg_node" if "KG" in decision else "doc_node"

def kg_node(state: AgentState):
    """Simulates Knowledge Graph retrieval for Equipment Tags & Failure History"""
    # In a full build, this would query Neo4j
    state['history_data'] = "KG DATA: Asset P-101 has 3 failure records: Seal Leak (2023), Bearing Wear (2024)."
    return state

def doc_node(state: AgentState):
    """Simulates Vector RAG retrieval from Technical Manuals & SOPs"""
    # In a full build, this would query Qdrant
    state['context'] = "DOC DATA: OEM Manual specifies seal replacement every 4000 operating hours."
    return state

def analyzer(state: AgentState):
    """Synthesizes the final Industrial Intelligence response"""
    combined_info = f"{state['history_data']} | {state['context']}"
    prompt = f"System: Industrial Expert. Query: {state['query']}. Data: {combined_info}. Provide RCA and Recommendation."
    state['final_answer'] = llm.invoke(prompt).content
    return state

# 4. BUILD THE LANGGRAPH WORKFLOW
workflow = StateGraph(AgentState)
workflow.add_node("kg_node", kg_node)
workflow.add_node("doc_node", doc_node)
workflow.add_node("analyzer", analyzer)

workflow.set_conditional_entry_point(router, {
    "kg_node": "kg_node", 
    "doc_node": "doc_node"
})
workflow.add_edge("kg_node", "analyzer")
workflow.add_edge("doc_node", "analyzer")
workflow.add_edge("analyzer", END)

agent_engine = workflow.compile()

# 5. API ENDPOINTS
class ChatQuery(BaseModel):
    query: str

@app.post("/chat")
async def chat_endpoint(request: ChatQuery):
    try:
        result = agent_engine.invoke({"query": request.query, "context": "", "history_data": ""})
        return {"response": result['final_answer']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ocr_ingest")
async def ocr_endpoint(file: UploadFile = File(...)):
    """Handles Universal Document Intelligence (OCR for PDF/Images)"""
    genai.configure(api_key=GEMINI_KEY)
    vision_model = genai.GenerativeModel('gemini-1.5-flash')
    
    content = await file.read()
    # Industrial Vision Prompt
    prompt = "Extract all Equipment Tags, Maintenance Logs, and Technical Specs from this document into a table."
    
    response = vision_model.generate_content([
        prompt, 
        {'mime_type': file.content_type, 'data': content}
    ])
    
    return {"extracted_data": response.text}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
