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
    initial_sidebar_state="auto"  # Changed from "expanded" to "auto" for mobile
)

# Enhanced CSS with FIXED chat alignment
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
    
    /* FIXED CHAT ALIGNMENT */
    .chat-container {
        max-height: 400px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        background: #f8f9fa;
    }
    
    .user-message {
        display: flex;
        justify-content: flex-end;
        margin: 0.5rem 0;
    }
    
    .ai-message {
        display: flex;
        justify-content: flex-start;
        margin: 0.5rem 0;
    }
    
    .message-bubble-user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 18px;
        border-bottom-right-radius: 5px;
        max-width: 70%;
        word-wrap: break-word;
    }
    
    .message-bubble-ai {
        background: white;
        color: #333;
        padding: 0.75rem 1rem;
        border-radius: 18px;
        border-bottom-left-radius: 5px;
        max-width: 70%;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        word-wrap: break-word;
    }
    
    .agent-badge {
        font-size: 0.75rem;
        color: #667eea;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }
    
    /* TRIP CARDS */
    .trip-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .budget-card {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .safety-card {
        background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .itinerary-card {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
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
    
    .stForm {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem auto;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* TAB CONTENT HEIGHT LIMIT */
    .tab-content {
        max-height: 500px;
        overflow-y: auto;
        padding: 1rem;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp { background: #fafafa; }
    

    <style>
    /* MOBILE RESPONSIVE FIXES */
    @media screen and (max-width: 768px) {
        .main { 
            padding: 0.25rem 0.5rem !important; 
            max-width: 100% !important;
            margin: 0 !important;
        }
        
        .block-container {
            padding-top: 0.25rem !important;
            padding-bottom: 0.25rem !important;
            max-width: 100% !important;
            margin: 0 !important;
        }
        
        .stButton > button {
            height: 3rem !important;
            font-size: 1rem !important;
        }
        
        .trip-card {
            padding: 1rem !important;
            margin: 0.5rem 0 !important;
        }
        
        .budget-card, .safety-card {
            padding: 0.75rem !important;
            margin: 0.25rem 0 !important;
        }
        
        .user-message, .ai-message {
            max-width: 85% !important;
        }
        
        .message-bubble-user, .message-bubble-ai {
            max-width: 100% !important;
            font-size: 0.9rem !important;
        }
        
        .chat-container {
            max-height: 300px !important;
        }
        
        .stForm {
            padding: 1rem !important;
            margin: 0.5rem 0 !important;
        }
        
        .stSelectbox > div > div {
            font-size: 0.9rem !important;
        }
        
        .stTextInput > div > div > input {
            font-size: 0.9rem !important;
        }
    }
    
    /* GENERAL MOBILE OPTIMIZATIONS */
    @media screen and (max-width: 480px) {
        .main { 
            padding: 0.1rem 0.25rem !important; 
        }
        
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.3rem !important; }
        h3 { font-size: 1.1rem !important; }
        
        .trip-card h1 { font-size: 1.4rem !important; }
        .trip-card p { font-size: 0.9rem !important; }
        
        .budget-card h2, .safety-card h2 {
            font-size: 1.2rem !important;
        }
    }
    
    /* PREVENT HORIZONTAL SCROLL */
    html, body {
        overflow-x: hidden !important;
        max-width: 100% !important;
    }
    
    .stApp {
        background: #fafafa !important;
        max-width: 100% !important;
        overflow-x: hidden !important;
    }
    
    /* FIX STREAMLIT SIDEBAR ON MOBILE */
    @media screen and (max-width: 768px) {
        .css-1d391kg {
            width: 100% !important;
        }
    }
    </style>
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
if 'current_page' not in st.session_state:
    st.session_state.current_page = "🏠 Dashboard"
if 'current_trip_plan' not in st.session_state:
    st.session_state.current_trip_plan = None
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'show_chat_modal' not in st.session_state:
    st.session_state.show_chat_modal = False
if 'user_trips' not in st.session_state:
    st.session_state.user_trips = []
if 'guest_trips' not in st.session_state:
    st.session_state.guest_trips = []
if 'chat_input_key' not in st.session_state:
    st.session_state.chat_input_key = 0

# Helper functions (keeping existing ones)
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
    st.session_state.current_trip_plan = None
    st.session_state.show_chat_modal = False

def save_trip_to_storage(trip_plan, trip_request):
    """Save trip to appropriate storage"""
    trip_data = {
        "id": str(uuid.uuid4()),
        "title": f"{trip_request['days']}-day trip to {trip_plan['destination']}",
        "destination": trip_plan['destination'],
        "origin_city": trip_request['origin_city'],
        "days": trip_request['days'],
        "month": trip_request['month'],
        "budget_total": trip_request['budget_total'],
        "interests": trip_request['interests'],
        "created_at": datetime.now().isoformat(),
        "trip_data": trip_plan
    }
    
    if st.session_state.guest_mode:
        st.session_state.guest_trips.insert(0, trip_data)
        st.session_state.guest_trips = st.session_state.guest_trips[:10]
    
    return trip_data

# REAL LLM CHAT FUNCTION (working version)
def get_llm_response(user_message, trip_context=None):
    """Call REAL backend LLM API for intelligent responses"""
    
    try:
        payload = {
            "message": user_message,
            "trip_context": trip_context
        }
        
        if st.session_state.guest_mode:
            endpoint = "/chat-guest"
            headers = {"Content-Type": "application/json"}
        else:
            endpoint = "/chat"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {st.session_state.access_token}"
            }
        
        response = requests.post(
            f"{BACKEND_URL}{endpoint}",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "Sorry, I could not generate a response.")
        elif response.status_code == 429:
            return "Rate limit reached. Please wait a moment before asking another question!"
        else:
            return f"AI having technical difficulties. Please try again! Error: {response.status_code}"
    
    except requests.exceptions.Timeout:
        return "Request timeout. The AI is taking longer than usual to respond. Please try again!"
    except requests.exceptions.ConnectionError:
        return "Connection error. Please check your connection and try again!"
    except Exception as e:
        return f"AI error: {str(e)}. Please try again!"

# FIXED CHAT MODAL with proper alignment
def render_floating_chat():
    """Render floating chat with FIXED message alignment"""
    
    # Show chat modal if activated
    if st.session_state.show_chat_modal:
        with st.container():
            st.markdown("### 💬 AI Travel Assistant")
            
            # Chat messages container with fixed alignment
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            
            # Welcome message
            if not st.session_state.chat_messages and st.session_state.current_trip_plan:
                destination = st.session_state.current_trip_plan.get('destination', 'your destination')
                st.markdown(f"""
                <div class="ai-message">
                    <div class="message-bubble-ai">
                        <div class="agent-badge">🤖 AI Assistant</div>
                        🎉 Great! Your trip to <strong>{destination}</strong> is ready!<br><br>
                        I can answer any questions about your personalized plan. What would you like to know?
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Display chat messages with FIXED alignment
            for message in st.session_state.chat_messages:
                if message.get("type") == "user" or message.get("sender") == "user":
                    st.markdown(f"""
                    <div class="user-message">
                        <div class="message-bubble-user">
                            {message["content"]}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    agent = message.get("agent", "🤖 AI Assistant")
                    content = message["content"].replace('\n', '<br>')
                    st.markdown(f"""
                    <div class="ai-message">
                        <div class="message-bubble-ai">
                            <div class="agent-badge">{agent}</div>
                            {content}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Quick questions if we have a trip
            if st.session_state.current_trip_plan:
                st.markdown("**💡 Quick Questions:**")
                col1, col2, col3 = st.columns(3)
                
                quick_questions = [
                    "What's my budget?",
                    "Show itinerary", 
                    "Safety info"
                ]
                
                for i, question in enumerate(quick_questions):
                    with [col1, col2, col3][i]:
                        if st.button(question, key=f"quick_{i}", use_container_width=True):
                            # Add user message
                            st.session_state.chat_messages.append({
                                "type": "user",
                                "content": question,
                                "timestamp": datetime.now()
                            })
                            
                            # Generate response
                            with st.spinner("🤖 AI thinking..."):
                                ai_response = get_llm_response(question, st.session_state.current_trip_plan)
                            
                            st.session_state.chat_messages.append({
                                "type": "ai",
                                "content": ai_response,
                                "agent": "🤖 AI Assistant",
                                "timestamp": datetime.now()
                            })
                            
                            st.rerun()
            
            # Chat input
            st.markdown("---")
            col1, col2 = st.columns([4, 1])
            
            with col1:
                user_input = st.text_input(
                    "Ask about your trip...", 
                    key=f"chat_input_{st.session_state.chat_input_key}",
                    placeholder="e.g., What's my budget breakdown?",
                    label_visibility="collapsed"
                )
            
            with col2:
                if st.button("Send", key="send_chat", use_container_width=True):
                    if user_input.strip():
                        # Add user message
                        st.session_state.chat_messages.append({
                            "type": "user",
                            "content": user_input,
                            "timestamp": datetime.now()
                        })
                        
                        # Generate response
                        with st.spinner("🤖 AI thinking..."):
                            ai_response = get_llm_response(user_input, st.session_state.current_trip_plan)
                        
                        st.session_state.chat_messages.append({
                            "type": "ai",
                            "content": ai_response,
                            "agent": "🤖 AI Assistant",
                            "timestamp": datetime.now()
                        })
                        
                        # Clear input and refresh
                        st.session_state.chat_input_key += 1
                        st.rerun()
            
            # Chat controls
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("🗑️ Clear Chat", key="clear_chat"):
                    st.session_state.chat_messages = []
                    st.rerun()
            
            with col_b:
                if st.button("❌ Close Chat", key="close_chat"):
                    st.session_state.show_chat_modal = False
                    st.rerun()

# Login page (keeping existing)
def render_login_page():
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="font-size: 2.5rem; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">✈️ AI Travel Planner</h1>
        <p style="font-size: 1rem; color: #666; margin: 0.5rem 0;">Complete Multi-Agent Travel Planning</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎯 Continue as Guest", use_container_width=True):
            login_as_guest()
            st.success("🎉 Welcome, Guest!")
            time.sleep(1)
            st.rerun()
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("📧 Email", placeholder="demo@example.com")
            password = st.text_input("🔒 Password", type="password", placeholder="demo123")
            
            if st.form_submit_button("🔑 Login", use_container_width=True):
                if email and password:
                    success, message = login_user(email, password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

# Sidebar (keeping existing)
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
        nav_options = ["🏠 Dashboard", "✈️ Plan New Trip", "📚 Trip History", "⚙️ Settings"]
        
        for option in nav_options:
            if st.button(option, use_container_width=True, 
                        key=f"nav_{option}", 
                        type="primary" if st.session_state.current_page == option else "secondary"):
                st.session_state.current_page = option
                st.rerun()
        
        st.markdown("---")
        
        # Chat button in sidebar
        if st.button("💬 AI Chat Assistant", use_container_width=True, type="secondary"):
            st.session_state.show_chat_modal = not st.session_state.show_chat_modal
            st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.rerun()
        
        return st.session_state.current_page

# Dashboard
def render_dashboard():
    st.header("📊 Your Travel Dashboard")
    
    if st.session_state.current_trip_plan:
        plan = st.session_state.current_trip_plan
        st.markdown(f"""
        <div class="trip-card">
            <h3>🎯 Latest Trip: {plan.get('destination', 'Unknown')}</h3>
            <p>Your personalized travel plan is ready! Use the AI chat for questions.</p>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✈️ Plan Your Trip", use_container_width=True, type="primary"):
            st.session_state.current_page = "✈️ Plan New Trip"
            st.rerun()

# TRIP PLANNING WITH TABS (Fixed vertical scrolling)
def render_enhanced_trip_planning():
    """Trip planning with TABS instead of long vertical sections"""
    st.header("🗺️ Plan Your Adventure")
    
    if st.session_state.guest_mode:
        st.info("🎯 **Guest Mode:** Your trip will be planned but not saved permanently.")
    
    # Trip planning form
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
        
        form_submitted = st.form_submit_button("🚀 Generate Trip Plan", use_container_width=True, type="primary")
        
        if form_submitted:
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
                    
                    # API call
                    if st.session_state.guest_mode:
                        try:
                            response = requests.post(f"{BACKEND_URL}/plan-guest",
                                                   json=payload, 
                                                   headers={"Content-Type": "application/json"},
                                                   timeout=60)
                        except:
                            st.error("🔌 Connection error. Please try again.")
                            st.stop()
                    else:
                        response = make_api_request("/plan", "POST", payload)
                    
                    if response and response.status_code == 200:
                        plan = response.json()
                        
                        # Store the plan
                        st.session_state.current_trip_plan = plan
                        
                        # Save to storage
                        save_trip_to_storage(plan, payload)
                        
                        st.success("🎉 Your trip plan is ready!")
                        st.balloons()
                        
                    else:
                        st.error("❌ Error generating trip plan. Please try again.")

    # DISPLAY TRIP WITH TABS (Fixed vertical scrolling!)
    if st.session_state.current_trip_plan:
        plan = st.session_state.current_trip_plan
        
        st.markdown("---")
        
        # MAIN TRIP HEADER
        st.markdown(f"""
        <div class="trip-card">
            <h1 style="margin: 0; color: white;">✈️ Your Trip to {plan['destination']}</h1>
            <p style="margin: 0.5rem 0; font-size: 1.1rem; opacity: 0.9;">Complete AI-generated travel plan</p>
        </div>
        """, unsafe_allow_html=True)
        
        # TRIP SUMMARY CARDS (always visible)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            budget_info = plan.get('budget_analysis', {})
            total_cost = budget_info.get('total', 0)
            within_budget = plan.get('within_budget', True)
            budget_status = "Within Budget ✅" if within_budget else "Over Budget ⚠️"
            
            st.markdown(f"""
            <div class="budget-card">
                <h3 style="margin: 0; color: white;">💰 Budget</h3>
                <h2 style="margin: 0.5rem 0; color: white;">${total_cost:,.2f}</h2>
                <p style="margin: 0; font-size: 0.9rem;">{budget_status}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            itinerary = plan.get('itinerary', [])
            safety_info = plan.get('safety_info', {})
            safety_level = safety_info.get('safety_level', 'Medium')
            
            st.markdown(f"""
            <div class="safety-card">
                <h3 style="margin: 0; color: white;">🛡️ Safety</h3>
                <h2 style="margin: 0.5rem 0; color: white;">{safety_level} Risk</h2>
                <p style="margin: 0; font-size: 0.9rem;">{len(itinerary)} Days Planned</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            highlights = plan.get('destination_info', {}).get('highlights', [])
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #6f42c1 0%, #e83e8c 100%); color: white; padding: 1rem; border-radius: 10px; text-align: center;">
                <h3 style="margin: 0; color: white;">🎯 Highlights</h3>
                <h2 style="margin: 0.5rem 0; color: white;">{len(highlights)}</h2>
                <p style="margin: 0; font-size: 0.9rem;">Must-See Places</p>
            </div>
            """, unsafe_allow_html=True)
        
        # TABS INSTEAD OF VERTICAL SECTIONS (Fixed!)
        tab1, tab2, tab3, tab4 = st.tabs(["🗓️ Itinerary", "💰 Budget", "🛡️ Safety", "🎯 Destination"])
        
        with tab1:
            st.markdown('<div class="tab-content">', unsafe_allow_html=True)
            if itinerary:
                for day in itinerary:
                    st.markdown(f"""
                    <div class="itinerary-card">
                        <h4 style="margin: 0; color: #667eea;">Day {day.get('day', 1)}: {day.get('title', 'Adventure Day')}</h4>
                        <p style="margin: 0.5rem 0;"><strong>🌅 Morning:</strong> {day.get('morning', 'Start your day!')}</p>
                        <p style="margin: 0.5rem 0;"><strong>☀️ Afternoon:</strong> {day.get('afternoon', 'Explore!')}</p>
                        <p style="margin: 0.5rem 0;"><strong>🌙 Evening:</strong> {day.get('evening', 'Relax!')}</p>
                        {f'<p style="margin: 0.5rem 0;"><strong>🍽️ Recommended:</strong> {", ".join(day["meal_suggestions"][:2])}</p>' if day.get('meal_suggestions') else ''}
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div class="tab-content">', unsafe_allow_html=True)
            budget_breakdown = budget_info.get('breakdown', {})
            
            if budget_breakdown:
                col1, col2 = st.columns(2)
                
                with col1:
                    for category, amount in list(budget_breakdown.items())[:3]:
                        percentage = (amount / total_cost * 100) if total_cost > 0 else 0
                        st.write(f"**{category.title()}:** ${amount:,.2f} ({percentage:.0f}%)")
                
                with col2:
                    for category, amount in list(budget_breakdown.items())[3:]:
                        percentage = (amount / total_cost * 100) if total_cost > 0 else 0
                        st.write(f"**{category.title()}:** ${amount:,.2f} ({percentage:.0f}%)")
                
                daily_avg = budget_info.get('daily_average', total_cost / max(len(itinerary), 1))
                st.info(f"📊 **Daily Average:** ${daily_avg:,.2f} per day")
                
                # Budget tips
                tips = budget_info.get('budget_tips', [])
                if tips:
                    st.write("**💡 Money-Saving Tips:**")
                    for tip in tips:
                        st.write(f"• {tip}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab3:
            st.markdown('<div class="tab-content">', unsafe_allow_html=True)
            if safety_info:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Safety Level:** {safety_info.get('safety_level', 'Medium')}")
                    st.write(f"**Visa Required:** {'Yes' if safety_info.get('visa_required', False) else 'No'}")
                    
                    vaccinations = safety_info.get('vaccinations', [])
                    if vaccinations:
                        st.write("**Vaccinations:**")
                        for vaccine in vaccinations[:3]:
                            st.write(f"• {vaccine}")
                
                with col2:
                    tips = safety_info.get('safety_tips', [])
                    if tips:
                        st.write("**Safety Tips:**")
                        for tip in tips[:4]:
                            st.write(f"• {tip}")
                    
                    weather = safety_info.get('weather_advisory', '')
                    if weather:
                        st.write(f"**Weather:** {weather}")
                
                # Emergency contacts
                emergency = safety_info.get('emergency_contacts', {})
                if emergency:
                    st.write("**🚨 Emergency Contacts:**")
                    for service, number in emergency.items():
                        st.write(f"• {service.title()}: {number}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab4:
            st.markdown('<div class="tab-content">', unsafe_allow_html=True)
            dest_info = plan.get('destination_info', {})
            if dest_info:
                reason = dest_info.get('reason', '')
                if reason:
                    st.write(f"**Why {plan['destination']}:** {reason}")
                
                highlights = dest_info.get('highlights', [])
                if highlights:
                    st.write("**Top Highlights:**")
                    for highlight in highlights:
                        st.write(f"• {highlight}")
                
                # Agent messages
                agent_messages = plan.get('agent_messages', [])
                if agent_messages:
                    st.write("**🤖 AI Agent Insights:**")
                    for msg in agent_messages:
                        agent_name = msg.get('agent', 'Unknown Agent')
                        content = msg.get('content', 'No details available')
                        st.write(f"**{agent_name}:** {content}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # AI CHAT INTEGRATION (below tabs)
        st.markdown("---")
        st.subheader("💬 Ask AI About Your Trip")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.info("🤖 **Use the AI assistant to get detailed information about your trip!**")
            st.write("Ask about specific days, budget details, safety concerns, or local recommendations.")
        
        with col2:
            if st.button("💬 Open AI Chat", use_container_width=True, type="primary"):
                st.session_state.show_chat_modal = True
                st.rerun()

# Trip History (keeping existing)
def render_trip_history():
    st.header("📚 Trip History")
    
    if st.session_state.guest_mode:
        trips = st.session_state.guest_trips
        st.info("🎯 **Guest Mode:** Showing session trips. Create an account to save permanently!")
    else:
        response = make_api_request("/trips")
        if response and response.status_code == 200:
            data = response.json()
            trips = data.get("trips", [])
        else:
            trips = []
    
    if trips:
        st.write(f"📋 **Total Trips:** {len(trips)}")
        
        for trip in trips:
            with st.expander(f"✈️ {trip.get('title', 'Unknown Trip')}", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"🎯 **Destination:** {trip.get('destination', 'Unknown')}")
                    st.write(f"📅 **Duration:** {trip.get('days', 0)} days")
                    st.write(f"💰 **Budget:** ${trip.get('budget_total', 0):,.2f}")
                
                with col2:
                    st.write(f"🏙️ **From:** {trip.get('origin_city', 'Unknown')}")
                    st.write(f"🗓️ **Month:** {trip.get('month', 'Unknown')}")
                    st.write(f"📅 **Created:** {trip.get('created_at', 'Unknown')[:10]}")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(f"🔄 Reload Trip", key=f"reload_{trip.get('id', 'unknown')}"):
                        st.session_state.current_trip_plan = trip.get('trip_data', {})
                        st.session_state.current_page = "✈️ Plan New Trip"
                        st.success(f"✅ Loaded trip to {trip.get('destination')}!")
                        st.rerun()
                
                with col_b:
                    if st.button(f"💬 Ask AI About This Trip", key=f"chat_{trip.get('id', 'unknown')}"):
                        st.session_state.current_trip_plan = trip.get('trip_data', {})
                        st.session_state.show_chat_modal = True
                        st.rerun()
    else:
        st.info("🗺️ No trips yet! Plan your first adventure.")
        
        if st.button("✈️ Plan Your First Trip", use_container_width=True):
            st.session_state.current_page = "✈️ Plan New Trip"
            st.rerun()

# Settings (keeping existing)
def render_settings():
    st.header("⚙️ Settings")
    
    if st.session_state.guest_mode:
        st.info("🎯 **Guest Mode:** Limited settings available.")
    
    st.markdown("### 🤖 AI Assistant")
    st.checkbox("🔔 Enable chat notifications", value=True)
    st.selectbox("🎨 Chat theme", ["Default", "Dark", "Colorful"], index=0)
    
    st.markdown("### 🎨 App Preferences")
    col1, col2 = st.columns(2)
    
    with col1:
        st.selectbox("🌍 Default Origin", ["Hyderabad", "Mumbai", "Delhi", "Bangalore"], index=0)
        st.multiselect("❤️ Favorite Interests", 
                      ["culture", "food", "adventure", "beaches", "mountains"], 
                      default=["culture", "food"])
    
    with col2:
        st.number_input("💰 Default Budget", min_value=100, value=1500, step=100)
        st.selectbox("💬 AI Response Length", ["Concise", "Detailed", "Very Detailed"], index=1)
    
    if st.session_state.guest_mode:
        if st.button("🗑️ Clear All Data", type="secondary"):
            st.session_state.guest_trips = []
            st.session_state.current_trip_plan = None
            st.session_state.chat_messages = []
            st.success("✅ All data cleared!")

# Main application
def main():
    if not st.session_state.authenticated:
        render_login_page()
        return
    
    page = render_sidebar()
    
    if page == "🏠 Dashboard":
        render_dashboard()
    elif page == "✈️ Plan New Trip":
        render_enhanced_trip_planning()
    elif page == "📚 Trip History":
        render_trip_history()
    elif page == "⚙️ Settings":
        render_settings()
    
    # Always render the chat modal if it's open
    if st.session_state.show_chat_modal:
        render_floating_chat()

# Footer
st.markdown("""
<div style="background: #f8f9fa; border-radius: 10px; margin-top: 2rem; padding: 1rem; text-align: center;">
    <h4>🤖 Complete Multi-Agent Travel Planning System</h4>
    <p>✨ Fixed Chat Alignment • Tabbed Layout • No Vertical Scrolling</p>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
