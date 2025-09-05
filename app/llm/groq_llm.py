from groq import Groq
from app.llm.base_llm import BaseLLM
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential

class GroqLLM(BaseLLM):
    """Groq LLM implementation - Fast inference with Llama and Mixtral models"""
    
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile", 
                 temperature: float = 0.7, max_tokens: int = 1000):
        super().__init__(api_key, model, temperature, max_tokens)
        self.client = Groq(api_key=api_key)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            
            return completion.choices[0].message.content
        
        except Exception as e:
            print(f"Error with Groq API: {e}")
            raise