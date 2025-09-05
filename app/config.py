import os
from dotenv import load_dotenv
from enum import Enum

load_dotenv()

class LLMProvider(Enum):
    GROQ = "groq"
    TOGETHER = "together"
    GEMINI = "gemini"

class Config:
    # API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # LLM Settings
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
    MODEL_TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", "0.7"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))
    
    # Model names for each provider
    MODELS = {
        "groq": "llama-3.3-70b-versatile",  # Fast and good
        "together": "meta-llama/Llama-3-8b-chat-hf",
        "gemini": "gemini-1.5-flash"
    }
    
    @classmethod
    def get_active_provider(cls):
        """Get the active LLM provider based on available API keys"""
        if cls.LLM_PROVIDER == "groq" and cls.GROQ_API_KEY:
            return LLMProvider.GROQ
        elif cls.LLM_PROVIDER == "together" and cls.TOGETHER_API_KEY:
            return LLMProvider.TOGETHER
        elif cls.LLM_PROVIDER == "gemini" and cls.GEMINI_API_KEY:
            return LLMProvider.GEMINI
        
        # Fallback to any available
        if cls.GROQ_API_KEY:
            return LLMProvider.GROQ
        elif cls.GEMINI_API_KEY:
            return LLMProvider.GEMINI
        elif cls.TOGETHER_API_KEY:
            return LLMProvider.TOGETHER
        
        raise ValueError("No valid API keys found. Please set at least one API key.")