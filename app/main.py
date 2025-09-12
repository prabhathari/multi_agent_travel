# app/main.py - Complete version with Phase 2 authentication and database features

from fastapi import FastAPI, HTTPException, Request, Depends
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

# Phase 2: Import authentication and database
from app.auth.routes import router as auth_router
from app.auth.routes import get_current_user
from app.database import init_database, get_db
from app.auth.models import User, Trip, Feedback
from sqlalchemy.orm import Session

# Create rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Create FastAPI app with conditional docs (hidden in production)
app = FastAPI(
    title="Multi-Agent Travel Planner API - Phase 2",
    docs_url="/docs" if os.getenv("DEBUG", "false").lower() == "true" else None,
    redoc_url="/redoc" if os.getenv("DEBUG", "false").lower() == "true" else None,
)

# Phase 2: Include authentication router
app.include_router(auth_router)

# Add rate limit exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add security middleware - TrustedHost
#if os.getenv("ALLOWED_HOSTS"):
#    app.add_middleware(
#        TrustedHostMiddleware,
#        allowed_hosts=os.getenv("ALLOWED_HOSTS", "localhost").split(",")
#    )

# Add GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add CORS middleware with security
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost,http://127.0.0.1").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if os.getenv("DEBUG", "false").lower() != "true" else ["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=3600,
)

# Phase 2: Database initialization
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_database()

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
        "message": "Multi-Agent Travel Planner API - Phase 2",
        "status": "running",
        "version": "2.0.0",
        "features": ["Authentication", "Database", "Multi-user"],
        "endpoints": {
            "health": "/health",
            "plan": "/plan (requires auth)",
            "auth": "/auth/login, /auth/signup",
            "trips": "/trips (user history)",
            "docs": "/docs (disabled in production)"
        }
    }

# Health check endpoint (no rate limit)
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "multi-agent-travel-planner",
        "version": "2.0.0",
        "database": "connected"
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

