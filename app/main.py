from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import traceback

# Import agents
from app.agents.destination_agent import DestinationAgent
from app.agents.itinerary_agent import ItineraryAgent
from app.agents.budget_agent import BudgetAgent
from app.agents.safety_agent import SafetyAgent

app = FastAPI(title="Multi-Agent Travel Planner API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class TripRequest(BaseModel):
    traveler_name: str
    origin_city: str
    days: int
    month: str
    budget_total: float
    interests: List[str]
    visa_passport: str

class TripResponse(BaseModel):
    destination: str
    destination_info: Dict[str, Any]
    itinerary: List[Dict[str, Any]]
    budget_analysis: Dict[str, Any]
    safety_info: Dict[str, Any]
    within_budget: bool
    agent_messages: List[Dict[str, str]]

@app.get("/")
def read_root():
    return {"message": "Multi-Agent Travel Planner API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/plan", response_model=TripResponse)
async def generate_trip_plan(request: TripRequest):
    """Generate a complete trip plan using multiple AI agents"""
    
    agent_messages = []
    
    try:
        # Convert request to dict for easier passing
        context = request.dict()
        
        # Step 1: Destination Selection
        dest_agent = DestinationAgent()
        destination_info = dest_agent.process(context)
        context['destination'] = destination_info['destination']
        
        agent_messages.append({
            "agent": "DestinationAgent",
            "role": "Destination Expert",
            "content": f"Selected {destination_info['destination']}: {destination_info.get('reason', '')}"
        })
        
        # Step 2: Itinerary Planning
        itin_agent = ItineraryAgent()
        itinerary = itin_agent.process(context)
        
        agent_messages.append({
            "agent": "ItineraryAgent",
            "role": "Itinerary Planner",
            "content": f"Created {len(itinerary)}-day detailed itinerary"
        })
        
        # Step 3: Budget Analysis
        budget_agent = BudgetAgent()
        budget_analysis = budget_agent.process(context)
        
        total_cost = budget_analysis.get('total', sum(budget_analysis.get('breakdown', {}).values()))
        within_budget = total_cost <= request.budget_total
        
        agent_messages.append({
            "agent": "BudgetAgent",
            "role": "Budget Analyst",
            "content": f"Estimated total cost: ${total_cost:.2f} (Budget: ${request.budget_total})"
        })
        
        # Step 4: Safety Advisory
        safety_agent = SafetyAgent()
        safety_info = safety_agent.process(context)
        
        agent_messages.append({
            "agent": "SafetyAgent",
            "role": "Safety Advisor",
            "content": f"Safety level: {safety_info.get('safety_level', 'Unknown')}, Visa required: {safety_info.get('visa_required', 'Check requirements')}"
        })
        
        return TripResponse(
            destination=destination_info['destination'],
            destination_info=destination_info,
            itinerary=itinerary,
            budget_analysis=budget_analysis,
            safety_info=safety_info,
            within_budget=within_budget,
            agent_messages=agent_messages
        )
        
    except Exception as e:
        print(f"Error in trip planning: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating trip plan: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)