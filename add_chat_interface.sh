#!/bin/bash
# add_chat_interface.sh - Add Phase 3A Chat Interface

echo "💬 ADDING PHASE 3A: CHAT INTERFACE..."

# Create backup
cp streamlit_app.py streamlit_app.py.backup_phase2

# Add the chat interface to streamlit_app.py
python3 << 'EOF'
import re

# Read current file
with open('streamlit_app.py', 'r') as f:
    content = f.read()

# Add chat imports after existing imports
new_imports = '''import uuid
from typing import List, Dict
import asyncio

'''

# Add after the datetime import
content = content.replace('from datetime import datetime', 'from datetime import datetime\n' + new_imports)

# Add chat CSS to the existing CSS section
chat_css = '''
    
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
'''

# Add chat CSS to existing CSS section (before the closing </style>)
content = content.replace('    .stApp { background: #fafafa; }', '    .stApp { background: #fafaba; }' + chat_css)

# Add chat functions before the main() function
chat_functions = '''

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
        content = f"Great choice! I can help you find the perfect destination. 🎯\\n\\n"
        
        if any(country in message_lower for country in ["japan", "tokyo", "kyoto"]):
            content += "Japan is incredible! Cherry blossoms in spring, amazing food, rich culture. Let me get our budget analyst involved for cost planning.\\n\\n"
        elif any(country in message_lower for country in ["europe", "paris", "london", "italy"]):
            content += "Europe offers incredible diversity! From Paris's romance to Italy's cuisine to London's history. What draws you to Europe?\\n\\n"
        else:
            content += "What type of experience interests you? Adventure, culture, relaxation, food scenes?\\n\\n"
        
        content += "Tell me about your budget and timeframe!"
    
    elif any(word in message_lower for word in ["budget", "cost", "price", "$", "expensive"]):
        agent_type = "budget"
        content = "Perfect! Let me help with budget planning! 💰\\n\\n"
        content += "I can break down costs for:\\n"
        content += "• ✈️ Flights\\n• 🏨 Accommodation\\n• 🍽️ Food & drinks\\n• 🎯 Activities\\n• 🚌 Local transport\\n\\n"
        content += "What's your total budget and destination?"
    
    elif any(word in message_lower for word in ["days", "weeks", "duration"]):
        agent_type = "itinerary"
        content = "Time planning is key! 🗓️\\n\\n"
        content += "I recommend:\\n• 3-5 days: City exploration\\n• 1 week: Country highlights\\n• 2+ weeks: Multi-destination\\n\\n"
        content += "How many days do you have and where to?"
    
    elif any(word in message_lower for word in ["safe", "visa", "passport"]):
        agent_type = "safety"
        content = "Safety first! 🛡️\\n\\n"
        content += "I provide:\\n• Visa requirements\\n• Safety ratings\\n• Health recommendations\\n• Emergency contacts\\n\\n"
        content += "Which destination and what's your passport country?"
    
    else:
        agent_type = "assistant"
        if any(word in message_lower for word in ["hello", "hi", "hey"]):
            content = "Hello! Welcome to your AI travel team! 👋\\n\\n"
            content += "Meet your specialists:\\n🎯 Destination Expert\\n💰 Budget Analyst\\n🗓️ Itinerary Planner\\n🛡️ Safety Advisor\\n\\n"
            content += "Just tell me your travel dreams!"
        else:
            content = "I'm here to help plan your perfect trip! 🌍\\n\\n"
            content += "Share with me:\\n• Where you want to go\\n• Your budget range\\n• How many days\\n• What you love doing\\n\\n"
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
            "Hi! I'm your AI travel assistant with a team of specialists! 🌍\\n\\n"
            "🎯 **Destination Expert** - finds amazing places\\n"
            "💰 **Budget Analyst** - manages your money\\n"
            "🗓️ **Itinerary Planner** - creates daily plans\\n"
            "🛡️ **Safety Advisor** - keeps you safe\\n\\n"
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

'''

# Insert chat functions before main() function
content = content.replace('def main():', chat_functions + 'def main():')

# Update the navigation in render_sidebar to include chat
old_nav = 'nav_options = ["🏠 Dashboard", "✈️ Plan New Trip", "📚 Trip History", "⚙️ Settings"]'
new_nav = 'nav_options = ["🏠 Dashboard", "💬 AI Chat", "✈️ Plan New Trip", "📚 Trip History", "⚙️ Settings"]'

content = content.replace(old_nav, new_nav)

# Add chat page routing in main() function
old_routing = '''    if page == "🏠 Dashboard":
        render_dashboard()
    elif page == "✈️ Plan New Trip":
        render_trip_planning()
    elif page == "📚 Trip History":
        render_trip_history()
    elif page == "⚙️ Settings":
        render_settings()'''

new_routing = '''    if page == "🏠 Dashboard":
        render_dashboard()
    elif page == "💬 AI Chat":
        render_ai_chat_page()
    elif page == "✈️ Plan New Trip":
        render_trip_planning()
    elif page == "📚 Trip History":
        render_trip_history()
    elif page == "⚙️ Settings":
        render_settings()'''

content = content.replace(old_routing, new_routing)

# Write back the updated file
with open('streamlit_app.py', 'w') as f:
    f.write(content)

print("✅ Phase 3A Chat Interface added successfully!")
EOF

# Restart frontend to apply changes
docker-compose -f docker-compose.prod.yml restart frontend

echo "⏳ Restarting frontend with chat interface..."
sleep 15

echo ""
echo "🎉 PHASE 3A: CHAT INTERFACE DEPLOYED!"
echo ""
echo "✅ New Features Added:"
echo "  💬 AI Chat page in navigation"
echo "  🤖 Multi-agent conversation system"
echo "  🎯 Smart intent detection"
echo "  💡 Quick reply suggestions"
echo "  🎨 Beautiful chat bubbles and design"
echo ""
echo "🧪 Test the Chat Interface:"
echo "  1. Go to your app: http://34.123.121.132"
echo "  2. Click '💬 AI Chat' in the sidebar"
echo "  3. Start chatting: 'I want to visit Japan for 7 days'"
echo "  4. Try quick replies and different agents"
echo ""
echo "🚀 Phase 3A Complete!"
echo "   Next: Phase 3B will add trip generation from chat"
