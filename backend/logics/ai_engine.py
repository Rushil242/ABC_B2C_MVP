import os
import json
import logging
import google.generativeai as genai
from typing import Dict, Any

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
# Replace 'gemini-1.5-flash' with 'gemini-3.0-flash' if/when available to you.
# Currently, 1.5 Flash is the production standard for high-speed, low-latency tasks.
MODEL_NAME = "gemini-3.0-flash" 

class AIEngine:
    """
    Production-ready wrapper for Google Gemini API.
    Handles text generation and structured JSON extraction.
    """

    def __init__(self):
        # 1. Setup API Key
        # Ensure GEMINI_API_KEY is set in your environment variables
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not found. AI features will fail or return mocks.")
            self.model = None
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(MODEL_NAME)

    def generate_human_explanation(self, risk_data: Dict[str, Any]) -> str:
        """
        Uses LLM to write a professional, 2-sentence explanation of a specific tax risk.
        """
        if not self.model:
            return f"API Key Missing: {risk_data['description']}"

        try:
            # Construct a tight, specific prompt
            prompt = f"""
            Role: You are an expert Chartered Accountant (CA) in India.
            Task: Explain a specific tax risk to a client in simple, professional terms.
            Constraints: 
            1. Use exactly 2 sentences.
            2. Be direct but polite.
            3. Mention the specific amounts involved.
            
            Risk Data:
            - Type: {risk_data.get('type')}
            - Technical Description: {risk_data.get('description')}
            - Financial Impact: ₹{risk_data.get('impact_value')}
            
            Output:
            """

            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            logger.error(f"LLM Generation Error: {e}")
            # Fallback to hardcoded description if AI fails (Network/Quota issue)
            return f"{risk_data['description']} (AI Unavailable)"

    def summarize_notice(self, notice_text: str) -> Dict[str, Any]:
        """
        Uses Gemini's 'JSON Mode' to extract structured data from unstructured OCR text.
        """
        if not self.model:
            return self._mock_notice_response()

        try:
            # Prompt specifically designed for JSON extraction
            prompt = f"""
            Role: Indian Income Tax Expert.
            Task: Extract structured data from the following Tax Notice text.
            
            Input Text:
            \"\"\"{notice_text[:5000]}\"\"\" 
            (Truncated to 5k chars to save tokens if file is huge)

            Requirements:
            1. Identify the Section (e.g., "143(1)", "139(9)").
            2. Find the Total Demand Amount (if any). If 0 or Refund, put 0.
            3. Find the Response Deadline date.
            4. Write a 1-sentence layman summary of why this notice was sent.

            Output Schema (JSON Only):
            {{
                "section": "string",
                "demand_amount": float,
                "deadline": "YYYY-MM-DD",
                "summary": "string"
            }}
            """

            # FORCE JSON OUTPUT: This is a specific feature of Gemini
            response = self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )

            # Clean and Parse
            result = json.loads(response.text)
            return result

        except Exception as e:
            logger.error(f"LLM Extraction Error: {e}")
            return self._mock_notice_response()

    def _mock_notice_response(self):
        """Fallback if API fails"""
        return {
            "section": "Unknown",
            "demand_amount": 0,
            "deadline": "Unknown",
            "summary": "Could not analyze notice due to AI service error."
        }