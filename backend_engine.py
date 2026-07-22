import os
import json
import requests
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Retrieve DeepSeek/Gemini Key from Vercel Env
        api_key = os.environ.get("FORGEMIND_API_KEY")
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        payload = json.loads(post_data)
        user_query = payload.get("query", "")

        # Logic to "Route" between agents based on PRD Keywords
        agent_name = "Orion™ Orchestrator"
        system_prompt = "You are Orion, the ForgeMind AI orchestrator. Coordinate between Atlas (docs), Sentinel (maintenance), and Guardian (compliance)."

        if "fail" in user_query.lower() or "pump" in user_query.lower():
            agent_name = "Sentinel™ (Predictive Maint)"
        elif "comply" in user_query.lower() or "audit" in user_query.lower():
            agent_name = "Guardian™ (Compliance)"
        elif "who" in user_query.lower() or "where" in user_query.lower():
            agent_name = "PulseGraph™ (Knowledge Engine)"

        # Secure API Call (Example using DeepSeek/OpenAI standard)
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        api_payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"As {agent_name}, answer this: {user_query}"}
            ]
        }

        try:
            # Note: You can replace this URL with Gemini or DeepSeek as needed
            response = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=api_payload)
            response_json = response.json()
            ai_message = response_json['choices'][0]['message']['content']
        except:
            ai_message = "Agent synchronization error. Please check Enterprise API permissions."

        # Send Response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response_body = {
            "agent": agent_name,
            "message": ai_message,
            "confidence": 98
        }
        self.wfile.write(json.dumps(response_body).encode())
