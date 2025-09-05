from app.agents.base_agent import BaseAgent
from typing import Dict, Any

class BudgetAgent(BaseAgent):
    """Agent responsible for budget analysis"""
    
    def __init__(self):
        super().__init__("BudgetAgent", "Travel Budget Analyst")
    
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        system_prompt = """You are a travel budget expert. Analyze the trip cost breakdown.
        
        Return your response as JSON in this exact format:
        {
            "breakdown": {
                "flights": 500,
                "accommodation": 300,
                "food": 200,
                "activities": 150,
                "transport": 100,
                "misc": 50
            },
            "total": 1300,
            "daily_average": 260,
            "budget_tips": ["tip1", "tip2"]
        }"""
        
        prompt = f"""
        Estimate costs for a {context['days']}-day trip to {context['destination']}.
        Origin: {context['origin_city']}
        Month: {context['month']}
        Total budget: ${context['budget_total']}
        
        Provide realistic cost breakdown in USD.
        """
        
        response = self.llm.generate_json(prompt, system_prompt)
        
        if isinstance(response, dict) and "breakdown" in response:
            return response
        else:
            # Fallback budget
            per_day = context['budget_total'] / context['days']
            return {
                "breakdown": {
                    "flights": context['budget_total'] * 0.35,
                    "accommodation": context['budget_total'] * 0.25,
                    "food": context['budget_total'] * 0.20,
                    "activities": context['budget_total'] * 0.15,
                    "transport": context['budget_total'] * 0.05
                },
                "total": context['budget_total'],
                "daily_average": per_day,
                "budget_tips": ["Book in advance", "Use public transport"]
            }