# Mini Multi‑Agent Travel Planner — Python FastAPI + Streamlit UI
# ------------------------------------------------
# Backend: FastAPI (already defined)
# Frontend: Streamlit simple UI to interact with /plan endpoint
# ------------------------------------------------

# (The FastAPI backend code remains unchanged from the previous version.)

# =========================
# streamlit_app.py (Frontend)
# =========================
import streamlit as st
import requests

st.set_page_config(page_title="AI Travel Planner", layout="centered")

st.title("✈️ Multi‑Agent Travel Planner")

st.markdown("Enter your preferences and let AI agents plan your trip!")

# User input form
with st.form("trip_form"):
    traveler_name = st.text_input("Your name", value="Alex")
    origin_city = st.text_input("Origin city", value="Hyderabad")
    days = st.slider("Trip duration (days)", 1, 14, 5)
    month = st.selectbox("Travel month", ["January","March","June","August","November"])
    budget_total = st.number_input("Budget (USD)", min_value=100.0, value=900.0)
    interests = st.multiselect("Interests", ["beach","local food","museums","temples","wildlife","mountains"], default=["beach","local food","museums"])
    visa_passport = st.text_input("Passport nationality", value="Indian")

    submitted = st.form_submit_button("Generate Plan")

if submitted:
    with st.spinner("Planning your trip..."):
        payload = {
            "traveler_name": traveler_name,
            "origin_city": origin_city,
            "days": days,
            "month": month,
            "budget_total": budget_total,
            "interests": interests,
            "visa_passport": visa_passport,
        }
        try:
            resp = requests.post("http://127.0.0.1:8000/plan", json=payload)
            if resp.status_code == 200:
                plan = resp.json()

                st.success(f"Destination selected: {plan['destination']}")
                st.subheader("🗓 Itinerary")
                for day in plan["itinerary"]:
                    st.markdown(f"**Day {day['day']}**: {', '.join(day['highlights'])}")
                    st.caption(day["notes"])

                st.subheader("💰 Budget Estimate")
                st.json(plan["estimated_cost_breakdown"])
                st.markdown(f"Within budget: {'✅ Yes' if plan['within_budget'] else '❌ No'}")

                st.subheader("⚠️ Safety Notes")
                for note in plan["safety_notes"]:
                    st.markdown(f"- {note}")

                with st.expander("🔍 Agent Decision Trace"):
                    for m in plan["messages"]:
                        st.markdown(f"**{m['agent']} ({m['role']})**: {m['content']}")
            else:
                st.error(f"Backend error {resp.status_code}: {resp.text}")
        except Exception as e:
            st.error(f"Could not reach backend: {e}")

