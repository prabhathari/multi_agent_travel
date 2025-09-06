from app.agents.base_agent import BaseAgent
from typing import Dict, Any
import json

class DestinationAgent(BaseAgent):
   """Agent responsible for selecting the best destination"""
   
   def __init__(self):
       super().__init__("DestinationAgent", "Travel Destination Expert")
   
   def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
       # Check if user provided a preferred destination
       if context.get('preferred_destination') and context['preferred_destination'].strip():
           # User specified a destination - validate and provide details
           system_prompt = """You are a travel destination expert. The user has specified a preferred destination.
           Validate if it's a real place and provide detailed information about it.
           Consider their budget, interests, and travel dates.
           
           Return your response as JSON in this exact format:
           {
               "destination": "City, Country",
               "reason": "Why this destination is good/bad for their preferences, budget, and timing",
               "highlights": ["highlight1", "highlight2", "highlight3"]
           }"""
           
           prompt = f"""
           The traveler wants to visit: {context['preferred_destination']}
           Traveler: {context['traveler_name']}
           From: {context['origin_city']}
           Duration: {context['days']} days
           Month: {context['month']}
           Budget: ${context['budget_total']} USD
           Interests: {', '.join(context['interests'])}
           Passport: {context['visa_passport']}
           
           Validate this destination exists and assess if it matches their requirements.
           If it's not suitable for their budget or timing, mention that in the reason.
           """
       else:
           # No preferred destination - AI suggests based on preferences
           system_prompt = """You are a travel destination expert. Based on the traveler's preferences, 
           suggest the BEST single destination. Consider budget, interests, visa requirements, and travel month.
           
           Return your response as JSON in this exact format:
           {
               "destination": "City, Country",
               "reason": "Brief explanation why this destination matches their preferences",
               "highlights": ["highlight1", "highlight2", "highlight3"]
           }"""
           
           prompt = f"""
           Traveler: {context['traveler_name']}
           From: {context['origin_city']}
           Duration: {context['days']} days
           Month: {context['month']}
           Budget: ${context['budget_total']} USD
           Interests: {', '.join(context['interests'])}
           Passport: {context['visa_passport']}
           
           Select the best destination and explain why.
           """
       
       response = self.llm.generate_json(prompt, system_prompt)
       
       # Ensure we have the required fields
       if isinstance(response, dict) and "destination" in response:
           return response
       else:
           # Fallback
           return {
               "destination": context.get('preferred_destination', 'Bali, Indonesia'),
               "reason": "Perfect for your interests and budget",
               "highlights": ["Beaches", "Temples", "Culture"]
           }
