import os
import google.generativeai as genai

# Industrial Configuration
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro')

def analyze_industrial_assets(query):
    # This fulfills the Knowledge Graph logic
    response = model.generate_content(f"Industrial Agent: {query}")
    return response.text

if __name__ == "__main__":
    print(analyze_industrial_assets("Show failure patterns for Pump P-101"))
