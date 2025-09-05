import streamlit as st
import requests
import json
from datetime import datetime

st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    div[data-testid="metric-container"] {
        background-color: #f0f2f6;
        border: 1px solid #e0e2e6;
        border-radius: 8px;
        padding: 10px;
        margin: 5px 0;
    }
    </style>
""", unsafe_allow_html=True)

st.title("✈️ AI Multi-Agent Travel Planner")
st.markdown("Let our AI agents collaborate to plan your perfect trip!")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    api_url = st.text_input("API URL", value="http://backend:8000")
    
    st.markdown("---")
    st.markdown("### 🤖 AI Agents")
    st.info("""
    **Active Agents:**
    - 📍 Destination Expert
    - 🗓️ Itinerary Planner
    - 💰 Budget Analyst
    - 🛡️ Safety Advisor
    """)

# Main form
col1, col2 = st.columns([2, 1])

with col1:
    with st.form("trip_form"):
        st.subheader("📝 Trip Details")
        
        col_a, col_b = st.columns(2)
        with col_a:
            traveler_name = st.text_input("Your Name", value="Alex")
            origin_city = st.text_input("Origin City", value="Hyderabad")
            visa_passport = st.text_input("Passport Nationality", value="Indian")
        
        with col_b:
            days = st.slider("Trip Duration (days)", 1, 14, 5)
            month = st.selectbox("Travel Month", 
                ["January", "February", "March", "April", "May", "June",
                 "July", "August", "September", "October", "November", "December"])
            budget_total = st.number_input("Total Budget (USD)", min_value=100.0, value=1500.0, step=100.0)
        
        st.subheader("🎯 Interests")
        interests = st.multiselect(
            "Select your interests",
            ["beach", "mountains", "culture", "history", "food", "adventure", 
             "wildlife", "shopping", "nightlife", "relaxation", "photography",
             "museums", "temples", "nature", "city tour"],
            default=["beach", "culture", "food"]
        )
        
        submitted = st.form_submit_button("🚀 Generate Travel Plan", use_container_width=True)

with col2:
    st.subheader("📊 Quick Stats")
    if 'plan' in st.session_state:
        plan = st.session_state.plan
        st.metric("Destination", plan['destination'])
        st.metric("Total Cost", f"${plan['budget_analysis']['total']:.2f}")
        st.metric("Per Day", f"${plan['budget_analysis']['daily_average']:.2f}")
        if plan['within_budget']:
            st.success("✅ Within Budget!")
        else:
            st.warning("⚠️ Over Budget")

# Process form submission
if submitted:
    with st.spinner("🤔 AI agents are planning your trip..."):
        payload = {
            "traveler_name": traveler_name,
            "origin_city": origin_city,
            "days": days,
            "month": month,
            "budget_total": budget_total,
            "interests": interests,
            "visa_passport": visa_passport
        }
        
        try:
            response = requests.post(f"{api_url}/plan", json=payload, timeout=60)
            
            if response.status_code == 200:
                plan = response.json()
                st.session_state.plan = plan
                
                # Display results in tabs
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "📍 Destination", 
                    "🗓️ Itinerary", 
                    "💰 Budget", 
                    "🛡️ Safety", 
                    "🤖 Agent Trace"
                ])
                
                with tab1:
                    st.header(f"Recommended Destination: {plan['destination']}")
                    dest_info = plan['destination_info']
                    
                    st.markdown(f"**Why this destination?** {dest_info.get('reason', 'Perfect match for your preferences!')}")
                    
                    if 'highlights' in dest_info:
                        st.subheader("✨ Highlights")
                        for highlight in dest_info['highlights']:
                            st.markdown(f"- {highlight}")
                
                with tab2:
                    st.header("Your Itinerary")
                    for day_plan in plan['itinerary']:
                        with st.expander(f"Day {day_plan['day']}: {day_plan.get('title', 'Adventure Awaits!')}", expanded=True):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"**Morning:** {day_plan.get('morning', 'Free time')}")
                                st.markdown(f"**Afternoon:** {day_plan.get('afternoon', 'Explore')}")
                                st.markdown(f"**Evening:** {day_plan.get('evening', 'Dinner')}")
                            
                            with col2:
                                st.markdown("**🍽️ Food Options:**")
                                for meal in day_plan.get('meal_suggestions', ['Local cuisine']):
                                    st.markdown(f"- {meal}")
                
                with tab3:
                    st.header("Budget Breakdown")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("💵 Cost Distribution")
                        breakdown = plan['budget_analysis']['breakdown']
                        for category, amount in breakdown.items():
                            st.metric(category.capitalize(), f"${amount:.2f}")
                    
                    with col2:
                        st.subheader("📊 Summary")
                        st.metric("Total Estimated Cost", f"${plan['budget_analysis']['total']:.2f}")
                        st.metric("Daily Average", f"${plan['budget_analysis']['daily_average']:.2f}")
                        
                        if 'budget_tips' in plan['budget_analysis']:
                            st.markdown("**💡 Money-Saving Tips:**")
                            for tip in plan['budget_analysis']['budget_tips']:
                                st.markdown(f"- {tip}")
                
                with tab4:
                    st.header("Safety Information")
                    safety = plan['safety_info']
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Safety Level", safety.get('safety_level', 'Unknown'))
                        st.metric("Visa Required", "Yes" if safety.get('visa_required') else "No")
                        
                        if 'weather_advisory' in safety:
                            st.info(f"🌤️ **Weather:** {safety['weather_advisory']}")
                    
                    with col2:
                        if 'vaccinations' in safety:
                            st.markdown("**💉 Recommended Vaccinations:**")
                            for vac in safety['vaccinations']:
                                st.markdown(f"- {vac}")
                        
                        if 'emergency_contacts' in safety:
                            st.markdown("**📞 Emergency Contacts:**")
                            for service, number in safety['emergency_contacts'].items():
                                st.markdown(f"- {service}: {number}")
                    
                    if 'safety_tips' in safety:
                        st.warning("⚠️ **Important Safety Tips:**")
                        for tip in safety['safety_tips']:
                            st.markdown(f"- {tip}")
                
                with tab5:
                    st.header("Agent Decision Process")
                    for msg in plan['agent_messages']:
                        with st.container():
                            st.markdown(f"**{msg['agent']}** ({msg['role']})")
                            st.info(msg['content'])
                            st.markdown("---")
                
                # Download button for the plan
                st.download_button(
                    label="📥 Download Travel Plan (JSON)",
                    data=json.dumps(plan, indent=2),
                    file_name=f"travel_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.Timeout:
            st.error("Request timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to the backend. Make sure the API is running on " + api_url)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Powered by Multi-Agent AI System | Built with FastAPI & Streamlit</p>
</div>
""", unsafe_allow_html=True)