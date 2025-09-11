import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, List, Any
import time
import uuid

# Set page config
st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Complete CSS
st.markdown("""
    <style>
    .main { 
        padding: 0.5rem 1rem; 
        max-width: 1000px;
        margin: 0 auto;
    }
    
    .block-container {
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
        max-width: 1000px;
        margin: 0 auto;
    }
    
    .stButton > button {
        border-radius: 20px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        font-weight: 600;
        height: 2.5rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    .user-profile, .guest-profile {
        padding: 1rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .user-profile {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .guest-profile {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
    }
    
    .user-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: rgba(255,255,255,0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 0.5rem auto;
        font-size: 16px;
        font-weight: bold;
    }
    
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 10px;
        padding: 0.5rem;
        margin: 0.25rem 0;
        text-align: center;
    }
    
    .dashboard-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .stForm {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 12px;
        max-width: 800px;
        margin: 1rem auto;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp { background: #fafafa; }
    </style>
""", unsafe_allow_html=True)

# Configuration
BACKEND_URL = "http://backend:8000"

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'guest_mode' not in st.session_state:
    st.session_state.guest_mode = False
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'user_trips' not in st.session_state:
    st.session_state.user_trips = []
if 'user_stats' not in st.session_state:
    st.session_state.user_stats = {}
if 'guest_trips' not in st.session_state:
    st.session_state.guest_trips = []
if 'current_page' not in st.session_state:
    st.session_state.current_page = "🏠 Dashboard"
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

# Helper functions
def make_api_request(endpoint, method="GET", data=None, auth_required=True):
    headers = {"Content-Type": "application/json"}
    if auth_required and st.session_state.access_token:
        headers["Authorization"] = f"Bearer {st.session_state.access_token}"
    
    url = f"{BACKEND_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=60)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=30)
        return response
    except:
        return None

def login_user(email, password):
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login", 
                               json={"email": email.strip().lower(), "password": password},
                               headers={"Content-Type": "application/json"}, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.access_token = data["access_token"]
            st.session_state.user_info = data["user"]
            st.session_state.authenticated = True
            st.session_state.guest_mode = False
            return True, "✅ Login successful!"
        else:
            return False, "❌ Invalid credentials"
    except:
        return False, "❌ Connection error"

