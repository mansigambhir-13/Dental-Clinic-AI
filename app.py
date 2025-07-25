import streamlit as st
import os
from modules.chatbot import DentalAssistantBot
from modules.booking_system import BookingSystem
from config import Config

# Page configuration
st.set_page_config(
    page_title="Dental Clinic AI Assistant",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize session state variables."""
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'user_name' not in st.session_state:
        st.session_state.user_name = ""
    if 'user_phone' not in st.session_state:
        st.session_state.user_phone = ""
    if 'booking_mode' not in st.session_state:
        st.session_state.booking_mode = False
    if 'selected_slot' not in st.session_state:
        st.session_state.selected_slot = None

def check_gemini_key():
    """Check if Gemini API key is configured."""
    if not Config.GEMINI_API_KEY:
        st.error("🔑 Gemini API key not configured!")
        st.info("Please add your Gemini API key to the .env file:")
        st.code("GEMINI_API_KEY=your_api_key_here")
        return False
    return True

def initialize_chatbot():
    """Initialize the chatbot."""
    if st.session_state.chatbot is None:
        try:
            with st.spinner("Initializing AI assistant..."):
                st.session_state.chatbot = DentalAssistantBot()
            st.success("✅ AI Assistant ready!")
        except Exception as e:
            st.error(f"❌ Error initializing chatbot: {str(e)}")
            return False
    return True

def display_sidebar():
    """Display sidebar with clinic information and options."""
    with st.sidebar:
        st.title("🦷 Clinic Info")
        
        if st.session_state.chatbot:
            try:
                clinic_info = st.session_state.chatbot.get_clinic_info()
                
                st.info(f"""
                **{clinic_info.get('name', 'Dental Clinic')}**
                
                📍 {clinic_info.get('address', 'Address not available')}
                📞 {clinic_info.get('phone', 'Phone not available')}
                """)
                
                st.subheader("📊 System Status")
                # Safe dictionary access using .get() method
                st.write(f"Available Appointments: {clinic_info.get('available_slots', 0)}")
                st.write(f"FAQ Entries: {clinic_info.get('faqs_available', 0)}")
                st.write(f"Knowledge Chunks: {clinic_info.get('knowledge_chunks', 0)}")
                
            except Exception as e:
                st.warning(f"Could not load clinic info: {str(e)}")
                # Fallback display
                st.info(f"""
                **{Config.CLINIC_NAME}**
                
                📍 {Config.CLINIC_ADDRESS}
                📞 {Config.CLINIC_PHONE}
                """)
                st.subheader("📊 System Status")
                st.write("System initializing...")
        
        st.subheader("💡 Try asking:")
        example_questions = [
            "What are your office hours?",
            "Show me available appointments",
            "What is a root canal?",
            "Do you accept insurance?",
            "How much does a cleaning cost?"
        ]
        
        for question in example_questions:
            if st.button(question, key=f"example_{question[:10]}"):
                st.session_state.current_input = question
        
        st.subheader("🎯 Features")
        st.write("✅ FAQ Answering")
        st.write("✅ Appointment Booking")
        st.write("✅ Dental Knowledge")
        st.write("✅ AI-Powered Responses")
        
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

def handle_booking_flow(user_input, response_data):
    """Handle the appointment booking flow."""
    if response_data.get('additional_data', {}).get('action') == 'show_slots':
        available_slots = response_data['additional_data']['available_slots']
        
        st.write("**To book an appointment, please:**")
        
        # User information form
        with st.form("booking_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Your Name", value=st.session_state.user_name)
                
            with col2:
                phone = st.text_input("Phone Number", value=st.session_state.user_phone)
            
            # Slot selection
            slot_options = {}
            for slot in available_slots:
                slot_id = slot['id']
                slot_display = f"ID {slot_id}: {slot['date']} at {slot['time']} ({slot['type']})"
                slot_options[slot_display] = slot_id
            
            selected_slot_display = st.selectbox("Choose an appointment slot:", list(slot_options.keys()))
            selected_slot_id = slot_options[selected_slot_display]
            
            if st.form_submit_button("📅 Book This Appointment"):
                if name and phone:
                    # Attempt booking
                    booking_result = st.session_state.chatbot.booking_system.book_appointment(
                        selected_slot_id,
                        {'name': name, 'phone': phone}
                    )
                    
                    if booking_result['success']:
                        st.success(f"✅ {booking_result['message']}")
                        st.info(f"Booking ID: {booking_result['booking_id']}")
                        
                        # Save user info for future
                        st.session_state.user_name = name
                        st.session_state.user_phone = phone
                        
                        # Add booking confirmation to chat
                        booking_details = booking_result['appointment_details']
                        confirmation_msg = f"""
                        🎉 **Appointment Confirmed!**
                        
                        **Booking ID:** {booking_result['booking_id']}
                        **Patient:** {booking_details['patient_info']['name']}
                        **Date:** {booking_details['date']}
                        **Time:** {booking_details['time']}
                        **Type:** {booking_details['type']}
                        **Duration:** {booking_details['duration']}
                        
                        Please save your booking ID and arrive 15 minutes early.
                        """
                        
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": confirmation_msg
                        })
                        
                    else:
                        st.error(f"❌ {booking_result['message']}")
                else:
                    st.warning("Please provide your name and phone number.")

def display_chat_message(role, content):
    """Display a chat message."""
    if role == "user":
        with st.chat_message("user", avatar="👤"):
            st.write(content)
    else:
        with st.chat_message("assistant", avatar="🦷"):
            st.write(content)

def main():
    """Main application function."""
    st.title(Config.APP_TITLE)
    st.caption(Config.APP_DESCRIPTION)
    
    # Initialize session state
    initialize_session_state()
    
    # Check Gemini configuration
    if not check_gemini_key():
        return
    
    # Initialize chatbot
    if not initialize_chatbot():
        return
    
    # Display sidebar
    display_sidebar()
    
    # Display chat history
    for message in st.session_state.messages:
        display_chat_message(message["role"], message["content"])
    
    # Handle input from sidebar examples
    if 'current_input' in st.session_state:
        user_input = st.session_state.current_input
        del st.session_state.current_input
    else:
        # Chat input
        user_input = st.chat_input("Ask me about dental services, book an appointment, or get dental advice...")
    
    if user_input:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_input})
        display_chat_message("user", user_input)
        
        # Get bot response
        with st.spinner("Thinking..."):
            try:
                # Handle different response formats for backwards compatibility
                if hasattr(st.session_state.chatbot, 'process_message'):
                    response_data = st.session_state.chatbot.process_message(user_input)
                    bot_response = response_data['response']
                    intent = response_data.get('intent', 'general')
                else:
                    # Fallback to simple query processing
                    bot_response = st.session_state.chatbot.process_query(user_input)
                    intent = 'general'
                    response_data = {'response': bot_response, 'intent': intent}
                
                # Add to conversation history if method exists
                if hasattr(st.session_state.chatbot, 'add_to_conversation_history'):
                    st.session_state.chatbot.add_to_conversation_history(
                        user_input, bot_response, intent
                    )
                
                # Display bot response
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
                display_chat_message("assistant", bot_response)
                
                # Handle special booking flow
                if intent == 'booking' and response_data.get('additional_data'):
                    handle_booking_flow(user_input, response_data)
                
            except Exception as e:
                error_message = f"Sorry, I encountered an error: {str(e)}"
                st.session_state.messages.append({"role": "assistant", "content": error_message})
                display_chat_message("assistant", error_message)
        
        # Rerun to update the chat display
        st.rerun()

if __name__ == "__main__":
    main()