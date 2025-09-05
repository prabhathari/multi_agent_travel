from app.config import Config, LLMProvider
from app.llm.groq_llm import GroqLLM
from app.llm.base_llm import BaseLLM
import google.generativeai as genai

def get_llm_client() -> BaseLLM:
    """Factory function to get the appropriate LLM client"""
    provider = Config.get_active_provider()
    
    if provider == LLMProvider.GROQ:
        return GroqLLM(
            api_key=Config.GROQ_API_KEY,
            model=Config.MODELS["groq"],
            temperature=Config.MODEL_TEMPERATURE,
            max_tokens=Config.MAX_TOKENS
        )
    elif provider == LLMProvider.GEMINI:
        # For Gemini, we'll use a simple wrapper
        class GeminiLLM(BaseLLM):
            def __init__(self, api_key, model, temperature, max_tokens):
                super().__init__(api_key, model, temperature, max_tokens)
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(model)
            
            def generate(self, prompt, system_prompt=None):
                full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                response = self.model.generate_content(full_prompt)
                return response.text
        
        return GeminiLLM(
            api_key=Config.GEMINI_API_KEY,
            model=Config.MODELS["gemini"],
            temperature=Config.MODEL_TEMPERATURE,
            max_tokens=Config.MAX_TOKENS
        )
    
    raise ValueError(f"Unsupported LLM provider: {provider}")