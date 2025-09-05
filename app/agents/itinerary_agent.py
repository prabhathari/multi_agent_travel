from app.agents.base_agent import BaseAgent
from typing import Dict, Any, List

class ItineraryAgent(BaseAgent):
    """Agent responsible for creating detailed itineraries"""
    
    def __init__(self):
        super().__init__("ItineraryAgent", "Travel Itinerary Planner")
    
    def process(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        system_prompt = """You are a travel itinerary expert. Create a day-by-day itinerary.
        
        Return your response as JSON in this exact format:
        {
            "itinerary": [
                {
                    "day": 1,
                    "title": "Arrival and Exploration",
                    "morning": "Activity description",
                    "afternoon": "Activity description", 
                    "evening": "Activity description",
                    "meal_suggestions": ["restaurant1", "restaurant2"]
                }
            ]
        }"""
        
        prompt = f"""
        Create a {context['days']}-day itinerary for {context['destination']}.
        Traveler interests: {', '.join(context['interests'])}
        Month of travel: {context['month']}
        Budget level: ${context['budget_total']} for entire trip
        
        Include specific activities, landmarks, and meal recommendations.
        """
        
        response = self.llm.generate_json(prompt, system_prompt)
        
        if isinstance(response, dict) and "itinerary" in response:
            return response["itinerary"]
        else:
            # Fallback itinerary
            return [
                {
                    "day": i + 1,
                    "title": f"Day {i + 1}",
                    "morning": "Explore local area",
                    "afternoon": "Visit main attractions",
                    "evening": "Dinner and relaxation",
                    "meal_suggestions": ["Local restaurant"]
                }
                for i in range(context['days'])
            ]