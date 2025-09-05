from abc import ABC, abstractmethod
from typing import Dict, Any
from app.llm import get_llm_client

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.llm = get_llm_client()
    
    @abstractmethod
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the context and return results"""
        pass
    
    def create_prompt(self, template: str, context: Dict[str, Any]) -> str:
        """Create prompt from template and context"""
        return template.format(**context)