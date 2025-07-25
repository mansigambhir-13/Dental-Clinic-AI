import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Gemini Configuration - Works both locally and on Streamlit Cloud
    GEMINI_API_KEY = ""
    
    # Try to get API key from Streamlit secrets first, then from environment
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and "GEMINI_API_KEY" in st.secrets:
            GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
        else:
            GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    except ImportError:
        # If streamlit not available (local development), use .env
        GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    GEMINI_MODEL = "gemini-1.5-flash"
    
    # App Configuration
    APP_TITLE = "🦷 Dental Clinic AI Assistant"
    APP_DESCRIPTION = "Your friendly dental clinic assistant for FAQs, appointments, and information"
    
    # Data File Paths
    FAQS_FILE = "data/faqs.json"
    KNOWLEDGE_BASE_FILE = "data/knowledge_base.txt"
    APPOINTMENTS_FILE = "data/appointments.json"
    
    # RAG Configuration
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    MAX_CHUNKS = 3
    CHUNK_SIZE = 200
    
    # Appointment Configuration
    CLINIC_NAME = "Bright Smile Dental Clinic"
    CLINIC_ADDRESS = "123 Health Street, Medical District"
    CLINIC_PHONE = "(555) 123-DENT"