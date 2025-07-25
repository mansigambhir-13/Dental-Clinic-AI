# Dental Clinic AI Assistant - Modules Package
"""
This package contains the core modules for the dental clinic AI assistant:

- chatbot: Main chatbot logic and OpenAI integration
- rag_system: Retrieval-Augmented Generation system
- booking_system: Appointment booking and management
- intent_classifier: User intent recognition
"""

__version__ = "1.0.0"
__author__ = "Dental AI Assistant Team"

# Import main classes for easy access
from .chatbot import DentalAssistantBot
from .rag_system import RAGSystem
from .booking_system import BookingSystem
from .intent_classifier import IntentClassifier

__all__ = [
    'DentalAssistantBot',
    'RAGSystem', 
    'BookingSystem',
    'IntentClassifier'
]