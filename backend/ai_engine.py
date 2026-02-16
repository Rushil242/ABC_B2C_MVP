import os
import json
import logging
import google.generativeai as genai
from typing import Dict, Any, List

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from dotenv import load_dotenv
load_dotenv()

# --- CONFIGURATION ---
MODEL_NAME = "gemini-1.5-flash" 

class AIEngine:
    def __init__(self):
        # Ensure GEMINI_API_KEY is set in your environment variables (.env)
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not found. AI features will be disabled.")
            self.model = None
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(MODEL_NAME)

    def generate_risk_explanation(self, risk_data: dict, user_profile: dict = None) -> str:
        """
        Uses Gemini to write a personalized explanation based on user profile.
        """
        if not self.model:
            return f"{risk_data['description']} (AI Explanation Unavailable)"

        try:
            # Extract Context from Profile
            profile_context = "Standard Client"
            if user_profile:
                risk_appetite = user_profile.get('risk', 'Balanced')
                horizon = user_profile.get('horizon', 'Medium-Term')
                profile_context = f"Risk Appetite: {risk_appetite}, Planning Horizon: {horizon}"

            prompt = f"""
            Role: Expert Tax Consultant.
            Task: Write a 1-sentence explanation for this tax risk.
            
            Client Profile: {profile_context}
            
            Risk Data:
            - Title: {risk_data['title']}
            - Tech Detail: {risk_data['description']}
            - Amount: ₹{risk_data['amount_involved']}
            
            Instructions:
            - If Client is 'Conservative', emphasize safety and compliance.
            - If Client is 'Aggressive', emphasize strategic correction.
            - Be professional and direct.
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"AI Error: {e}")
            return risk_data['description']

    def summarize_notice_text(self, ocr_text: str) -> dict:
        """
        Extracts structured data from Notice PDF text.
        """
        if not self.model:
            return {"summary": "AI Unavailable", "section": "Unknown"}

        try:
            prompt = f"""
            Extract JSON from this Tax Notice:
            Text: {ocr_text[:4000]}
            
            Schema:
            {{
                "section": "e.g. 143(1)",
                "date": "YYYY-MM-DD",
                "demand_amount": 0.0,
                "summary": "1 sentence summary"
            }}
            """
            response = self.model.generate_content(
                prompt, 
                generation_config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"AI Parsing Error: {e}")
            return {}