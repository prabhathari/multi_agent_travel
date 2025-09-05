from app.agents.base_agent import BaseAgent
from typing import Dict, Any, List

class SafetyAgent(BaseAgent):
    """Agent responsible for safety and travel advisories"""
    
    def __init__(self):
        super().__init__("SafetyAgent", "Travel Safety Advisor")
    
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        system_prompt = """You are a travel safety expert. Provide safety advice and important information.
        
        Return your response as JSON in this exact format:
        {
            "safety_level": "Low/Medium/High",
            "visa_required": true/false,
            "vaccinations": ["vaccine1", "vaccine2"],
            "safety_tips": ["tip1", "tip2", "tip3"],
            "emergency_contacts": {
                "police": "number",
                "medical": "number"
            },
            "weather_advisory": "Brief weather description for the travel month"
        }"""
        
        prompt = f"""
        Provide safety information for travel to {context['destination']}.
        Traveler passport: {context['visa_passport']}
        Travel month: {context['month']}
        Duration: {context['days']} days
        
        Include visa requirements, health advisories, and safety tips.
        """
        
        response = self.llm.generate_json(prompt, system_prompt)
        
        if isinstance(response, dict) and "safety_tips" in response:
            return response
        else:
            # Fallback safety info
            return {
                "safety_level": "Low",
                "visa_required": False,
                "vaccinations": ["Routine vaccines up to date"],
                "safety_tips": [
                    "Keep copies of important documents",
                    "Register with your embassy",
                    "Get travel insurance"
                ],
                "emergency_contacts": {
                    "police": "911",
                    "medical": "Emergency services"
                },
                "weather_advisory": f"Typical weather for {context['month']}"
            }