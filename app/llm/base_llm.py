from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json

class BaseLLM(ABC):
    """Base class for LLM providers"""
    
    def __init__(self, api_key: str, model: str, temperature: float = 0.7, max_tokens: int = 1000):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response from LLM"""
        pass
    
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Generate JSON response from LLM"""
        response = self.generate(prompt, system_prompt)
        
        # Try to extract JSON from response
        try:
            # Look for JSON between ```json and ``` markers
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response
            
            return json.loads(json_str)
        except json.JSONDecodeError:
            # If JSON parsing fails, return as text
            return {"response": response}