# app/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI(title="Mini Multi-Agent Travel Planner")

# -----------------------------
# Request / Response Models
# -----------------------------
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
    itinerary: List[Dict[str, Any]]
    estimated_cost_breakdown: Dict[str, float]
    within_budget: bool
    safety_notes: List[str]
    messages: List[Dict[str, str]]

# -----------------------------
# Mock LLM (simulated responses)
# -----------------------------
def mock_llm_response(agent: str, context: Dict[str, Any]) -> str:
    if agent == "DestinationAgent":
        if "beach" in context["interests"]:
            return "Bali"
        elif "mountains" in context["interests"]:
            return "Nepal"
        else:
            return "Paris"
    elif agent == "ItineraryAgent":
        return "Day 1: Arrival and local food tour. Day 2: Beach or museum. Day 3: Hiking or temple visit."
    elif agent == "BudgetAgent":
        return "Flights: 400, Hotel: 300, Food: 150, Activities: 100"
    elif agent == "SafetyAgent":
        return "Carry travel insurance. Be aware of local customs."
    return "No response"

# -----------------------------
# Multi-Agent Orchestrator
# -----------------------------
@app.post("/plan", response_model=TripResponse)
def generate_trip_plan(request: TripRequest):
    messages = []

    # Destination Agent
    destination = mock_llm_response("DestinationAgent", request.dict())
    messages.append({"agent": "DestinationAgent", "role": "planner", "content": destination})

    # Itinerary Agent
    itinerary_text = mock_llm_response("ItineraryAgent", {"destination": destination, **request.dict()})
    messages.append({"agent": "ItineraryAgent", "role": "planner", "content": itinerary_text})

    itinerary = [
        {"day": i+1, "highlights": [part.strip()], "notes": "Auto-generated"}
        for i, part in enumerate(itinerary_text.split(".")[:-1])
    ]

    # Budget Agent
    budget_text = mock_llm_response("BudgetAgent", request.dict())
    messages.append({"agent": "BudgetAgent", "role": "analyst", "content": budget_text})

    cost_items = {kv.split(":")[0].strip(): float(kv.split(":")[1].strip())
                  for kv in budget_text.split(",")}
    total_cost = sum(cost_items.values())
    within_budget = total_cost <= request.budget_total

    # Safety Agent
    safety_text = mock_llm_response("SafetyAgent", {"destination": destination})
    messages.append({"agent": "SafetyAgent", "role": "advisor", "content": safety_text})
    safety_notes = safety_text.split(".")

    return TripResponse(
        destination=destination,
        itinerary=itinerary,
        estimated_cost_breakdown=cost_items,
        within_budget=within_budget,
        safety_notes=[note.strip() for note in safety_notes if note.strip()],
        messages=messages,
    )
