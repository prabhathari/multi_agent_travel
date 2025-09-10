import streamlit as st
import requests
import json
from datetime import datetime
import uuid
from typing import List, Dict
import asyncio


from typing import Dict, List, Any
import time

# Set page config
st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# COMPACT CENTERED CSS - IMPROVED VERSION
st.markdown("""
    <style>
    /* Main container - centered with max width */
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
    
    .stApp > div:first-child {
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Compact spacing */
    h1, h2, h3 { margin-top: 1rem !important; margin-bottom: 0.5rem !important; }
    
    /* Title section */
    .title-section {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 1rem;
    }
    
    .title-section h1 {
        font-size: 2.5rem;
        margin: 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Buttons */
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
    
    /* Guest section */
    .guest-section { max-width: 500px; margin: 1rem auto; text-align: center; }
    
    .guest-button > button {
        background: linear-gradient(90deg, #28a745 0%, #20c997 100%) !important;
        height: 2.8rem !important;
        font-size: 1.1rem !important;
    }
    
    /* User profiles */
    .user-profile, .guest-profile {
        padding: 1rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .user-profile { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .guest-profile { background: linear-gradient(135deg, #28a745 0%, #20c997 100%); }
    
    .user-avatar {
        width: 40px; height: 40px; border-radius: 50%;
        background: rgba(255,255,255,0.2);
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto 0.5rem; font-size: 16px; font-weight: bold;
    }
    
    /* Cards and metrics */
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
    
    .feature-cards {
        display: flex; gap: 1rem; margin: 1rem 0;
        flex-wrap: wrap; justify-content: center;
    }
    
    .feature-card {
        flex: 1; min-width: 250px; max-width: 300px;
        background: white; padding: 1rem; border-radius: 10px;
        text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Forms */
    .stForm {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 12px;
        max-width: 800px;
        margin: 1rem auto;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .center-content { max-width: 800px; margin: 0 auto; }
    
    /* Hide streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Footer */
    .footer-section {
        background: #f8f9fa; border-radius: 10px;
        margin-top: 1rem; padding: 1rem; text-align: center;
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .main { padding: 0.25rem 0.5rem; }
        .title-section h1 { font-size: 2rem; }
        .feature-cards { flex-direction: column; }
    }
    
    .stApp { background: #fafaba; }
    
    /* Phase 3A: Chat Interface Styles */
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        overflow: hidden;
    }

    .chat-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        text-align: center;
        border-radius: 15px 15px 0 0;
    }

    .message-bubble {
        margin: 0.75rem 0;
        max-width: 75%;
        padding: 0.75rem 1rem;
        border-radius: 15px;
        word-wrap: break-word;
        line-height: 1.4;
    }

    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: auto;
        text-align: right;
        border-bottom-right-radius: 5px;
    }

    .ai-message {
        background: white;
        color: #333;
        margin-right: auto;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
        border-bottom-left-radius: 5px;
    }

    .agent-avatar {
        display: inline-block;
        width: 28px;
        height: 28px;
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        border-radius: 50%;
        text-align: center;
        line-height: 28px;
        color: white;
        font-weight: bold;
        margin-right: 0.5rem;
        font-size: 0.8rem;
    }

    .destination-agent { background: linear-gradient(135deg, #ffc107 0%, #ff8c00 100%); }
    .budget-agent { background: linear-gradient(135deg, #28a745 0%, #20c997 100%); }
    .itinerary-agent { background: linear-gradient(135deg, #007bff 0%, #6610f2 100%); }
    .safety-agent { background: linear-gradient(135deg, #dc3545 0%, #fd7e14 100%); }

    .chat-messages-container {
        max-height: 400px;
        overflow-y: auto;
        padding: 1rem;
        background: #f8f9fa;
    }

    .quick-replies {
        padding: 0.5rem 1rem;
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        background: #f8f9fa;
    }

    .quick-reply-btn {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .quick-reply-btn:hover {
        background: #667eea;
        color: white;
        border-color: #667eea;
    }

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

# Helper functions (keep your existing ones)
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

# COMPACT LOGIN PAGE
def render_login_page():
    st.markdown("""
    <div class="title-section">
        <h1>✈️ AI Travel Planner</h1>
        <p>Phase 2 - Multi-user AI Travel Planning</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="guest-section"><h3>🚀 Quick Start</h3></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="guest-button">', unsafe_allow_html=True)
        if st.button("🎯 Continue as Guest", use_container_width=True):
            login_as_guest()
            st.success("🎉 Welcome, Guest!")
            time.sleep(1)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<p style='text-align: center; color: #666; font-size: 0.9rem; margin: 0.5rem 0;'><em>Guest mode: Plan trips without registration</em></p>", unsafe_allow_html=True)
    st.markdown('<hr style="margin: 1rem 0; border: none; height: 1px; background: linear-gradient(90deg, transparent, #ddd, transparent);">', unsafe_allow_html=True)
    
    st.markdown('<div class="center-content">', unsafe_allow_html=True)
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
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Compact features
    st.markdown("### ✨ Features")
    st.markdown("""
    <div class="feature-cards">
        <div class="feature-card">
            <h4>🤖 AI Agents</h4>
            <p>4 specialized AI agents plan your trip</p>
        </div>
        <div class="feature-card">
            <h4>💾 Save Trips</h4>
            <p>Account users save trips permanently</p>
        </div>
        <div class="feature-card">
            <h4>🎯 Smart Planning</h4>
            <p>Budget-aware with safety insights</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

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

def render_trip_planning():
    """Render trip planning page with full API integration"""
    st.header("🗺️ Plan Your Next Adventure")
    
    if st.session_state.guest_mode:
        st.info("🎯 **Guest Mode:** Your trip will be planned but not saved permanently. Create an account to save your trips!")
    
    # Default preferences
    default_prefs = {
        "origin_city": "Hyderabad",
        "favorite_interests": ["culture", "food"],
        "preferred_budget": 1500
    }
    
    if not st.session_state.guest_mode:
        # Load user preferences for authenticated users
        prefs_response = make_api_request("/auth/preferences")
        if prefs_response and prefs_response.status_code == 200:
            default_prefs.update(prefs_response.json())
    
    with st.form("trip_form"):
        st.subheader("📝 Trip Details")
        
        col_a, col_b = st.columns(2)
        with col_a:
            traveler_name = st.text_input("👤 Your Name", value=st.session_state.user_info.get('name', 'Traveler'))
            origin_city = st.text_input("🏙️ Origin City", value=default_prefs.get('origin_city', 'Hyderabad'))
            destination_override = st.text_input("🎯 Preferred Destination (optional)", placeholder="Leave blank for AI suggestion")
            visa_passport = st.text_input("🛂 Passport Nationality", value="Indian")
        
        with col_b:
            days = st.slider("📅 Trip Duration (days)", 1, 14, 5)
            month = st.selectbox("🗓️ Travel Month", 
                ["January", "February", "March", "April", "May", "June",
                 "July", "August", "September", "October", "November", "December"],
                index=5)  # Default to June
            budget_total = st.number_input("💰 Total Budget (USD)", 
                                         min_value=100.0, 
                                         value=float(default_prefs.get('preferred_budget', 1500)), 
                                         step=100.0)
        
        st.subheader("🎯 What interests you?")
        interests = st.multiselect(
            "Select your interests",
            ["beach", "mountains", "culture", "history", "food", "adventure", 
             "wildlife", "shopping", "nightlife", "relaxation", "photography",
             "museums", "temples", "nature", "city tour", "festivals", "art"],
            default=default_prefs.get('favorite_interests', ["culture", "food"])
        )
        
        submitted = st.form_submit_button("🚀 Generate Travel Plan", use_container_width=True, type="primary")
    
    # Process form submission
    if submitted:
        if not interests:
            st.error("⚠️ Please select at least one interest!")
        else:
            with st.spinner("🤔 AI agents are collaborating on your perfect trip..."):
                payload = {
                    "traveler_name": traveler_name,
                    "origin_city": origin_city,
                    "days": days,
                    "month": month,
                    "budget_total": budget_total,
                    "interests": interests,
                    "visa_passport": visa_passport,
                    "preferred_destination": destination_override
                }
                
                if st.session_state.guest_mode:
                    # For guest mode, make request without authentication
                    try:
                        response = requests.post(f"{BACKEND_URL}/plan-guest",
                                               json=payload,
                                               headers={"Content-Type": "application/json"},
                                               timeout=60)
                    except:
                        st.error("🔌 Cannot connect to the backend. Please try again.")
                        return
                else:
                    # For authenticated users
                    response = make_api_request("/plan", "POST", payload)
                
                if response and response.status_code == 200:
                    plan = response.json()
                    st.success("🎉 Your amazing trip plan is ready!")
                    
                    # Store trip data
                    trip_record = {
                        'id': f"trip_{len(st.session_state.guest_trips) + 1}",
                        'created_at': datetime.now().isoformat(),
                        'traveler_name': traveler_name,
                        'destination': plan['destination'],
                        'origin_city': origin_city,
                        'days': days,
                        'month': month,
                        'budget_total': budget_total,
                        'interests': interests,
                        'trip_data': plan
                    }
                    
                    if st.session_state.guest_mode:
                        st.session_state.guest_trips.append(trip_record)
                        st.session_state.user_trips = st.session_state.guest_trips
                    else:
                        # Reload user data for authenticated users
                        load_user_data()
                    
                    # Display the plan
                    display_trip_plan(plan)
                    
                elif response:
                    try:
                        error_msg = response.json().get("detail", "Failed to generate trip plan")
                        if response.status_code == 401:
                            st.error("🔐 Session expired. Please log in again.")
                            logout_user()
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {error_msg}")
                    except:
                        st.error(f"❌ Error: HTTP {response.status_code}")
                else:
                    st.error("🔌 Cannot connect to the backend API.")

def display_trip_plan(plan):
    """Display the complete trip plan with improved layout"""
    
    st.markdown("---")
    st.header("🎯 Your Perfect Trip Plan")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📍 Destination", 
        "🗓️ Itinerary", 
        "💰 Budget", 
        "🛡️ Safety", 
        "💭 Feedback"
    ])
    
    with tab1:
        st.subheader(f"🎯 Perfect Match: {plan['destination']}")
        dest_info = plan['destination_info']
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"**Why this destination?** {dest_info.get('reason', 'AI selected this based on your preferences!')}")
            
            if 'highlights' in dest_info:
                st.markdown("### ✨ Must-See Highlights")
                for i, highlight in enumerate(dest_info['highlights'], 1):
                    st.write(f"🌟 **{i}.** {highlight}")
        
        with col2:
            st.markdown("### 📊 Quick Info")
            st.metric("🌟 AI Score", "9.2/10")
            st.metric("🌡️ Weather", "Perfect")
            st.metric("💸 Cost Level", "Moderate")
    
    with tab2:
        st.subheader("🗓️ Your Perfect Itinerary")
        
        for day_plan in plan['itinerary']:
            with st.expander(f"📅 Day {day_plan['day']}: {day_plan.get('title', 'Adventure Day!')}", expanded=True):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown("**🌅 Morning**")
                    st.write(day_plan.get('morning', 'Start your adventure!'))
                    
                    st.markdown("**☀️ Afternoon**") 
                    st.write(day_plan.get('afternoon', 'Explore amazing places'))
                    
                    st.markdown("**🌙 Evening**")
                    st.write(day_plan.get('evening', 'Relax and enjoy dinner'))
                
                with col2:
                    st.markdown("**🍽️ Food Recommendations**")
                    for meal in day_plan.get('meal_suggestions', ['Local specialties']):
                        st.write(f"• {meal}")
    
    with tab3:
        st.subheader("💰 Smart Budget Breakdown")
        
        budget_analysis = plan['budget_analysis']
        breakdown = budget_analysis.get('breakdown', {})
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 💵 Cost Categories")
            for category, amount in breakdown.items():
                percentage = (amount / sum(breakdown.values())) * 100 if breakdown.values() else 0
                st.metric(
                    category.replace('_', ' ').title(),
                    f"${amount:.2f}",
                    f"{percentage:.1f}% of total"
                )
        
        with col2:
            st.markdown("### 📊 Budget Summary")
            total = budget_analysis.get('total', 0)
            daily_avg = budget_analysis.get('daily_average', 0)
            
            st.metric("💰 Total Cost", f"${total:.2f}")
            st.metric("📅 Per Day", f"${daily_avg:.2f}")
            
            if plan.get('within_budget', True):
                st.success("✅ Perfect! Within your budget!")
            else:
                st.warning("⚠️ Slightly over budget, but worth it!")
            
            if 'budget_tips' in budget_analysis:
                st.markdown("**💡 Money-Saving Tips:**")
                for tip in budget_analysis['budget_tips']:
                    st.write(f"💡 {tip}")
    
    with tab4:
        st.subheader("🛡️ Safety & Travel Guide")
        safety = plan['safety_info']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🚨 Safety Overview")
            safety_level = safety.get('safety_level', 'Unknown')
            
            if safety_level.lower() == 'low':
                st.success(f"🟢 **Safety Level:** {safety_level} - Very Safe!")
            elif safety_level.lower() == 'medium':
                st.warning(f"🟡 **Safety Level:** {safety_level} - Generally Safe")
            else:
                st.error(f"🔴 **Safety Level:** {safety_level} - Extra Caution Needed")
            
            visa_required = safety.get('visa_required', False)
            if visa_required:
                st.info("🛂 **Visa Required:** Yes - Apply in advance!")
            else:
                st.success("🛂 **Visa Required:** No - Easy travel!")
        
        with col2:
            st.markdown("### 💉 Health & Emergency")
            
            if 'vaccinations' in safety:
                st.markdown("**Recommended Vaccinations:**")
                for vac in safety['vaccinations']:
                    st.write(f"💉 {vac}")
            
            if 'emergency_contacts' in safety:
                st.markdown("**📞 Emergency Numbers:**")
                for service, number in safety['emergency_contacts'].items():
                    st.write(f"📞 **{service.title()}:** {number}")
        
        if 'safety_tips' in safety:
            st.markdown("### ⚠️ Essential Safety Tips")
            for i, tip in enumerate(safety['safety_tips'], 1):
                st.write(f"{i}. {tip}")
    
    with tab5:
        st.subheader("💭 Rate Your Trip Plan")
        
        col1, col2 = st.columns(2)
        
        with col1:
            rating = st.select_slider(
                "How amazing is this plan?",
                options=[1, 2, 3, 4, 5],
                value=5,
                format_func=lambda x: "⭐" * x + f" ({x}/5)"
            )
            
            feedback_comment = st.text_area("Any suggestions or comments?")
            
            if st.button("📝 Submit Feedback", use_container_width=True):
                if st.session_state.guest_mode:
                    st.info("💡 Feedback noted! Create an account to save feedback permanently.")
                else:
                    st.success("🎉 Thank you for your feedback!")
                st.balloons()
        
        with col2:
            st.markdown("### 🤖 AI Agent Process")
            for msg in plan['agent_messages']:
                st.info(f"**{msg['agent']}:** {msg['content']}")

def load_user_data():
    """Load user trips and statistics"""
    if st.session_state.guest_mode:
        # For guest mode, use session data
        st.session_state.user_trips = st.session_state.guest_trips
        st.session_state.user_stats = {
            "total_trips": len(st.session_state.guest_trips),
            "total_budget": sum([trip.get("budget_total", 0) for trip in st.session_state.guest_trips]),
            "average_rating": 4.5,
            "favorite_destinations": [],
            "user": st.session_state.user_info
        }
        return
    
    # Load trips for authenticated users
    response = make_api_request("/trips")
    if response and response.status_code == 200:
        data = response.json()
        st.session_state.user_trips = data.get("trips", [])
    
    # Load stats
    response = make_api_request("/stats")
    if response and response.status_code == 200:
        st.session_state.user_stats = response.json()
def render_trip_history():
    """Render trip history page with improved layout"""
    st.header("📚 Your Trip History")
    
    if st.session_state.guest_mode:
        st.info("🎯 **Guest Mode:** Showing trips from this session only. Create an account to save trips permanently!")
    
    if not st.session_state.user_trips:
        load_user_data()
    
    trips = st.session_state.user_trips
    
    if not trips:
        # Empty state with action
        st.markdown("""
        <div class="dashboard-card">
            <h3>🗺️ No Adventures Yet!</h3>
            <p>Start planning your first amazing trip!</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("✈️ Plan Your First Trip", use_container_width=True, type="primary"):
                st.session_state.current_page = "✈️ Plan New Trip"
                st.rerun()
    else:
        st.write(f"📊 Showing {len(trips)} trip{'s' if len(trips) != 1 else ''}")
        
        # Display trips
        for i, trip in enumerate(reversed(trips)):
            created_date = datetime.fromisoformat(trip.get('created_at', '2024-01-01T00:00:00')).strftime('%b %d, %Y')
            
            with st.expander(f"✈️ {trip.get('destination', 'Unknown')} - {trip.get('month', '')} ({created_date})", expanded=False):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**🏙️ Origin:** {trip.get('origin_city', 'Unknown')}")
                    st.write(f"**📅 Duration:** {trip.get('days', 0)} days")
                    st.write(f"**💰 Budget:** ${trip.get('budget_total', 0):.2f}")
                    st.write(f"**🎯 Interests:** {', '.join(trip.get('interests', []))}")
                
                with col2:
                    if st.button("📊 View Details", key=f"view_{i}", use_container_width=True):
                        if 'trip_data' in trip:
                            st.session_state.viewing_plan = trip['trip_data']
                            st.rerun()
                
                with col3:
                    st.write(f"**📅 Created:** {created_date}")
                    if st.session_state.guest_mode:
                        st.caption("🎯 Session data only")
        
        # Display selected plan
        if hasattr(st.session_state, 'viewing_plan'):
            st.markdown("---")
            st.header("📋 Trip Plan Details")
            plan = st.session_state.viewing_plan
            
            # Show basic trip info
            st.subheader(f"✈️ Trip to {plan['destination']}")
            
            col1, col2 = st.columns(2)
            with col1:
                dest_info = plan.get('destination_info', {})
                st.write(f"**📍 Destination:** {plan['destination']}")
                if 'reason' in dest_info:
                    st.write(f"**💭 Why this place:** {dest_info['reason']}")
            with col2:
                if plan.get('within_budget'):
                    st.success("✅ Within Budget")
                else:
                    st.warning("⚠️ Slightly Over Budget")
            
            # Show itinerary
            st.subheader("🗓️ Daily Itinerary")
            for day in plan.get('itinerary', []):
                with st.expander(f"Day {day['day']}: {day.get('title', 'Adventure Day')}", expanded=False):
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.write(f"🌅 **Morning:** {day.get('morning', 'Start your day!')}")
                        st.write(f"☀️ **Afternoon:** {day.get('afternoon', 'Explore!')}")
                        st.write(f"🌙 **Evening:** {day.get('evening', 'Relax!')}")
                    with col_b:
                        st.write("**🍽️ Food:**")
                        for meal in day.get('meal_suggestions', ['Local cuisine']):
                            st.write(f"• {meal}")
            
            # Show budget
            if 'budget_analysis' in plan:
                st.subheader("💰 Budget Analysis")
                budget_data = plan['budget_analysis']
                if 'breakdown' in budget_data:
                    col_x, col_y = st.columns(2)
                    with col_x:
                        for category, amount in list(budget_data['breakdown'].items())[:3]:
                            st.metric(category.replace('_', ' ').title(), f"${amount:.2f}")
                    with col_y:
                        for category, amount in list(budget_data['breakdown'].items())[3:]:
                            st.metric(category.replace('_', ' ').title(), f"${amount:.2f}")
            
            # Close button
            if st.button("❌ Close Details", type="secondary"):
                del st.session_state.viewing_plan
                st.rerun()

def render_settings():
    st.header("⚙️ Settings")
    st.info("Settings page - customize your preferences here.")



# Phase 3A: Chat Interface Functions
def init_chat_session():
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'chat_session_id' not in st.session_state:
        st.session_state.chat_session_id = str(uuid.uuid4())
    if 'current_agent' not in st.session_state:
        st.session_state.current_agent = "assistant"

def get_agent_info(agent_type):
    """Get agent avatar and name"""
    agents = {
        "assistant": {"avatar": "🤖", "name": "Travel Assistant", "class": ""},
        "destination": {"avatar": "🎯", "name": "Destination Expert", "class": "destination-agent"},
        "budget": {"avatar": "💰", "name": "Budget Analyst", "class": "budget-agent"},
        "itinerary": {"avatar": "🗓️", "name": "Itinerary Planner", "class": "itinerary-agent"},
        "safety": {"avatar": "🛡️", "name": "Safety Advisor", "class": "safety-agent"}
    }
    return agents.get(agent_type, agents["assistant"])

def add_chat_message(content, sender="user", agent_type="assistant"):
    """Add a message to chat history"""
    message = {
        "id": str(uuid.uuid4()),
        "content": content,
        "sender": sender,
        "agent_type": agent_type,
        "timestamp": datetime.now().isoformat()
    }
    st.session_state.chat_messages.append(message)

def display_chat_messages():
    """Display all chat messages"""
    for message in st.session_state.chat_messages:
        if message["sender"] == "user":
            st.markdown(f"""
            <div class="message-bubble user-message">
                {message["content"]}
                <br><small style="opacity: 0.8; font-size: 0.8rem;">
                    {datetime.fromisoformat(message["timestamp"]).strftime("%I:%M %p")}
                </small>
            </div>
            """, unsafe_allow_html=True)
        else:
            agent_info = get_agent_info(message["agent_type"])
            st.markdown(f"""
            <div class="message-bubble ai-message">
                <span class="agent-avatar {agent_info['class']}">{agent_info['avatar']}</span>
                <strong>{agent_info['name']}</strong>
                <br><br>
                {message["content"]}
                <br><small style="opacity: 0.6; font-size: 0.8rem;">
                    {datetime.fromisoformat(message["timestamp"]).strftime("%I:%M %p")}
                </small>
            </div>
            """, unsafe_allow_html=True)

def process_chat_message(user_message: str):
    """Process user message and return AI response"""
    message_lower = user_message.lower()
    
    # Simple intent detection for Phase 3A
    if any(word in message_lower for word in ["go", "visit", "travel", "trip", "destination"]):
        agent_type = "destination"
        content = f"Great choice! I can help you find the perfect destination. 🎯\n\n"
        
        if any(country in message_lower for country in ["japan", "tokyo", "kyoto"]):
            content += "Japan is incredible! Cherry blossoms in spring, amazing food, rich culture. Let me get our budget analyst involved for cost planning.\n\n"
        elif any(country in message_lower for country in ["europe", "paris", "london", "italy"]):
            content += "Europe offers incredible diversity! From Paris's romance to Italy's cuisine to London's history. What draws you to Europe?\n\n"
        else:
            content += "What type of experience interests you? Adventure, culture, relaxation, food scenes?\n\n"
        
        content += "Tell me about your budget and timeframe!"
    
    elif any(word in message_lower for word in ["budget", "cost", "price", "$", "expensive"]):
        agent_type = "budget"
        content = "Perfect! Let me help with budget planning! 💰\n\n"
        content += "I can break down costs for:\n"
        content += "• ✈️ Flights\n• 🏨 Accommodation\n• 🍽️ Food & drinks\n• 🎯 Activities\n• 🚌 Local transport\n\n"
        content += "What's your total budget and destination?"
    
    elif any(word in message_lower for word in ["days", "weeks", "duration"]):
        agent_type = "itinerary"
        content = "Time planning is key! 🗓️\n\n"
        content += "I recommend:\n• 3-5 days: City exploration\n• 1 week: Country highlights\n• 2+ weeks: Multi-destination\n\n"
        content += "How many days do you have and where to?"
    
    elif any(word in message_lower for word in ["safe", "visa", "passport"]):
        agent_type = "safety"
        content = "Safety first! 🛡️\n\n"
        content += "I provide:\n• Visa requirements\n• Safety ratings\n• Health recommendations\n• Emergency contacts\n\n"
        content += "Which destination and what's your passport country?"
    
    else:
        agent_type = "assistant"
        if any(word in message_lower for word in ["hello", "hi", "hey"]):
            content = "Hello! Welcome to your AI travel team! 👋\n\n"
            content += "Meet your specialists:\n🎯 Destination Expert\n💰 Budget Analyst\n🗓️ Itinerary Planner\n🛡️ Safety Advisor\n\n"
            content += "Just tell me your travel dreams!"
        else:
            content = "I'm here to help plan your perfect trip! 🌍\n\n"
            content += "Share with me:\n• Where you want to go\n• Your budget range\n• How many days\n• What you love doing\n\n"
            content += "Let's create something amazing!"
    
    return {"content": content, "agent": agent_type}

def get_quick_replies():
    """Get contextual quick reply suggestions"""
    if not st.session_state.chat_messages:
        return ["I want to visit Japan", "Europe trip", "$2000 budget", "7-day vacation"]
    
    last_message = st.session_state.chat_messages[-1]["content"].lower()
    
    if "budget" in last_message:
        return ["$1000-2000", "$2000-4000", "$4000+", "I'm flexible"]
    elif "destination" in last_message:
        return ["Asia", "Europe", "Americas", "Surprise me!"]
    elif "days" in last_message:
        return ["Weekend (3-4 days)", "1 week", "2 weeks", "1 month"]
    else:
        return ["Tell me more", "Sounds perfect!", "What about costs?", "Other options?"]

def render_chat_interface():
    """Render the main chat interface - Phase 3A"""
    init_chat_session()
    
    # Chat header
    st.markdown("""
    <div class="chat-container">
        <div class="chat-header">
            <h2 style="margin: 0;">💬 Chat with AI Travel Agents</h2>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Plan your perfect trip through conversation</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Welcome message if new chat
    if not st.session_state.chat_messages:
        add_chat_message(
            "Hi! I'm your AI travel assistant with a team of specialists! 🌍\n\n"
            "🎯 **Destination Expert** - finds amazing places\n"
            "💰 **Budget Analyst** - manages your money\n"
            "🗓️ **Itinerary Planner** - creates daily plans\n"
            "🛡️ **Safety Advisor** - keeps you safe\n\n"
            "Just tell me about your dream trip and we'll make it happen! Where would you like to go?",
            sender="ai",
            agent_type="assistant"
        )
    
    # Chat messages
    st.markdown('<div class="chat-messages-container">', unsafe_allow_html=True)
    display_chat_messages()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    st.markdown("### 💬 Your Message")
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "Message",
            key="chat_input",
            placeholder="Where would you like to travel?",
            label_visibility="collapsed"
        )
    
    with col2:
        send_clicked = st.button("Send", use_container_width=True, type="primary")
    
    # Process user input
    if send_clicked and user_input.strip():
        # Add user message
        add_chat_message(user_input, sender="user")
        
        # Get AI response
        with st.spinner("AI thinking..."):
            time.sleep(1)  # Simulate thinking time
            ai_response = process_chat_message(user_input)
            add_chat_message(ai_response["content"], sender="ai", agent_type=ai_response["agent"])
        
        # Clear input and rerun
        st.rerun()
    
    # Quick replies
    if st.session_state.chat_messages:
        st.markdown("### 💡 Quick Replies")
        quick_replies = get_quick_replies()
        
        cols = st.columns(len(quick_replies))
        for i, reply in enumerate(quick_replies):
            with cols[i]:
                if st.button(reply, key=f"quick_{i}", use_container_width=True):
                    add_chat_message(reply, sender="user")
                    ai_response = process_chat_message(reply)
                    add_chat_message(ai_response["content"], sender="ai", agent_type=ai_response["agent"])
                    st.rerun()
    
    # Chat actions
    st.markdown("---")
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_messages = []
            st.rerun()
    
    with col_b:
        if st.button("💾 Save Chat"):
            st.success("Chat saved! (Phase 3B: will save to history)")
    
    with col_c:
        if len(st.session_state.chat_messages) > 4:
            if st.button("📋 Create Trip Plan"):
                st.info("🚀 Phase 3B: Will generate trip plan from chat!")

def render_ai_chat_page():
    """Main chat page renderer"""
    st.header("💬 AI Travel Chat - Phase 3A")
    
    if st.session_state.guest_mode:
        st.info("🎯 **Guest Mode:** Chat history won't be saved permanently. Create an account to save conversations!")
    
    render_chat_interface()

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
<div class="footer-section">
    <h4>🤖 Powered by Multi-Agent AI System - Phase 2</h4>
    <p>Authentication • Database • Multi-user Support • Guest Mode</p>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
