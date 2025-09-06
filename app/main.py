# app/main.py - Complete version with security features

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import traceback
import os

# Import rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Import agents
from app.agents.destination_agent import DestinationAgent
from app.agents.itinerary_agent import ItineraryAgent
from app.agents.budget_agent import BudgetAgent
from app.agents.safety_agent import SafetyAgent

# Create rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Create FastAPI app with conditional docs (hidden in production)
app = FastAPI(
    title="Multi-Agent Travel Planner API",
    docs_url="/docs" if os.getenv("DEBUG", "false").lower() == "true" else None,
    redoc_url="/redoc" if os.getenv("DEBUG", "false").lower() == "true" else None,
)

# Add rate limit exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add security middleware - TrustedHost
#if os.getenv("ALLOWED_HOSTS"):
  #  app.add_middleware(
   #     TrustedHostMiddleware,
    #    allowed_hosts=os.getenv("ALLOWED_HOSTS", "localhost").split(",")
   # )

# Add GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add CORS middleware with security
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost,http://127.0.0.1").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if os.getenv("DEBUG", "false").lower() != "true" else ["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
    max_age=3600,
)

# Add request size validation middleware
@app.middleware("http")
async def validate_content_length(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > 1048576:  # 1MB limit
        return JSONResponse(
            status_code=413, 
            content={"detail": "Request too large. Maximum size is 1MB"}
        )
    response = await call_next(request)
    return response

# Request/Response Models
class TripRequest(BaseModel):
    traveler_name: str
    origin_city: str
    days: int
    month: str
    budget_total: float
    interests: List[str]
    visa_passport: str
    preferred_destination: str = "" 
    
    # Validation
    class Config:
        schema_extra = {
            "example": {
                "traveler_name": "John Doe",
                "origin_city": "New York",
                "days": 7,
                "month": "June",
                "budget_total": 2000,
                "interests": ["beach", "culture", "food"],
                "visa_passport": "US"
            }
        }

class TripResponse(BaseModel):
    destination: str
    destination_info: Dict[str, Any]
    itinerary: List[Dict[str, Any]]
    budget_analysis: Dict[str, Any]
    safety_info: Dict[str, Any]
    within_budget: bool
    agent_messages: List[Dict[str, str]]

# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Multi-Agent Travel Planner API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "plan": "/plan",
            "docs": "/docs (disabled in production)"
        }
    }

# Health check endpoint (no rate limit)
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "multi-agent-travel-planner"
    }

# Model info endpoint
@app.get("/models")
def get_model_info():
    """Get information about available models and current configuration"""
    from app.config import Config
    
    try:
        provider = Config.get_active_provider()
        return {
            "status": "success",
            "current_provider": provider.value,
            "model_temperature": Config.MODEL_TEMPERATURE,
            "max_tokens": Config.MAX_TOKENS,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# Main trip planning endpoint with rate limiting
@app.post("/plan", response_model=TripResponse)
@limiter.limit("5 per minute")  # Rate limit: 5 requests per minute
async def generate_trip_plan(request: Request, trip_request: TripRequest):
    """
    Generate a complete trip plan using multiple AI agents.
    
    Rate limited to 5 requests per minute per IP address.
    """
    
    agent_messages = []
    
    # Validate input
    if trip_request.days < 1 or trip_request.days > 30:
        raise HTTPException(status_code=400, detail="Days must be between 1 and 30")
    
    if trip_request.budget_total < 100 or trip_request.budget_total > 100000:
        raise HTTPException(status_code=400, detail="Budget must be between $100 and $100,000")
    
    if len(trip_request.interests) == 0:
        raise HTTPException(status_code=400, detail="At least one interest must be selected")
    
    try:
        # Convert request to dict for easier passing
        context = trip_request.dict()
        
        # Step 1: Destination Selection
        print(f"Processing trip request for {trip_request.traveler_name}")
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
        
        # Calculate total cost and check if within budget
        if 'breakdown' in budget_analysis:
            total_cost = sum(budget_analysis['breakdown'].values())
        else:
            total_cost = budget_analysis.get('total', 0)
        
        within_budget = total_cost <= trip_request.budget_total
        
        agent_messages.append({
            "agent": "BudgetAgent",
            "role": "Budget Analyst",
            "content": f"Estimated total cost: ${total_cost:.2f} (Budget: ${trip_request.budget_total})"
        })
        
        # Step 4: Safety Advisory
        safety_agent = SafetyAgent()
        safety_info = safety_agent.process(context)
        
        agent_messages.append({
            "agent": "SafetyAgent",
            "role": "Safety Advisor",
            "content": f"Safety level: {safety_info.get('safety_level', 'Unknown')}, Visa required: {safety_info.get('visa_required', 'Check requirements')}"
        })
        
        # Return the complete trip plan
        return TripResponse(
            destination=destination_info['destination'],
            destination_info=destination_info,
            itinerary=itinerary,
            budget_analysis=budget_analysis,
            safety_info=safety_info,
            within_budget=within_budget,
            agent_messages=agent_messages
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in trip planning: {str(e)}")
        print(traceback.format_exc())
        
        # Don't expose internal errors in production
        if os.getenv("DEBUG", "false").lower() == "true":
            raise HTTPException(status_code=500, detail=f"Error generating trip plan: {str(e)}")
        else:
            raise HTTPException(status_code=500, detail="An error occurred while generating your trip plan. Please try again.")

# Test endpoint (only in debug mode)
if os.getenv("DEBUG", "false").lower() == "true":
    @app.get("/test")
    def test_endpoint():
        """Test endpoint to verify API is working"""
        return {
            "message": "API is working!",
            "debug_mode": True,
            "environment": {
                "llm_provider": os.getenv("LLM_PROVIDER", "not set"),
                "allowed_hosts": os.getenv("ALLOWED_HOSTS", "not set"),
            }
        }

# Run the application (for local development)
if __name__ == "__main__":
    import uvicorn
    
    # Check if we're in development mode
    if os.getenv("DEBUG", "false").lower() == "true":
        print("🚀 Starting in DEBUG mode with auto-reload...")
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
    else:
        print("🚀 Starting in PRODUCTION mode...")
        uvicorn.run(app, host="0.0.0.0", port=8000, workers=2)
