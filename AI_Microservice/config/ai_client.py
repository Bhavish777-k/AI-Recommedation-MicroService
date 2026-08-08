# config/ai_client.py
from typing import Dict
from google.genai.errors import ClientError
from config.gemini import client as gemini_client

class AIClient:
    def __init__(self, gemini_client):
        self.gemini = gemini_client

    def generate(self, prompt: str, model: str = "gemini-flash-latest", timeout: int = 30) -> Dict:
        """
        Synchronous wrapper around google.genai client.models.generate_content.
        Returns a dict with key 'text' or raises an exception.
        """
        try:
            resp = self.gemini.models.generate_content(model=model, contents=prompt)
            # resp.text contains the generated text
            return {"text": getattr(resp, "text", str(resp))}
        except ClientError as e:
            # propagate structured error
            raise

# instantiate
ai_client = AIClient(gemini_client)