def signup_user(email, name, password, origin_city="Hyderabad"):
    try:
        response = requests.post(f"{BACKEND_URL}/auth/signup",
                               json={"email": email.strip().lower(), "name": name.strip(),
                                    "password": password, "origin_city": origin_city},
                               headers={"Content-Type": "application/json"}, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.access_token = data["access_token"]
            st.session_state.user_info = data["user"]
            st.session_state.authenticated = True
            st.session_state.guest_mode = False
            return True, "🎉 Account created!"
        else:
            return False, "❌ Account creation failed"
    except:
        return False, "❌ Connection error"

def login_as_guest():
    st.session_state.authenticated = True
    st.session_state.guest_mode = True
    st.session_state.user_info = {"name": "Guest User", "email": "guest@example.com"}

def logout_user():
    if st.session_state.access_token and not st.session_state.guest_mode:
        make_api_request("/auth/logout", "POST")
    
    st.session_state.authenticated = False
    st.session_state.guest_mode = False
    st.session_state.access_token = None
    st.session_state.user_info = None
    st.session_state.current_page = "🏠 Dashboard"

def load_user_data():
    if st.session_state.guest_mode:
        st.session_state.user_trips = st.session_state.guest_trips
        st.session_state.user_stats = {
            "total_trips": len(st.session_state.guest_trips),
            "total_budget": sum([trip.get("budget_total", 0) for trip in st.session_state.guest_trips]),
            "average_rating": 4.5,
            "favorite_destinations": [],
            "user": st.session_state.user_info
        }
        return
    
    response = make_api_request("/trips")
    if response and response.status_code == 200:
        data = response.json()
        st.session_state.user_trips = data.get("trips", [])
    
    response = make_api_request("/stats")
    if response and response.status_code == 200:
        st.session_state.user_stats = response.json()

def render_login_page():
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="font-size: 2.5rem; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">✈️ AI Travel Planner</h1>
        <p style="font-size: 1rem; color: #666; margin: 0.5rem 0;">Phase 2 - Multi-user AI Travel Planning</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div style="max-width: 500px; margin: 1rem auto; text-align: center;"><h3>🚀 Quick Start</h3></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎯 Continue as Guest", use_container_width=True):
            login_as_guest()
            st.success("🎉 Welcome, Guest!")
            time.sleep(1)
            st.rerun()
    
    st.markdown("<p style='text-align: center; color: #666; font-size: 0.9rem; margin: 0.5rem 0;'><em>Guest mode: Plan trips without registration</em></p>", unsafe_allow_html=True)
    st.markdown('<hr style="margin: 1rem 0; border: none; height: 1px; background: linear-gradient(90deg, transparent, #ddd, transparent);">', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
    
    with tab1:
        col1, col2, col3 = st.columns([0.5, 3, 0.5])
        with col2:
            st.markdown("### Welcome Back! 👋")
            with st.form("login_form"):
                email = st.text_input("📧 Email", placeholder="your@email.com")
                password = st.text_input("🔒 Password", type="password")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    submitted = st.form_submit_button("🔑 Login", use_container_width=True)
                with col_b:
                    demo_login = st.form_submit_button("🧪 Demo", use_container_width=True)
                
                if submitted and email and password:
                    with st.spinner("Logging in..."):
                        success, message = login_user(email, password)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                
                if demo_login:
                    success, message = login_user("demo@example.com", "demo123")
                    if success:
                        st.success("Demo login successful!")
                        st.rerun()
    
    with tab2:
        col1, col2, col3 = st.columns([0.5, 3, 0.5])
        with col2:
            st.markdown("### Create Account 🆕")
            with st.form("signup_form"):
                name = st.text_input("👤 Name", placeholder="Your Name")
                email = st.text_input("📧 Email", placeholder="your@email.com")
                password = st.text_input("🔒 Password", type="password")
                city = st.text_input("🏙️ City", value="Hyderabad")
                
                if st.form_submit_button("📝 Create Account", use_container_width=True):
                    if name and email and password:
                        success, message = signup_user(email, name, password, city)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)

def render_sidebar():
    with st.sidebar:
        if st.session_state.user_info:
            user = st.session_state.user_info
            profile_class = "guest-profile" if st.session_state.guest_mode else "user-profile"
            
            st.markdown(f"""
            <div class="{profile_class}">
                <div class="user-avatar">{user['name'][0].upper()}</div>
                <h3 style="margin: 0;">{user['name']}</h3>
                <p style="margin: 0.25rem 0; font-size: 0.85rem;">{user['email']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        nav_options = ["🏠 Dashboard", "💬 AI Chat", "✈️ Plan New Trip", "📚 Trip History", "⚙️ Settings"]
        
        for option in nav_options:
            if st.button(option, use_container_width=True, 
                        key=f"nav_{option}", 
                        type="primary" if st.session_state.current_page == option else "secondary"):
                st.session_state.current_page = option
                st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.rerun()
        
        return st.session_state.current_page

def render_dashboard():
    st.header("📊 Your Travel Dashboard")
    st.markdown("""
    <div class="dashboard-card">
        <h2>🗺️ Ready for Your Next Adventure?</h2>
        <p>Start planning your dream trip!</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✈️ Plan Your First Trip", use_container_width=True, type="primary"):
            st.session_state.current_page = "✈️ Plan New Trip"
            st.rerun()

def get_smart_ai_response(user_message, context=None):
    """Generate smart contextual AI responses - Phase 3B"""
    message_lower = user_message.lower()
    
    # Smart destination responses
    if any(word in message_lower for word in ["kamakya", "temple", "guwahati", "assam"]):
        return {
            "content": "Great choice! Kamakhya Temple in Guwahati, Assam is one of India's most sacred Shakti Peethas! 🕉️\n\n**Perfect for spiritual travelers:**\n• Best time: October-March (pleasant weather)\n• Duration: 2-3 days ideal\n• Budget: ₹8,000-15,000 for 3 days\n• Also visit: Umananda Temple, Brahmaputra River cruise\n• Stay: Guwahati city hotels\n\nWould you like me to create a detailed itinerary with nearby attractions?",
            "agent": "🎯 Destination Expert"
        }
    
    elif any(word in message_lower for word in ["budget", "cost", "price", "money", "expensive", "cheap"]):
        return {
            "content": "I'll help you plan a budget-friendly trip! 💰\n\n**Budget planning factors:**\n• Destination choice (domestic vs international)\n• Season (peak vs off-season)\n• Accommodation level (budget/mid-range/luxury)\n• Transport mode (flight/train/road)\n• Trip duration\n\n**For India trips:**\n• Budget: ₹3,000-8,000/day\n• Mid-range: ₹8,000-20,000/day\n• Luxury: ₹20,000+/day\n\nTell me your destination and I'll give specific estimates!",
            "agent": "💰 Budget Analyst"
        }
    
    elif any(word in message_lower for word in ["days", "duration", "how long", "time"]):
        return {
            "content": "Great question about trip duration! 🗓️\n\n**Recommended durations:**\n• City break: 2-3 days\n• State exploration: 5-7 days\n• Regional tour: 10-14 days\n• Cross-country: 15+ days\n\n**For temple/spiritual trips:**\n• Single temple: 1-2 days\n• Temple circuit: 5-7 days\n• Pilgrimage tour: 10+ days\n\nWhat type of experience are you looking for? I can suggest the perfect duration!",
            "agent": "🗓️ Itinerary Planner"
        }
    
    elif any(word in message_lower for word in ["safe", "safety", "secure", "dangerous"]):
        return {
            "content": "Safety first! Let me help with travel safety info. 🛡️\n\n**General India travel safety:**\n• Register with local authorities if required\n• Carry ID and emergency contacts\n• Use registered taxis/transport\n• Stay in verified accommodations\n• Keep emergency numbers handy\n\n**For temple visits:**\n• Respect dress codes\n• Follow local customs\n• Be cautious of crowds during festivals\n• Secure your belongings\n\nWhich destination? I'll provide specific safety guidelines!",
            "agent": "🛡️ Safety Advisor"
        }
    
    elif any(word in message_lower for word in ["hello", "hi", "hey", "start"]):
        return {
            "content": "Hello! Welcome to your AI travel planning team! 👋\n\n**Meet your specialists:**\n🎯 **Destination Expert** - Perfect place recommendations\n💰 **Budget Analyst** - Smart money planning\n🗓️ **Itinerary Planner** - Day-by-day schedules\n🛡️ **Safety Advisor** - Travel safety & tips\n\n**I can help you with:**\n• Destination suggestions\n• Budget planning\n• Itinerary creation\n• Safety information\n• Local tips & recommendations\n\nWhat's your dream destination?",
            "agent": "🤖 Travel Assistant"
        }
    
    elif any(word in message_lower for word in ["itinerary", "plan", "schedule", "day"]):
        return {
            "content": "I'll help create the perfect itinerary! 🗓️\n\n**Tell me:**\n• Your destination\n• Number of days\n• Your interests (culture, adventure, food, etc.)\n• Budget range\n• Any specific places you want to visit\n\n**I'll create:**\n• Day-by-day detailed plans\n• Best times to visit attractions\n• Restaurant recommendations\n• Local transport options\n• Hidden gems and must-sees\n\nShall we start planning your perfect trip?",
            "agent": "🗓️ Itinerary Planner"
        }
    
    else:
        # Context-aware general response
        if "trip" in message_lower or "travel" in message_lower:
            return {
                "content": f"I understand you're interested in travel planning! 🌍\n\nYour message: \"{user_message}\"\n\n**I can help you with:**\n• Finding perfect destinations\n• Planning detailed itineraries\n• Budget optimization\n• Safety & travel tips\n\n**Popular questions:**\n• \"Suggest a 5-day trip under ₹20,000\"\n• \"Plan a spiritual tour of South India\"\n• \"Best time to visit Rajasthan?\"\n\nWhat would you like to explore?",
                "agent": "🤖 Travel Assistant"
            }
        else:
            return {
                "content": f"Thanks for your message! I'm your intelligent travel assistant. 🤖\n\nI noticed you mentioned: \"{user_message}\"\n\n**I specialize in:**\n• Destination recommendations\n• Itinerary planning\n• Budget analysis\n• Travel safety\n\n**Try asking:**\n• \"Plan a trip to Kerala\"\n• \"What's my budget for Goa?\"\n• \"5-day North India itinerary\"\n\nHow can I help plan your next adventure?",
                "agent": "🤖 Travel Assistant"
            }

def render_ai_chat_page():
    """Enhanced AI Chat with smart responses - Phase 3B"""
    st.header("💬 AI Travel Chat")
    st.info("🚀 **Phase 3B: Smart Contextual Chat** - Intelligent AI agents with context awareness")
    
    # Add context info
    if st.session_state.guest_mode:
        st.warning("🎯 **Guest Mode:** Conversations won't be saved permanently. Create an account to save chat history!")
    
    # Display messages with agent info
    for message in st.session_state.chat_messages:
        if message["sender"] == "user":
            timestamp = message.get("timestamp", datetime.now()).strftime("%H:%M") if isinstance(message.get("timestamp"), datetime) else "now"
            st.markdown(f"""
            <div style="background: #667eea; color: white; padding: 0.75rem; border-radius: 15px; margin: 0.5rem 0; margin-left: 25%; text-align: right; border-bottom-right-radius: 5px;">
                {message["content"]}
                <br><small style="opacity: 0.8; font-size: 0.8rem;">{timestamp}</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            agent = message.get("agent", "🤖 AI Assistant")
            timestamp = message.get("timestamp", datetime.now()).strftime("%H:%M") if isinstance(message.get("timestamp"), datetime) else "now"
            st.markdown(f"""
            <div style="background: white; border: 1px solid #e9ecef; padding: 0.75rem; border-radius: 15px; margin: 0.5rem 0; margin-right: 25%; border-bottom-left-radius: 5px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <strong style="color: #667eea;">{agent}</strong><br><br>
                {message["content"]}
                <br><small style="opacity: 0.6; font-size: 0.8rem;">{timestamp}</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Welcome message with smart intro
    if not st.session_state.chat_messages:
        welcome_response = get_smart_ai_response("hello")
        st.markdown(f"""
        <div style="background: white; border: 1px solid #e9ecef; padding: 0.75rem; border-radius: 15px; margin: 0.5rem 0; margin-right: 25%; border-bottom-left-radius: 5px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <strong style="color: #667eea;">{welcome_response["agent"]}</strong><br><br>
            {welcome_response["content"]}
        </div>
        """, unsafe_allow_html=True)
    
    # Smart quick replies based on conversation
    if st.session_state.chat_messages:
        last_message = st.session_state.chat_messages[-1]["content"].lower()
        
        st.markdown("### 💡 Quick Replies")
        
        if "kamakya" in last_message or "temple" in last_message:
            quick_replies = ["Create 3-day itinerary", "What's the budget?", "Best time to visit", "Nearby attractions"]
        elif "budget" in last_message:
            quick_replies = ["₹10,000 budget", "₹20,000 budget", "Luxury options", "Budget tips"]
        elif "duration" in last_message or "days" in last_message:
            quick_replies = ["3-day trip", "Week-long journey", "Extended tour", "Quick getaway"]
        else:
            quick_replies = ["Plan my trip", "Budget advice", "Best destinations", "Safety tips"]
        
        cols = st.columns(len(quick_replies))
        for i, reply in enumerate(quick_replies):
            with cols[i]:
                if st.button(reply, key=f"quick_{i}", use_container_width=True):
                    # Add user message
                    st.session_state.chat_messages.append({
                        "content": reply,
                        "sender": "user",
                        "timestamp": datetime.now()
                    })
                    
                    # Generate smart response
                    ai_response = get_smart_ai_response(reply)
                    st.session_state.chat_messages.append({
                        "content": ai_response["content"],
                        "sender": "ai",
                        "agent": ai_response["agent"],
                        "timestamp": datetime.now()
                    })
                    
                    st.rerun()
    else:
        # Initial quick replies
        st.markdown("### 🚀 Popular Questions")
        initial_replies = ["Plan temple tour", "Budget for Kerala", "Best time Rajasthan", "5-day North India"]
        
        cols = st.columns(len(initial_replies))
        for i, reply in enumerate(initial_replies):
            with cols[i]:
                if st.button(reply, key=f"initial_{i}", use_container_width=True):
                    # Add user message
                    st.session_state.chat_messages.append({
                        "content": reply,
                        "sender": "user",
                        "timestamp": datetime.now()
                    })
                    
                    # Generate smart response
                    ai_response = get_smart_ai_response(reply)
                    st.session_state.chat_messages.append({
                        "content": ai_response["content"],
                        "sender": "ai", 
                        "agent": ai_response["agent"],
                        "timestamp": datetime.now()
                    })
                    
                    st.rerun()
    
    # Enhanced chat input
    st.markdown("### 💬 Ask Your Travel Question")
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "Message", 
            key="chat_input", 
            placeholder="Ask about destinations, budgets, itineraries, or safety...",
            label_visibility="collapsed"
        )
    
    with col2:
        if st.button("Send", use_container_width=True, type="primary"):
            if user_input.strip():
                # Add user message
                st.session_state.chat_messages.append({
                    "content": user_input,
                    "sender": "user",
                    "timestamp": datetime.now()
                })
                
                # Generate smart contextual response
                with st.spinner("AI agents thinking..."):
                    ai_response = get_smart_ai_response(user_input)
                    st.session_state.chat_messages.append({
                        "content": ai_response["content"],
                        "sender": "ai",
                        "agent": ai_response["agent"],
                        "timestamp": datetime.now()
                    })
                
                st.rerun()
    
    # Chat actions
    st.markdown("---")
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()
    
    with col_b:
        if st.button("💾 Save Chat", use_container_width=True):
            if st.session_state.guest_mode:
                st.info("💡 Create an account to save conversations permanently!")
            else:
                st.success("🎉 Conversation saved to your history!")
    
    with col_c:
        if len(st.session_state.chat_messages) > 4:
            if st.button("📋 Create Trip Plan", use_container_width=True):
                st.info("🚀 Analyzing your conversation to generate a trip plan...")
                time.sleep(2)
                st.session_state.current_page = "✈️ Plan New Trip"
                st.rerun()

def render_trip_planning():
    st.header("🗺️ Plan Your Adventure")
    
    if st.session_state.guest_mode:
        st.info("🎯 **Guest Mode:** Your trip will be planned but not saved permanently.")
    
    with st.form("trip_form"):
        col_a, col_b = st.columns(2)
        with col_a:
            traveler_name = st.text_input("👤 Name", value=st.session_state.user_info.get('name', 'Traveler'))
            origin_city = st.text_input("🏙️ From", value="Hyderabad")
            destination = st.text_input("🎯 Destination (optional)", placeholder="Leave blank for AI suggestion")
            visa_passport = st.text_input("🛂 Passport", value="Indian")
        
        with col_b:
            days = st.slider("📅 Days", 1, 14, 5)
            month = st.selectbox("🗓️ Month", 
                ["January", "February", "March", "April", "May", "June",
                 "July", "August", "September", "October", "November", "December"], index=5)
            budget = st.number_input("💰 Budget (USD)", min_value=100.0, value=1500.0, step=100.0)
        
        interests = st.multiselect("🎯 Interests",
            ["beach", "mountains", "culture", "history", "food", "adventure", 
             "wildlife", "shopping", "nightlife", "relaxation", "photography",
             "museums", "temples", "nature"], default=["culture", "food"])
        
        if st.form_submit_button("🚀 Generate Trip Plan", use_container_width=True, type="primary"):
            if not interests:
                st.error("⚠️ Please select at least one interest!")
            else:
                with st.spinner("🤔 AI agents are working on your trip..."):
                    payload = {
                        "traveler_name": traveler_name,
                        "origin_city": origin_city,
                        "days": days,
                        "month": month,
                        "budget_total": budget,
                        "interests": interests,
                        "visa_passport": visa_passport,
                        "preferred_destination": destination
                    }
                    
                    if st.session_state.guest_mode:
                        try:
                            response = requests.post(f"{BACKEND_URL}/plan-guest",
                                                   json=payload, 
                                                   headers={"Content-Type": "application/json"},
                                                   timeout=60)
                        except:
                            st.error("🔌 Connection error. Please try again.")
                            return
                    else:
                        response = make_api_request("/plan", "POST", payload)
                    
                    if response and response.status_code == 200:
                        plan = response.json()
                        st.success("🎉 Your trip plan is ready!")
                        
                        # Display plan
                        st.subheader(f"✈️ Trip to {plan['destination']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"📅 **Duration:** {days} days")
                            st.write(f"🗓️ **Month:** {month}")
                            st.write(f"💰 **Budget:** ${budget}")
                        with col2:
                            st.write(f"🏙️ **From:** {origin_city}")
                            st.write(f"🎯 **Interests:** {', '.join(interests)}")
                        
                        # Show itinerary
                        st.subheader("🗓️ Your Itinerary")
                        for day in plan.get('itinerary', []):
                            with st.expander(f"Day {day['day']}: {day.get('title', 'Adventure Day')}"):
                                st.write(f"🌅 **Morning:** {day.get('morning', 'Start your day!')}")
                                st.write(f"☀️ **Afternoon:** {day.get('afternoon', 'Explore!')}")
                                st.write(f"🌙 **Evening:** {day.get('evening', 'Relax!')}")
                        
                    else:
                        st.error("❌ Error generating trip plan. Please try again.")

def render_trip_history():
    st.header("📚 Trip History")
    st.info("Trip history will show your saved adventures here.")

def render_settings():
    st.header("⚙️ Settings")
    st.info("Settings page - customize your preferences here.")

def main():
    if not st.session_state.authenticated:
        render_login_page()
        return
    
    page = render_sidebar()
    
    if page == "🏠 Dashboard":
        render_dashboard()
    elif page == "💬 AI Chat":
        render_ai_chat_page()
    elif page == "✈️ Plan New Trip":
        render_trip_planning()
    elif page == "📚 Trip History":
        render_trip_history()
    elif page == "⚙️ Settings":
        render_settings()

# Footer
st.markdown("""
<div style="background: #f8f9fa; border-radius: 10px; margin-top: 1rem; padding: 1rem; text-align: center;">
    <h4>🤖 Powered by Multi-Agent AI System - Phase 2</h4>
    <p>Authentication • Database • Multi-user Support • Guest Mode</p>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
