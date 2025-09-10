import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, List, Any
import time

# Set page config
st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for Phase 2
st.markdown("""
    <style>
    .main { padding: 2rem; }
    
    /* Login/Signup styling */
    .login-container {
        max-width: 400px;
        margin: 2rem auto;
        padding: 2rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 20px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Guest button styling */
    .guest-button > button {
        background: linear-gradient(90deg, #28a745 0%, #20c997 100%) !important;
        border: none !important;
    }
    
    /* Metrics styling */
    div[data-testid="metric-container"] {
        background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* User profile styling */
    .user-profile {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .guest-profile {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .user-avatar {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: rgba(255,255,255,0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1rem auto;
        font-size: 24px;
        font-weight: bold;
    }
    
    /* Trip cards */
    .trip-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
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

# Helper functions for API calls
def make_api_request(endpoint, method="GET", data=None, auth_required=True):
    """Make authenticated API request with proper error handling"""
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
    except requests.exceptions.Timeout:
        st.error("Request timed out. Please try again.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the backend. Please check your connection.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Network error: {str(e)}")
        return None

def login_user(email, password):
    """Login user and store token with improved error handling"""
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login", 
                               json={"email": email, "password": password},
                               headers={"Content-Type": "application/json"},
                               timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.access_token = data["access_token"]
            st.session_state.user_info = data["user"]
            st.session_state.authenticated = True
            st.session_state.guest_mode = False
            return True, "Login successful!"
        else:
            try:
                error_detail = response.json().get("detail", f"HTTP {response.status_code}")
            except:
                error_detail = f"Login failed with status {response.status_code}"
            return False, error_detail
            
    except requests.exceptions.Timeout:
        return False, "Request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to server. Please check if the backend is running."
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def signup_user(email, name, password, origin_city="Hyderabad"):
    """Sign up new user with improved error handling"""
    try:
        response = requests.post(f"{BACKEND_URL}/auth/signup",
                               json={
                                   "email": email,
                                   "name": name,
                                   "password": password,
                                   "origin_city": origin_city
                               },
                               headers={"Content-Type": "application/json"},
                               timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.access_token = data["access_token"]
            st.session_state.user_info = data["user"]
            st.session_state.authenticated = True
            st.session_state.guest_mode = False
            return True, "Account created successfully!"
        else:
            try:
                error_detail = response.json().get("detail", f"HTTP {response.status_code}")
            except:
                error_detail = f"Signup failed with status {response.status_code}"
            return False, error_detail
            
    except requests.exceptions.Timeout:
        return False, "Request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to server. Please check if the backend is running."
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def login_as_guest():
    """Enable guest mode without authentication"""
    st.session_state.authenticated = True
    st.session_state.guest_mode = True
    st.session_state.access_token = None
    st.session_state.user_info = {
        "name": "Guest User",
        "email": "guest@example.com",
        "id": "guest",
        "created_at": datetime.now().isoformat()
    }
    st.session_state.user_stats = {
        "total_trips": len(st.session_state.guest_trips),
        "total_budget": sum([trip.get("budget_total", 0) for trip in st.session_state.guest_trips]),
        "average_rating": 4.5,
        "favorite_destinations": [],
        "user": st.session_state.user_info
    }

def logout_user():
    """Logout user and clear session"""
    if st.session_state.access_token and not st.session_state.guest_mode:
        make_api_request("/auth/logout", "POST")
    
    st.session_state.authenticated = False
    st.session_state.guest_mode = False
    st.session_state.access_token = None
    st.session_state.user_info = None
    st.session_state.user_trips = []
    st.session_state.user_stats = {}
    st.session_state.guest_trips = []

def load_user_data():
    """Load user trips and statistics"""
    if st.session_state.guest_mode:
        # For guest mode, use session data
        st.session_state.user_trips = st.session_state.guest_trips
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

def render_login_page():
    """Render login/signup page with guest option"""
    st.title("AI Travel Planner - Phase 2")
    st.markdown("### Multi-user travel planning with AI agents")
    
    # Guest login option at the top
    st.markdown("### Quick Start")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎯 Continue as Guest", use_container_width=True, key="guest_btn"):
            login_as_guest()
            st.success("Welcome, Guest! You can plan trips without creating an account.")
            st.rerun()
    
    st.markdown("*Guest mode: Plan trips without registration (data won't be saved permanently)*")
    
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
    
    with tab1:
        st.markdown("### Welcome Back!")
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("🔑 Login", use_container_width=True)
            
            if submitted:
                if email and password:
                    with st.spinner("Logging in..."):
                        success, message = login_user(email, password)
                        if success:
                            st.success(message)
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(message)
                else:
                    st.error("Please fill in all fields")
    
    with tab2:
        st.markdown("### Create Your Account")
        
        with st.form("signup_form"):
            name = st.text_input("Full Name", placeholder="John Doe")
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password", help="Minimum 6 characters")
            origin_city = st.text_input("Home City", value="Hyderabad")
            submitted = st.form_submit_button("📝 Create Account", use_container_width=True)
            
            if submitted:
                if name and email and password:
                    if len(password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        with st.spinner("Creating account..."):
                            success, message = signup_user(email, name, password, origin_city)
                            if success:
                                st.success(message)
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(message)
                else:
                    st.error("Please fill in all fields")
    
    # Demo info
    st.markdown("---")
    st.info("💡 **New to the platform?** Try guest mode for quick testing, or create an account to save your trips permanently!")

def render_sidebar():
    """Render authenticated user sidebar"""
    with st.sidebar:
        # User profile
        if st.session_state.user_info:
            user = st.session_state.user_info
            profile_class = "guest-profile" if st.session_state.guest_mode else "user-profile"
            
            st.markdown(f"""
            <div class="{profile_class}">
                <div class="user-avatar">{user['name'][0].upper()}</div>
                <h3>{user['name']}</h3>
                <p>{user['email']}</p>
                {'<small>🎯 Guest Mode - Data not saved</small>' if st.session_state.guest_mode else ''}
            </div>
            """, unsafe_allow_html=True)
        
        # Quick stats
        if st.session_state.user_stats:
            stats = st.session_state.user_stats
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Trips", stats.get('total_trips', 0))
            with col2:
                st.metric("Rating", f"{stats.get('average_rating', 0):.1f}/5")
            
            if stats.get('total_budget', 0) > 0:
                st.metric("Total Spent", f"${stats.get('total_budget', 0):.0f}")
        
        # Navigation
        st.markdown("---")
        page = st.radio(
            "**Navigation**",
            ["🏠 Dashboard", "✈️ Plan New Trip", "📚 Trip History", "⚙️ Settings"],
            key="nav_radio"
        )
        
        # Account options
        st.markdown("---")
        if st.session_state.guest_mode:
            if st.button("👤 Create Account", use_container_width=True):
                logout_user()
                st.rerun()
        
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.rerun()
        
        return page

def render_dashboard():
    """Render user dashboard"""
    st.header("📊 Your Travel Dashboard")
    
    if not st.session_state.user_stats:
        load_user_data()
    
    stats = st.session_state.user_stats
    
    if stats.get('total_trips', 0) == 0:
        if st.session_state.guest_mode:
            st.info("🗺️ Welcome, Guest! Start planning your adventure below. Note: Trip data won't be saved permanently in guest mode.")
        else:
            st.info("🗺️ No trips planned yet! Start your first adventure below.")
        
        if st.button("✈️ Plan Your First Trip", use_container_width=True):
            # st.session_state.nav_radio = "✈️ Plan New Trip"
            st.rerun()
    else:
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("✈️ Total Adventures", stats.get('total_trips', 0))
        with col2:
            st.metric("💵 Money Spent", f"${stats.get('total_budget', 0):.0f}")
        with col3:
            avg_rating = stats.get('average_rating', 0)
            st.metric("⭐ Avg Rating", f"{avg_rating:.1f}/5")
        with col4:
            if st.session_state.guest_mode:
                st.metric("👤 Mode", "Guest")
            else:
                member_since = datetime.fromisoformat(stats['user']['member_since']).strftime('%b %Y')
                st.metric("📅 Member Since", member_since)
        
        # Favorite destinations
        st.subheader("🗺️ Your Favorite Destinations")
        fav_destinations = stats.get('favorite_destinations', [])
        if fav_destinations:
            for dest, count in fav_destinations:
                st.write(f"📍 **{dest}** - {count} trip{'s' if count > 1 else ''}")
        else:
            st.info("Plan more trips to see your favorites!")

def render_trip_planning():
    """Render trip planning page"""
    st.header("🗺️ Plan Your Next Adventure")
    
    if st.session_state.guest_mode:
        st.info("🎯 **Guest Mode:** Your trip will be planned but not saved permanently. Create an account to save your trips!")
    
    # Default preferences (guest mode or from API)
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
            traveler_name = st.text_input("Your Name", value=st.session_state.user_info.get('name', 'Traveler'))
            origin_city = st.text_input("Origin City", value=default_prefs.get('origin_city', 'Hyderabad'))
            destination_override = st.text_input("Preferred Destination (optional)", placeholder="Leave blank for AI suggestion")
            visa_passport = st.text_input("Passport Nationality", value="Indian")
        
        with col_b:
            days = st.slider("Trip Duration (days)", 1, 14, 5)
            month = st.selectbox("Travel Month", 
                ["January", "February", "March", "April", "May", "June",
                 "July", "August", "September", "October", "November", "December"],
                index=8)
            budget_total = st.number_input("Total Budget (USD)", 
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
        
        submitted = st.form_submit_button("🚀 Generate Travel Plan", use_container_width=True)
    
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
                        st.error("Cannot connect to the backend. Please try again.")
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
    """Display the complete trip plan"""
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📍 Destination", 
        "🗓️ Itinerary", 
        "💰 Budget", 
        "🛡️ Safety", 
        "💭 Feedback"
    ])
    
    with tab1:
        st.header(f"🎯 Perfect Match: {plan['destination']}")
        dest_info = plan['destination_info']
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"**Why this destination?** {dest_info.get('reason', 'AI selected this based on your preferences!')}")
            
            if 'highlights' in dest_info:
                st.subheader("✨ Must-See Highlights")
                for i, highlight in enumerate(dest_info['highlights'], 1):
                    st.write(f"🌟 **{i}.** {highlight}")
        
        with col2:
            st.subheader("📊 Quick Info")
            st.metric("🌟 AI Score", "9.2/10")
            st.metric("🌡️ Weather", "Perfect")
            st.metric("💸 Cost Level", "Moderate")
    
    with tab2:
        st.header("🗓️ Your Perfect Itinerary")
        
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
        st.header("💰 Smart Budget Breakdown")
        
        budget_analysis = plan['budget_analysis']
        breakdown = budget_analysis.get('breakdown', {})
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("💵 Cost Categories")
            for category, amount in breakdown.items():
                percentage = (amount / sum(breakdown.values())) * 100 if breakdown.values() else 0
                st.metric(
                    category.replace('_', ' ').title(),
                    f"${amount:.2f}",
                    f"{percentage:.1f}% of total"
                )
        
        with col2:
            st.subheader("📊 Budget Summary")
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
        st.header("🛡️ Safety & Travel Guide")
        safety = plan['safety_info']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🚨 Safety Overview")
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
            st.subheader("💉 Health & Emergency")
            
            if 'vaccinations' in safety:
                st.markdown("**Recommended Vaccinations:**")
                for vac in safety['vaccinations']:
                    st.write(f"💉 {vac}")
            
            if 'emergency_contacts' in safety:
                st.markdown("**📞 Emergency Numbers:**")
                for service, number in safety['emergency_contacts'].items():
                    st.write(f"📞 **{service.title()}:** {number}")
        
        if 'safety_tips' in safety:
            st.subheader("⚠️ Essential Safety Tips")
            for i, tip in enumerate(safety['safety_tips'], 1):
                st.write(f"{i}. {tip}")
    
    with tab5:
        st.header("💭 Rate Your Trip Plan")
        
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
            st.subheader("🤖 AI Agent Process")
            for msg in plan['agent_messages']:
                st.info(f"**{msg['agent']}:** {msg['content']}")

def render_trip_history():
    """Render trip history page"""
    st.header("📚 Your Trip History")
    
    if st.session_state.guest_mode:
        st.info("🎯 **Guest Mode:** Showing trips from this session only. Create an account to save trips permanently!")
    
    if not st.session_state.user_trips:
        load_user_data()
    
    trips = st.session_state.user_trips
    
    if not trips:
        msg = "🗺️ No trips in this session yet!" if st.session_state.guest_mode else "🗺️ No trips planned yet!"
        st.info(msg + " Start your first adventure.")
        if st.button("✈️ Plan Your First Trip"):
            st.session_state.nav_radio = "✈️ Plan New Trip"
            st.rerun()
    else:
        st.write(f"📊 Showing {len(trips)} trip{'s' if len(trips) != 1 else ''}")
        
        # Display trips
        for i, trip in enumerate(reversed(trips)):
            created_date = datetime.fromisoformat(trip.get('created_at', '2024-01-01T00:00:00')).strftime('%b %Y')
            with st.expander(f"✈️ {trip.get('destination', 'Unknown')} - {trip.get('month', '')} ({created_date})", expanded=False):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**🏙️ Origin:** {trip.get('origin_city', 'Unknown')}")
                    st.write(f"**📅 Duration:** {trip.get('days', 0)} days")
                    st.write(f"**💰 Budget:** ${trip.get('budget_total', 0):.2f}")
                    st.write(f"**🎯 Interests:** {', '.join(trip.get('interests', []))}")
                
                with col2:
                    if st.button("📊 View Full Plan", key=f"view_{i}"):
                        if 'trip_data' in trip:
                            st.session_state.viewing_plan = trip['trip_data']
                
                with col3:
                    st.write(f"**📅 Created:** {created_date}")
                    if st.session_state.guest_mode:
                        st.caption("Session data only")
        
        # Display selected plan
        if hasattr(st.session_state, 'viewing_plan'):
            st.markdown("---")
            st.header("📋 Trip Plan Details")
            display_trip_plan(st.session_state.viewing_plan)
            if st.button("❌ Close Plan View"):
                del st.session_state.viewing_plan
                st.rerun()

def render_settings():
    """Render settings page"""
    st.header("⚙️ Settings & Preferences")
    
    if st.session_state.guest_mode:
        st.info("🎯 **Guest Mode:** Settings are temporary. Create an account to save preferences permanently!")
        
        # Guest mode simple preferences
        with st.form("guest_settings_form"):
            st.subheader("🎯 Session Preferences")
            
            col1, col2 = st.columns(2)
            with col1:
                origin_city = st.text_input("Default Origin City", value="Hyderabad")
                preferred_budget = st.number_input("Preferred Budget Range (USD)", 
                                                 min_value=100, 
                                                 value=1500,
                                                 step=100)
            
            with col2:
                favorite_interests = st.multiselect(
                    "Favorite Interests",
                    ["beach", "mountains", "culture", "history", "food", "adventure", 
                     "wildlife", "shopping", "nightlife", "relaxation", "photography",
                     "museums", "temples", "nature", "city tour"],
                    default=["culture", "food"]
                )
            
            if st.form_submit_button("💾 Save Session Preferences", use_container_width=True):
                st.success("✅ Session preferences saved!")
        
        # Account creation prompt
        st.markdown("---")
        st.subheader("🚀 Ready to Save Your Data?")
        st.write("Create an account to:")
        st.write("• Save trips permanently")
        st.write("• Access trip history across devices")
        st.write("• Get personalized recommendations")
        
        if st.button("👤 Create Account Now", use_container_width=True):
            logout_user()
            st.rerun()
    
    else:
        # Authenticated user settings
        # Load current preferences
        prefs_response = make_api_request("/auth/preferences")
        current_prefs = {}
        if prefs_response and prefs_response.status_code == 200:
            current_prefs = prefs_response.json()
        
        with st.form("settings_form"):
            st.subheader("🎯 Travel Preferences")
            
            col1, col2 = st.columns(2)
            with col1:
                origin_city = st.text_input("Default Origin City", value=current_prefs.get('origin_city', 'Hyderabad'))
                preferred_budget = st.number_input("Preferred Budget Range (USD)", 
                                                 min_value=100, 
                                                 value=int(current_prefs.get('preferred_budget', 1500)),
                                                 step=100)
            
            with col2:
                favorite_interests = st.multiselect(
                    "Favorite Interests",
                    ["beach", "mountains", "culture", "history", "food", "adventure", 
                     "wildlife", "shopping", "nightlife", "relaxation", "photography",
                     "museums", "temples", "nature", "city tour"],
                    default=current_prefs.get('favorite_interests', ["culture", "food"])
                )
            
            if st.form_submit_button("💾 Save Settings", use_container_width=True):
                update_data = {
                    "origin_city": origin_city,
                    "preferred_budget": preferred_budget,
                    "favorite_interests": favorite_interests
                }
                
                response = make_api_request("/auth/preferences", "PUT", update_data)
                if response and response.status_code == 200:
                    st.success("✅ Settings saved successfully!")
                else:
                    st.error("❌ Failed to save settings")
        
        # Account info
        st.subheader("👤 Account Information")
        if st.session_state.user_info:
            user = st.session_state.user_info
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Name:** {user['name']}")
                st.write(f"**Email:** {user['email']}")
            with col2:
                st.write(f"**Member Since:** {datetime.fromisoformat(user['created_at']).strftime('%B %Y')}")
                st.write(f"**Status:** {'Active' if user.get('is_active', True) else 'Inactive'}")

def main():
    """Main application logic"""
    
    # Check authentication
    if not st.session_state.authenticated:
        render_login_page()
        return
    
    # Load user data on first load
    if not st.session_state.user_trips and not st.session_state.user_stats:
        load_user_data()
    
    # Render sidebar and get current page
    page = render_sidebar()
    
    # Route to appropriate page
    if page == "🏠 Dashboard":
        render_dashboard()
    elif page == "✈️ Plan New Trip":
        render_trip_planning()
    elif page == "📚 Trip History":
        render_trip_history()
    elif page == "⚙️ Settings":
        render_settings()

# Enhanced footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <h4>🤖 Powered by Multi-Agent AI System - Phase 2</h4>
    <p>Authentication • Database • Multi-user Support • Guest Mode</p>
    <p style='font-size: 0.8em;'>✨ Complete AI Travel Planning Platform ✨</p>
</div>
""", unsafe_allow_html=True)

# Run the main application
if __name__ == "__main__":
    main()
