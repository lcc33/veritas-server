import os
import google.generativeai as genai
import json
import logging
from typing import Optional
from .base import AIPlatform

logger = logging.getLogger(__name__)

class Gemini(AIPlatform):
    def __init__(self, api_key: str, system_prompt: str = None):
        super().__init__(api_key, system_prompt)
        try:
            genai.configure(api_key=self.api_key)
            # Using flash for speed + cost efficiency
            self.model = genai.GenerativeModel("gemini-1.5-flash")
            logger.info("Gemini model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            raise

    def chat(self, prompt: str) -> str:
        if self.system_prompt:
            prompt = f"{self.system_prompt}\n\n{prompt}"

        try:
            response = self.model.generate_content(prompt)
            if response.text:
                return response.text
            else:
                raise Exception("Empty response from Gemini")
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise Exception(f"Gemini API error: {str(e)}")

    def generate_structured(self, prompt: str, response_format: dict) -> dict:
        """Generate structured JSON responses for fact-checking"""
        structured_prompt = f"""
        {prompt}
        
        You MUST respond with ONLY valid JSON in this exact format:
        {json.dumps(response_format, indent=2)}
        
        IMPORTANT: 
        - Do not include any other text, explanations, or markdown formatting
        - Do not use code blocks or backticks
        - Return pure JSON only
        
        Your response:
        """
        
        try:
            response_text = self.chat(structured_prompt)
            logger.debug(f"Raw Gemini response: {response_text}")
            
            # Clean response and parse JSON
            cleaned_response = response_text.strip()
            
            # Remove any potential markdown code blocks
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            
            cleaned_response = cleaned_response.strip()
            
            # Parse JSON
            result = json.loads(cleaned_response)
            logger.debug(f"Parsed Gemini response: {result}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.error(f"Response was: {response_text}")
            # Return a default structure if parsing fails
            return {
                "verdict": "unclear",
                "confidence": 50.0,
                "rationale": "Analysis failed due to technical error.",
                "relevant_source_indices": []
            }
        except Exception as e:
            logger.error(f"Gemini structured generation failed: {e}")
            return {
                "verdict": "unclear", 
                "confidence": 50.0,
                "rationale": "Analysis service unavailable.",
                "relevant_source_indices": []
            }