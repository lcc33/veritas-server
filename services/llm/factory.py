import logging
from core.config import settings

logger = logging.getLogger(__name__)

class LLMFactory:
    @staticmethod
    def create_gemini_client(system_prompt: str = None):
        """Create and return a configured Gemini client"""
        try:
            from .gemini import Gemini
            
            # Enhanced system prompt for fact-checking
            fact_checking_system_prompt = """
            You are Veritas, an expert fact-checking assistant. Your role is to analyze claims against provided evidence.

            GUIDELINES:
            - Be objective, evidence-based, and impartial
            - Only use the provided evidence sources, do not use external knowledge
            - If evidence is insufficient or conflicting, return "unclear"
            - Provide clear, concise rationales explaining your reasoning
            - Use confidence scores from 0-100 based on evidence strength and source credibility
            - Never hallucinate or invent facts not present in the evidence
            - Focus on factual accuracy, not opinions or beliefs

            Always respond with valid JSON in the exact format specified.
            """
            
            final_prompt = system_prompt or fact_checking_system_prompt
            
            if not settings.gemini_api_key:
                logger.error("Gemini API key not found in environment variables")
                return None
                
            client = Gemini(api_key=settings.gemini_api_key, system_prompt=final_prompt)
            logger.info("Gemini client created successfully")
            return client
            
        except ImportError as e:
            logger.error(f"Failed to import Gemini: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to create Gemini client: {e}")
            return None