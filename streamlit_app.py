import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, List, Any
import time
import uuid
import base64
from io import BytesIO

# PDF generation imports
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    st.warning("PDF export not available. Install reportlab: pip install reportlab")

# Set page config with mobile-friendly settings
st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"  # Collapsed for mobile
)

# Simplified, mobile-friendly CSS
st.markdown("""
    <style>
    /* Reset and mobile-first approach */
    * {
        box-sizing: border-box;
    }
    
    /* Main container adjustments */
    .main {
        padding: 0.5rem !important;
        max-width: 100% !important;
    }
    
    .block-container {
        padding: 0.5rem !important;
        max-width: 100% !important;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Simple button styling */
    .stButton > button {
        border-radius: 20px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border: none;
        font-weight: 600;
        width: 100%;
    }
    
    /* Message styles for chat */
    .user-msg {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.75rem;
        border-radius: 15px;
        border-bottom-right-radius: 5px;
        margin: 0.5rem 0;
        text-align: right;
    }
    
    .ai-msg {
        background: #f0f2f6;
        color: #333;
        padding: 0.75rem;
        border-radius: 15px;
        border-bottom-left-radius: 5px;
        margin: 0.5rem 0;
    }
    
    /* Trip card */
    .trip-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
    }
    
    /* Info cards */
    .info-card {
        background: white;
        border: 1px solid #e0e0e0;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    /* Mobile responsive adjustments */
    @media (max-width: 768px) {
        .main, .block-container {
            padding: 0.25rem !important;
        }
        
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.3rem !important; }
        h3 { font-size: 1.1rem !important; }
        
        .stButton > button {
            font-size: 0.9rem !important;
            padding: 0.5rem !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Configuration
BACKEND_URL = "http://backend:8000"

# Initialize session state
def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        'authenticated': False,
        'guest_mode': False,
        'access_token': None,
        'user_info': None,
        'current_page': "Dashboard",
        'current_trip_plan': None,
        'current_trip_request': None,
        'chat_messages': [],
        'show_chat': False,
        'guest_trips': [],
        'chat_input_counter': 0
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# Helper Functions
def make_api_request(endpoint, method="GET", data=None, auth_required=True):
    """Make API request to backend"""
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
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

def login_user(email, password):
    """Login user"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={"email": email.strip().lower(), "password": password},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.access_token = data["access_token"]
            st.session_state.user_info = data["user"]
            st.session_state.authenticated = True
            st.session_state.guest_mode = False
            return True, "✅ Login successful!"
        else:
            return False, "❌ Invalid credentials"
    except Exception as e:
        return False, f"❌ Connection error: {str(e)}"

def signup_user(email, name, password, origin_city="Hyderabad"):
    """Signup new user"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/signup",
            json={
                "email": email.strip().lower(),
                "name": name.strip(),
                "password": password,
                "origin_city": origin_city
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.access_token = data["access_token"]
            st.session_state.user_info = data["user"]
            st.session_state.authenticated = True
            st.session_state.guest_mode = False
            return True, "🎉 Account created!"
        else:
            return False, "❌ Account creation failed"
    except Exception as e:
        return False, f"❌ Connection error: {str(e)}"

def login_as_guest():
    """Login as guest"""
    st.session_state.authenticated = True
    st.session_state.guest_mode = True
    st.session_state.user_info = {"name": "Guest User", "email": "guest@example.com"}

def logout_user():
    """Logout user"""
    if st.session_state.access_token and not st.session_state.guest_mode:
        make_api_request("/auth/logout", "POST")
    
    # Reset session state
    init_session_state()
    st.session_state.authenticated = False
    st.session_state.guest_mode = False

def get_llm_response(user_message, trip_context=None):
    """Get response from LLM chat API"""
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
            return data.get("response", "Sorry, I couldn't generate a response.")
        elif response.status_code == 429:
            return "⏳ Rate limit reached. Please wait a moment before asking another question."
        else:
            return "🤖 AI is having technical difficulties. Please try again!"
            
    except requests.exceptions.Timeout:
        return "⏱️ Request timeout. Please try again!"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def generate_trip_pdf(trip_plan, trip_request):
    """Generate PDF for trip plan"""
    if not REPORTLAB_AVAILABLE:
        return None
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#764ba2'),
        spaceAfter=12
    )
    
    # Title
    elements.append(Paragraph(f"Travel Plan: {trip_plan.get('destination', 'Your Trip')}", title_style))
    elements.append(Spacer(1, 20))
    
    # Trip Overview
    elements.append(Paragraph("Trip Overview", heading_style))
    overview_data = [
        ['Traveler', trip_request.get('traveler_name', 'N/A')],
        ['Destination', trip_plan.get('destination', 'N/A')],
        ['Duration', f"{trip_request.get('days', 'N/A')} days"],
        ['Month', trip_request.get('month', 'N/A')],
        ['Budget', f"${trip_request.get('budget_total', 0):,.2f}"],
        ['From', trip_request.get('origin_city', 'N/A')]
    ]
    
    overview_table = Table(overview_data, colWidths=[2*inch, 3*inch])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    elements.append(overview_table)
    elements.append(PageBreak())
    
    # Itinerary
    elements.append(Paragraph("Day-by-Day Itinerary", heading_style))
    itinerary = trip_plan.get('itinerary', [])
    
    for day in itinerary:
        day_num = day.get('day', 1)
        day_title = day.get('title', 'Adventure Day')
        
        elements.append(Paragraph(f"Day {day_num}: {day_title}", styles['Heading3']))
        
        day_details = f"""
        <b>Morning:</b> {day.get('morning', 'Start your day')}<br/>
        <b>Afternoon:</b> {day.get('afternoon', 'Explore')}<br/>
        <b>Evening:</b> {day.get('evening', 'Relax')}<br/>
        """
        
        if day.get('meal_suggestions'):
            meals = ', '.join(day['meal_suggestions'][:2])
            day_details += f"<b>Recommended Meals:</b> {meals}"
        
        elements.append(Paragraph(day_details, styles['Normal']))
        elements.append(Spacer(1, 12))
    
    elements.append(PageBreak())
    
    # Budget Analysis
    elements.append(Paragraph("Budget Analysis", heading_style))
    budget_info = trip_plan.get('budget_analysis', {})
    
    if budget_info:
        breakdown = budget_info.get('breakdown', {})
        if breakdown:
            budget_data = [['Category', 'Amount']]
            total = 0
            for category, amount in breakdown.items():
                budget_data.append([category.title(), f"${amount:,.2f}"])
                total += amount
            budget_data.append(['TOTAL', f"${total:,.2f}"])
            
            budget_table = Table(budget_data)
            budget_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.green),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            elements.append(budget_table)
    
    # Safety Information
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Safety Information", heading_style))
    safety_info = trip_plan.get('safety_info', {})
    
    if safety_info:
        safety_text = f"""
        <b>Safety Level:</b> {safety_info.get('safety_level', 'Medium')}<br/>
        <b>Visa Required:</b> {'Yes' if safety_info.get('visa_required') else 'No'}<br/>
        <b>Weather:</b> {safety_info.get('weather_advisory', 'Check forecast')}<br/>
        """
        elements.append(Paragraph(safety_text, styles['Normal']))
        
        tips = safety_info.get('safety_tips', [])
        if tips:
            elements.append(Paragraph("<b>Safety Tips:</b>", styles['Normal']))
            for tip in tips[:5]:
                elements.append(Paragraph(f"• {tip}", styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Chat Popup Component (Modal-like)
def render_chat_popup():
    """Render chat as a popup modal"""
    with st.container():
        # Chat header
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.markdown("### 💬 AI Travel Assistant")
        with col3:
            if st.button("❌", key="close_chat", help="Close chat"):
                st.session_state.show_chat = False
                st.rerun()
        
        # Chat messages container
        chat_container = st.container()
        with chat_container:
            # Show messages
            for msg in st.session_state.chat_messages:
                if msg.get("type") == "user":
                    st.markdown(f'<div class="user-msg">👤 {msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="ai-msg">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
        
        # Quick questions
        if st.session_state.current_trip_plan:
            st.markdown("**Quick Questions:**")
            col1, col2, col3 = st.columns(3)
            
            questions = ["What's the budget?", "Show day 1", "Safety tips?"]
            
            for idx, (col, question) in enumerate(zip([col1, col2, col3], questions)):
                with col:
                    if st.button(question, key=f"quick_{idx}"):
                        # Add to messages
                        st.session_state.chat_messages.append({"type": "user", "content": question})
                        
                        # Get response
                        with st.spinner("AI thinking..."):
                            response = get_llm_response(question, st.session_state.current_trip_plan)
                        
                        st.session_state.chat_messages.append({"type": "ai", "content": response})
                        st.rerun()
        
        # Input area
        st.markdown("---")
        with st.form(key="chat_form", clear_on_submit=True):
            user_input = st.text_input("Ask anything about your trip...", key=f"chat_input_{st.session_state.chat_input_counter}")
            col1, col2 = st.columns([3, 1])
            
            with col2:
                submitted = st.form_submit_button("Send 📤", use_container_width=True)
            
            if submitted and user_input:
                # Add user message
                st.session_state.chat_messages.append({"type": "user", "content": user_input})
                
                # Get AI response
                with st.spinner("AI thinking..."):
                    response = get_llm_response(user_input, st.session_state.current_trip_plan)
                
                st.session_state.chat_messages.append({"type": "ai", "content": response})
                st.session_state.chat_input_counter += 1
                st.rerun()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()

# Login Page
def render_login_page():
    """Render login/signup page"""
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                ✈️ AI Travel Planner
            </h1>
            <p>Your intelligent travel companion with multi-agent AI</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Guest login
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎯 Continue as Guest", use_container_width=True):
            login_as_guest()
            st.success("Welcome, Guest!")
            time.sleep(1)
            st.rerun()
    
    st.markdown("---")
    
    # Login/Signup tabs
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            st.markdown("**Login to your account**")
            email = st.text_input("Email", placeholder="demo@example.com")
            password = st.text_input("Password", type="password", placeholder="demo123")
            
            if st.form_submit_button("Login", use_container_width=True):
                if email and password:
                    success, message = login_user(email, password)
                    if success:
                        st.success(message)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please enter email and password")
    
    with tab2:
        with st.form("signup_form"):
            st.markdown("**Create new account**")
            name = st.text_input("Full Name")
            email = st.text_input("Email Address")
            password = st.text_input("Password", type="password")
            origin_city = st.text_input("Your City", value="Hyderabad")
            
            if st.form_submit_button("Sign Up", use_container_width=True):
                if name and email and password:
                    success, message = signup_user(email, name, password, origin_city)
                    if success:
                        st.success(message)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please fill all fields")

# Dashboard Page
def render_dashboard():
    """Render main dashboard"""
    st.header("🏠 Dashboard")
    
    # Welcome card
    user_name = st.session_state.user_info.get('name', 'User')
    st.markdown(f"""
        <div class="trip-card">
            <h2>Welcome back, {user_name}! 👋</h2>
            <p>Ready to plan your next adventure?</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🗺️ Mode", "Guest" if st.session_state.guest_mode else "Member")
    
    with col2:
        trips_count = len(st.session_state.guest_trips) if st.session_state.guest_mode else 0
        st.metric("✈️ Trips", trips_count)
    
    with col3:
        st.metric("💬 AI Chat", "Available")
    
    st.markdown("---")
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✈️ Plan New Trip", use_container_width=True):
            st.session_state.current_page = "Plan Trip"
            st.rerun()
    
    with col2:
        if st.button("📚 View History", use_container_width=True):
            st.session_state.current_page = "History"
            st.rerun()
    
    # Current trip preview
    if st.session_state.current_trip_plan:
        st.markdown("---")
        st.subheader("📍 Current Trip")
        
        plan = st.session_state.current_trip_plan
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"**Destination:** {plan.get('destination', 'Unknown')}")
        
        with col2:
            budget = plan.get('budget_analysis', {}).get('total', 0)
            st.info(f"**Budget:** ${budget:,.0f}")
        
        with col3:
            if REPORTLAB_AVAILABLE and st.session_state.current_trip_request:
                pdf_buffer = generate_trip_pdf(plan, st.session_state.current_trip_request)
                if pdf_buffer:
                    st.download_button(
                        "📄 Download PDF",
                        data=pdf_buffer,
                        file_name=f"trip_{plan.get('destination', 'plan').replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

# Trip Planning Page
def render_trip_planning():
    """Render trip planning page"""
    st.header("✈️ Plan Your Trip")
    
    if st.session_state.guest_mode:
        st.info("🎯 **Guest Mode:** Your trips are temporary. Sign up to save permanently!")
    
    # Trip form
    with st.form("trip_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            traveler_name = st.text_input("Your Name", value=st.session_state.user_info.get('name', 'Traveler'))
            origin_city = st.text_input("From City", value="Hyderabad")
            destination = st.text_input("Destination (optional)", placeholder="Leave blank for AI suggestion")
            visa_passport = st.text_input("Passport", value="Indian")
        
        with col2:
            days = st.slider("Duration (days)", 1, 14, 5)
            month = st.selectbox("Travel Month", 
                ["January", "February", "March", "April", "May", "June",
                 "July", "August", "September", "October", "November", "December"])
            budget = st.number_input("Budget (USD)", min_value=100.0, value=1500.0, step=100.0)
        
        interests = st.multiselect("Your Interests",
            ["beach", "mountains", "culture", "history", "food", "adventure",
             "wildlife", "shopping", "nightlife", "relaxation", "photography"],
            default=["culture", "food"])
        
        submitted = st.form_submit_button("🚀 Generate Trip Plan", use_container_width=True)
        
        if submitted:
            if not interests:
                st.error("⚠️ Please select at least one interest!")
            else:
                with st.spinner("🤖 AI agents are planning your trip..."):
                    # Prepare request
                    trip_request = {
                        "traveler_name": traveler_name,
                        "origin_city": origin_city,
                        "days": days,
                        "month": month,
                        "budget_total": budget,
                        "interests": interests,
                        "visa_passport": visa_passport,
                        "preferred_destination": destination if destination else ""
                    }
                    
                    # Store request for PDF
                    st.session_state.current_trip_request = trip_request
                    
                    # API call
                    endpoint = "/plan-guest" if st.session_state.guest_mode else "/plan"
                    response = make_api_request(endpoint, "POST", trip_request, 
                                              auth_required=not st.session_state.guest_mode)
                    
                    if response and response.status_code == 200:
                        plan = response.json()
                        st.session_state.current_trip_plan = plan
                        
                        # Save to guest trips if in guest mode
                        if st.session_state.guest_mode:
                            trip_record = {
                                "id": str(uuid.uuid4()),
                                "destination": plan.get('destination'),
                                "days": days,
                                "month": month,
                                "budget_total": budget,
                                "created_at": datetime.now().isoformat(),
                                "trip_data": plan
                            }
                            st.session_state.guest_trips.insert(0, trip_record)
                        
                        st.success("✅ Trip plan generated successfully!")
                        st.balloons()
                    else:
                        st.error("❌ Failed to generate trip plan. Please try again.")
    
    # Display trip if exists
    if st.session_state.current_trip_plan:
        display_trip_plan()

def display_trip_plan():
    """Display the generated trip plan"""
    plan = st.session_state.current_trip_plan
    
    st.markdown("---")
    
    # Trip header
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"""
            <div class="trip-card">
                <h2>📍 {plan.get('destination', 'Your Destination')}</h2>
                <p>Your personalized AI-generated travel plan</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Chat button
        if st.button("💬 Ask AI", use_container_width=True):
            st.session_state.show_chat = True
            st.rerun()
        
        # PDF export
        if REPORTLAB_AVAILABLE and st.session_state.current_trip_request:
            pdf_buffer = generate_trip_pdf(plan, st.session_state.current_trip_request)
            if pdf_buffer:
                st.download_button(
                    "📄 Export PDF",
                    data=pdf_buffer,
                    file_name=f"trip_{plan.get('destination', 'plan').replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        budget_info = plan.get('budget_analysis', {})
        total = budget_info.get('total', 0)
        st.metric("💰 Total Cost", f"${total:,.0f}")
    
    with col2:
        safety = plan.get('safety_info', {})
        level = safety.get('safety_level', 'Medium')
        st.metric("🛡️ Safety", level)
    
    with col3:
        itinerary = plan.get('itinerary', [])
        st.metric("📅 Days", len(itinerary))
    
    # Detailed information in tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📅 Itinerary", "💰 Budget", "🛡️ Safety", "📍 Highlights"])
    
    with tab1:
        itinerary = plan.get('itinerary', [])
        for day in itinerary:
            with st.expander(f"Day {day.get('day', 1)}: {day.get('title', 'Adventure')}"):
                st.write(f"**🌅 Morning:** {day.get('morning', 'N/A')}")
                st.write(f"**☀️ Afternoon:** {day.get('afternoon', 'N/A')}")
                st.write(f"**🌙 Evening:** {day.get('evening', 'N/A')}")
                if day.get('meal_suggestions'):
                    meals = ', '.join(day['meal_suggestions'][:2])
                    st.write(f"**🍽️ Recommended:** {meals}")
    
    with tab2:
        budget_info = plan.get('budget_analysis', {})
        breakdown = budget_info.get('breakdown', {})
        
        if breakdown:
            for category, amount in breakdown.items():
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**{category.title()}**")
                with col2:
                    st.write(f"${amount:,.0f}")
        
        tips = budget_info.get('budget_tips', [])
        if tips:
            st.write("**💡 Money-Saving Tips:**")
            for tip in tips:
                st.write(f"• {tip}")
    
    with tab3:
        safety_info = plan.get('safety_info', {})
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Safety Level:** {safety_info.get('safety_level', 'N/A')}")
            st.write(f"**Visa Required:** {'Yes ✅' if safety_info.get('visa_required') else 'No ❌'}")
        
        with col2:
            weather = safety_info.get('weather_advisory', '')
            if weather:
                st.write(f"**Weather:** {weather}")
        
        tips = safety_info.get('safety_tips', [])
        if tips:
            st.write("**🛡️ Safety Tips:**")
            for tip in tips[:5]:
                st.write(f"• {tip}")
        
        vaccinations = safety_info.get('vaccinations', [])
        if vaccinations:
            st.write("**💉 Vaccinations:**")
            for vaccine in vaccinations[:3]:
                st.write(f"• {vaccine}")
    
    with tab4:
        dest_info = plan.get('destination_info', {})
        
        reason = dest_info.get('reason', '')
        if reason:
            st.write(f"**Why {plan.get('destination')}?**")
            st.write(reason)
        
        highlights = dest_info.get('highlights', [])
        if highlights:
            st.write("**🌟 Must-See Highlights:**")
            for highlight in highlights:
                st.write(f"• {highlight}")

# Trip History Page
def render_trip_history():
    """Render trip history page"""
    st.header("📚 Trip History")
    
    if st.session_state.guest_mode:
        st.info("🎯 **Guest Mode:** Showing temporary session trips only")
        trips = st.session_state.guest_trips
    else:
        # Fetch from API
        response = make_api_request("/trips")
        if response and response.status_code == 200:
            trips = response.json().get('trips', [])
        else:
            trips = []
    
    if not trips:
        st.info("📭 No trips yet. Start planning your first adventure!")
        if st.button("✈️ Plan Your First Trip", use_container_width=True):
            st.session_state.current_page = "Plan Trip"
            st.rerun()
    else:
        st.write(f"**Total Trips:** {len(trips)}")
        
        for idx, trip in enumerate(trips):
            with st.expander(f"📍 {trip.get('destination', 'Unknown')} ({trip.get('days', 0)} days)"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**From:** {trip.get('origin_city', 'N/A')}")
                    st.write(f"**Month:** {trip.get('month', 'N/A')}")
                    st.write(f"**Budget:** ${trip.get('budget_total', 0):,.0f}")
                
                with col2:
                    created = trip.get('created_at', '')
                    if created:
                        try:
                            date = datetime.fromisoformat(created).strftime('%Y-%m-%d')
                            st.write(f"**Created:** {date}")
                        except:
                            pass
                
                # Action buttons
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button(f"View Details", key=f"view_{idx}_{trip.get('id', '')}"):
                        st.session_state.current_trip_plan = trip.get('trip_data', {})
                        st.session_state.current_page = "Plan Trip"
                        st.rerun()
                
                with col2:
                    if st.button(f"💬 Ask AI", key=f"chat_{idx}_{trip.get('id', '')}"):
                        st.session_state.current_trip_plan = trip.get('trip_data', {})
                        st.session_state.show_chat = True
                        st.rerun()

# Sidebar Navigation
def render_sidebar():
    """Render sidebar with navigation"""
    with st.sidebar:
        # User profile section
        if st.session_state.user_info:
            user = st.session_state.user_info
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea, #764ba2); 
                     color: white; padding: 1rem; border-radius: 10px; text-align: center;">
                    <h3 style="margin: 0; color: white;">👤 {user.get('name', 'User')}</h3>
                    <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.9;">
                        {user.get('email', '')}
                    </p>
                    {'<p style="margin: 0.25rem 0 0 0; font-size: 0.8rem;">🎯 Guest Mode</p>' if st.session_state.guest_mode else ''}
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation menu
        st.markdown("### 🧭 Navigation")
        
        menu_items = [
            ("🏠 Dashboard", "Dashboard"),
            ("✈️ Plan Trip", "Plan Trip"),
            ("📚 History", "History")
        ]
        
        for label, page in menu_items:
            if st.button(
                label, 
                use_container_width=True,
                key=f"nav_{page}",
                type="primary" if st.session_state.current_page == page else "secondary"
            ):
                st.session_state.current_page = page
                st.rerun()
        
        st.markdown("---")
        
        # Chat button
        if st.button("💬 AI Assistant", use_container_width=True, type="secondary"):
            st.session_state.show_chat = not st.session_state.show_chat
            st.rerun()
        
        st.markdown("---")
        
        # Logout
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.rerun()
        
        # Info section
        st.markdown("---")
        st.markdown("### ℹ️ Info")
        st.markdown("""
        <div style="font-size: 0.8rem; color: #666;">
            <p>✨ Features:</p>
            <ul style="margin: 0; padding-left: 1rem;">
                <li>Multi-Agent AI</li>
                <li>PDF Export</li>
                <li>Chat Assistant</li>
                <li>Mobile Friendly</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# Main Application
def main():
    """Main application entry point"""
    
    # Check if user is authenticated
    if not st.session_state.authenticated:
        render_login_page()
        return
    
    # Render sidebar
    render_sidebar()
    
    # Render current page
    if st.session_state.current_page == "Dashboard":
        render_dashboard()
    elif st.session_state.current_page == "Plan Trip":
        render_trip_planning()
    elif st.session_state.current_page == "History":
        render_trip_history()
    
    # Render chat popup if active
    if st.session_state.show_chat:
        # Create a floating container for chat
        with st.container():
            st.markdown("---")
            st.markdown("### 💬 AI Travel Assistant")
            
            # Create columns for better layout
            chat_col1, chat_col2 = st.columns([4, 1])
            
            with chat_col2:
                if st.button("❌ Close", key="close_chat_main"):
                    st.session_state.show_chat = False
                    st.rerun()
            
            # Render the chat interface
            render_chat_popup()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem; padding: 1rem;">
        <p>🤖 Powered by Multi-Agent AI System</p>
        <p>✈️ Your Intelligent Travel Companion | 📱 Mobile Optimized | 📄 PDF Export</p>
    </div>
    """, unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    main()