# Phase 2: Enhanced trip planning endpoint with authentication and database
@app.post("/plan", response_model=TripResponse)
@limiter.limit("5 per minute")  # Rate limit: 5 requests per minute
async def generate_trip_plan(
    request: Request, 
    trip_request: TripRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a complete trip plan using multiple AI agents.
    
    **Phase 2 Features:**
    - Requires user authentication
    - Saves trip to user's personal database
    - Rate limited to 5 requests per minute per IP address
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
        print(f"Processing trip request for {trip_request.traveler_name} (User: {current_user.name}, ID: {current_user.id})")
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
        
        # Create complete trip plan
        complete_plan = {
            "destination": destination_info['destination'],
            "destination_info": destination_info,
            "itinerary": itinerary,
            "budget_analysis": budget_analysis,
            "safety_info": safety_info,
            "within_budget": within_budget,
            "agent_messages": agent_messages
        }
        
        # Phase 2: Save trip to database instead of JSON file
        db_trip = Trip(
            user_id=current_user.id,
            title=f"{trip_request.days}-day trip to {destination_info['destination']}",
            destination=destination_info['destination'],
            origin_city=trip_request.origin_city,
            days=trip_request.days,
            month=trip_request.month,
            budget_total=trip_request.budget_total,
            interests=trip_request.interests,
            visa_passport=trip_request.visa_passport,
            preferred_destination=trip_request.preferred_destination,
            trip_data=complete_plan  # Store complete AI response as JSONB
        )
        
        db.add(db_trip)
        db.commit()
        db.refresh(db_trip)
        
        print(f"✅ Trip saved to database with ID: {db_trip.id} for user: {current_user.email}")
        
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

# Phase 2: Get user's trip history from database
@app.get("/trips")
async def get_user_trips(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """Get authenticated user's trip history from database"""
    
    trips = db.query(Trip).filter(
        Trip.user_id == current_user.id
    ).order_by(Trip.created_at.desc()).offset(skip).limit(limit).all()
    
    trip_list = []
    for trip in trips:
        trip_list.append({
            "id": str(trip.id),
            "title": trip.title,
            "destination": trip.destination,
            "origin_city": trip.origin_city,
            "days": trip.days,
            "month": trip.month,
            "budget_total": float(trip.budget_total),
            "interests": trip.interests,
            "created_at": trip.created_at.isoformat(),
            "is_favorite": trip.is_favorite,
            "trip_data": trip.trip_data  # Complete plan data
        })
    
    return {
        "trips": trip_list,
        "total": len(trip_list),
        "user": {
            "id": str(current_user.id),
            "name": current_user.name,
            "email": current_user.email
        }
    }

# Phase 2: Submit feedback for a trip
@app.post("/trips/{trip_id}/feedback")
async def submit_trip_feedback(
    trip_id: str,
    feedback_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit feedback for a specific trip"""
    
    # Verify trip belongs to user
    trip = db.query(Trip).filter(
        Trip.id == trip_id,
        Trip.user_id == current_user.id
    ).first()
    
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    # Check if feedback already exists
    existing_feedback = db.query(Feedback).filter(
        Feedback.trip_id == trip_id,
        Feedback.user_id == current_user.id
    ).first()
    
    if existing_feedback:
        # Update existing feedback
        existing_feedback.rating = feedback_data.get("rating", existing_feedback.rating)
        existing_feedback.aspects = feedback_data.get("aspects", existing_feedback.aspects)
        existing_feedback.comment = feedback_data.get("comment", existing_feedback.comment)
    else:
        # Create new feedback
        feedback = Feedback(
            trip_id=trip_id,
            user_id=current_user.id,
            rating=feedback_data.get("rating", 5),
            aspects=feedback_data.get("aspects", []),
            comment=feedback_data.get("comment", "")
        )
        db.add(feedback)
    
    db.commit()
    
    return {"message": "Feedback submitted successfully"}

# Phase 2: Get trip feedback
@app.get("/trips/{trip_id}/feedback")
async def get_trip_feedback(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get feedback for a specific trip"""
    
    # Verify trip belongs to user
    trip = db.query(Trip).filter(
        Trip.id == trip_id,
        Trip.user_id == current_user.id
    ).first()
    
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    feedback = db.query(Feedback).filter(
        Feedback.trip_id == trip_id,
        Feedback.user_id == current_user.id
    ).first()
    
    if not feedback:
        return {"feedback": None}
    
    return {
        "feedback": {
            "id": str(feedback.id),
            "rating": feedback.rating,
            "aspects": feedback.aspects,
            "comment": feedback.comment,
            "created_at": feedback.created_at.isoformat()
        }
    }

# Phase 2: Get user statistics
@app.get("/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user travel statistics"""
    
    # Count trips
    total_trips = db.query(Trip).filter(Trip.user_id == current_user.id).count()
    
    # Calculate total budget spent
    trips = db.query(Trip).filter(Trip.user_id == current_user.id).all()
    total_budget = sum([float(trip.budget_total) for trip in trips])
    
    # Calculate average rating
    feedbacks = db.query(Feedback).filter(Feedback.user_id == current_user.id).all()
    avg_rating = sum([f.rating for f in feedbacks]) / max(len(feedbacks), 1)
    
    # Get favorite destinations
    destinations = {}
    for trip in trips:
        dest = trip.destination
        destinations[dest] = destinations.get(dest, 0) + 1
    
    top_destinations = sorted(destinations.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "total_trips": total_trips,
        "total_budget": total_budget,
        "average_rating": round(avg_rating, 1),
        "favorite_destinations": top_destinations,
        "user": {
            "name": current_user.name,
            "email": current_user.email,
            "member_since": current_user.created_at.isoformat()
        }
    }

# Add this new endpoint for guest users
@app.post("/plan-guest", response_model=TripResponse)
@limiter.limit("10 per minute")  # Higher limit for guests
async def generate_trip_plan_guest(request: Request, trip_request: TripRequest):
    """
    Generate a trip plan for guest users (no authentication required)
    """
    
    agent_messages = []
    
    # Same validation as authenticated endpoint
    if trip_request.days < 1 or trip_request.days > 30:
        raise HTTPException(status_code=400, detail="Days must be between 1 and 30")
    
    if trip_request.budget_total < 100 or trip_request.budget_total > 100000:
        raise HTTPException(status_code=400, detail="Budget must be between $100 and $100,000")
    
    if len(trip_request.interests) == 0:
        raise HTTPException(status_code=400, detail="At least one interest must be selected")
    
    try:
        # Same AI agent processing as authenticated users
        context = trip_request.dict()
        
        # AI agents (same as authenticated)
        dest_agent = DestinationAgent()
        destination_info = dest_agent.process(context)
        context['destination'] = destination_info['destination']
        
        agent_messages.append({
            "agent": "DestinationAgent",
            "role": "Destination Expert",
            "content": f"Selected {destination_info['destination']}: {destination_info.get('reason', '')}"
        })
        
        itin_agent = ItineraryAgent()
        itinerary = itin_agent.process(context)
        
        agent_messages.append({
            "agent": "ItineraryAgent",
            "role": "Itinerary Planner",
            "content": f"Created {len(itinerary)}-day detailed itinerary"
        })
        
        budget_agent = BudgetAgent()
        budget_analysis = budget_agent.process(context)
        
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
        
        safety_agent = SafetyAgent()
        safety_info = safety_agent.process(context)
        
        agent_messages.append({
            "agent": "SafetyAgent",
            "role": "Safety Advisor",
            "content": f"Safety level: {safety_info.get('safety_level', 'Unknown')}"
        })
        
        print(f"Guest trip plan generated for {trip_request.traveler_name} to {destination_info['destination']}")
        
        # Return plan (not saved to database)
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
        print(f"Error in guest trip planning: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while generating your trip plan. Please try again.")
# Test endpoint (only in debug mode)
if os.getenv("DEBUG", "false").lower() == "true":
    @app.get("/test")
    def test_endpoint():
        """Test endpoint to verify API is working"""
        return {
            "message": "Phase 2 API is working!",
            "debug_mode": True,
            "features": ["Authentication", "Database", "Multi-user"],
            "environment": {
                "llm_provider": os.getenv("LLM_PROVIDER", "not set"),
                "database_url": "configured" if os.getenv("DATABASE_URL") else "not set",
            }
        }

# Run the application (for local development)
if __name__ == "__main__":
    import uvicorn
    
    # Check if we're in development mode
    if os.getenv("DEBUG", "false").lower() == "true":
        print("🚀 Starting Phase 2 in DEBUG mode with auto-reload...")
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
    else:
        print("🚀 Starting Phase 2 in PRODUCTION mode...")
        uvicorn.run(app, host="0.0.0.0", port=8000, workers=2)

# ==========================================
# REAL LLM CHAT ENDPOINT - Phase 3B Final
# ==========================================

from pydantic import BaseModel
from app.llm import get_llm_client

class ChatRequest(BaseModel):
    message: str
    trip_context: dict = None

class ChatResponse(BaseModel):
    response: str
    agent: str = "🤖 AI Assistant"

@app.post("/chat", response_model=ChatResponse)
@limiter.limit("20 per minute")  # Rate limit: 20 chat messages per minute
async def chat_with_ai(
    request: Request,
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Real LLM-powered chat endpoint for travel assistance
    """
    
    try:
        # Get LLM client (Groq/Gemini)
        llm = get_llm_client()
        
        # Prepare context-aware system prompt
        system_prompt = """You are an expert travel assistant. You provide helpful, accurate, and specific travel advice.

IMPORTANT INSTRUCTIONS:
- Be conversational and friendly
- Use emojis appropriately (but not excessively)
- Keep responses under 300 words
- Be specific and actionable
- If user has a trip context, use it to provide personalized advice

Response format: Provide direct, helpful answers without unnecessary introductions."""

        # Add trip context if available
        if chat_request.trip_context:
            destination = chat_request.trip_context.get('destination', 'the destination')
            budget_info = chat_request.trip_context.get('budget_analysis', {})
            itinerary = chat_request.trip_context.get('itinerary', [])
            safety_info = chat_request.trip_context.get('safety_info', {})
            
            context_prompt = f"""
CURRENT TRIP CONTEXT:
- Destination: {destination}
- Duration: {len(itinerary)} days
- Budget: ${budget_info.get('total', 0):,.2f}
- Safety Level: {safety_info.get('safety_level', 'Unknown')}

Use this context to provide specific, personalized advice about their {destination} trip.
"""
            
            system_prompt += context_prompt
        
        # Prepare user prompt with context awareness
        if chat_request.trip_context:
            destination = chat_request.trip_context.get('destination', 'your destination')
            user_prompt = f"User is asking about their {destination} trip: {chat_request.message}"
        else:
            user_prompt = f"User question: {chat_request.message}"
        
        # Call the real LLM
        try:
            ai_response = llm.generate(user_prompt, system_prompt)
            
            # Determine agent type based on question content
            message_lower = chat_request.message.lower()
            
            if any(word in message_lower for word in ['budget', 'cost', 'money', 'price']):
                agent = "💰 Budget Analyst"
            elif any(word in message_lower for word in ['day', 'itinerary', 'plan', 'schedule']):
                agent = "🗓️ Itinerary Planner"
            elif any(word in message_lower for word in ['safe', 'safety', 'visa', 'danger']):
                agent = "🛡️ Safety Advisor"
            elif any(word in message_lower for word in ['food', 'restaurant', 'eat', 'cuisine']):
                agent = "🍽️ Food Expert"
            elif any(word in message_lower for word in ['weather', 'climate', 'pack', 'clothes']):
                agent = "🌤️ Weather Expert"
            else:
                agent = "🤖 AI Travel Assistant"
            
            return ChatResponse(
                response=ai_response,
                agent=agent
            )
            
        except Exception as llm_error:
            # Fallback if LLM fails
            print(f"LLM Error: {llm_error}")
            
            fallback_response = "I'm having trouble processing your request right now. Please try rephrasing your question or try again in a moment."
            
            return ChatResponse(
                response=fallback_response,
                agent="🤖 AI Assistant"
            )
    
    except Exception as e:
        print(f"Chat endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail="Chat service temporarily unavailable")

# Guest chat endpoint (no authentication required)
@app.post("/chat-guest", response_model=ChatResponse)
@limiter.limit("10 per minute")  # Lower limit for guests
async def chat_with_ai_guest(
    request: Request,
    chat_request: ChatRequest
):
    """
    Chat endpoint for guest users (no authentication required)
    """
    
    try:
        # Get LLM client
        llm = get_llm_client()
        
        # Basic system prompt for guests
        system_prompt = """You are a travel assistant. Provide helpful travel advice.

INSTRUCTIONS:
- Be friendly and conversational
- Keep responses under 250 words
- Use emojis appropriately
- Be encouraging about travel planning

For guests without accounts, focus on general travel advice and encourage them to create an account for personalized trip planning."""

        # Add context if available
        if chat_request.trip_context:
            destination = chat_request.trip_context.get('destination', 'the destination')
            context_info = f"\nUser has a planned trip to {destination}. Provide specific advice about this destination."
            system_prompt += context_info
        
        # Generate response
        try:
            ai_response = llm.generate(chat_request.message, system_prompt)
            
            return ChatResponse(
                response=ai_response,
                agent="🤖 AI Travel Assistant"
            )
            
        except Exception as llm_error:
            # Fallback for guests
            fallback_response = f"I understand you're asking about: '{chat_request.message}'\n\nI'm having some technical difficulties right now. For the best travel planning experience with personalized AI assistance, consider creating an account!"
            
            return ChatResponse(
                response=fallback_response,
                agent="🤖 Travel Assistant"
            )
    
    except Exception as e:
        print(f"Guest chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="Chat service temporarily unavailable")

# Chat history endpoint (for authenticated users)
@app.get("/chat/history")
async def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """
    Get user's recent chat history (if you want to implement persistence)
    For now, this is a placeholder - you could store chat messages in database
    """
    
    # This is a placeholder - you could implement chat history storage
    # For now, chat history is maintained in the frontend session state
    
    return {
        "message": "Chat history is maintained in session",
        "note": "Implement database storage for persistent chat history"
    }

print("✅ Real LLM chat endpoints added to FastAPI backend!")
