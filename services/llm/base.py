from abc import ABC, abstractmethod
from typing import Optional

class AIPlatform(ABC):
    def __init__(self, api_key: str, system_prompt: Optional[str] = None):
        self.api_key = api_key
        self.system_prompt = system_prompt
    
    @abstractmethod
    def chat(self, prompt: str) -> str:
        pass
    
    @abstractmethod
    def generate_structured(self, prompt: str, response_format: dict) -> dict:
        pass