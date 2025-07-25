# Intent recognition
from typing import Dict, List
import re

class IntentClassifier:
    def __init__(self):
        self.intent_patterns = {
            'booking': [
                'book', 'schedule', 'appointment', 'reserve', 'available',
                'slot', 'time', 'when can', 'make appointment', 'see doctor',
                'visit', 'come in'
            ],
            'faq': [
                'hours', 'cost', 'price', 'insurance', 'location', 'where',
                'phone', 'contact', 'accept', 'how much', 'when open',
                'services', 'do you', 'emergency'
            ],
            'knowledge': [
                'what is', 'how to', 'tell me about', 'explain', 'information',
                'learn', 'treatment', 'procedure', 'pain', 'care', 'recovery',
                'healing', 'advice', 'recommend', 'cleaning', 'filling',
                'crown', 'root canal', 'whitening', 'braces', 'implant'
            ]
        }

    def classify_intent(self, user_input: str) -> str:
        """
        Classify user intent based on keyword matching.
        Returns: 'booking', 'faq', 'knowledge', or 'general'
        """
        user_input_lower = user_input.lower()
        
        # Score each intent
        intent_scores = {}
        for intent, keywords in self.intent_patterns.items():
            score = 0
            for keyword in keywords:
                if keyword in user_input_lower:
                    score += 1
            intent_scores[intent] = score
        
        # Find the intent with highest score
        if max(intent_scores.values()) > 0:
            return max(intent_scores, key=intent_scores.get)
        
        # Check for specific booking phrases
        booking_phrases = [
            'book an appointment', 'schedule appointment', 'make appointment',
            'available times', 'free slots', 'when can i come'
        ]
        for phrase in booking_phrases:
            if phrase in user_input_lower:
                return 'booking'
        
        # Check for question words (likely FAQ)
        question_words = ['what', 'when', 'where', 'how', 'why', 'who', 'which']
        for word in question_words:
            if user_input_lower.startswith(word):
                return 'faq'
        
        # Default to knowledge if unsure
        return 'knowledge'

    def get_confidence_score(self, user_input: str, intent: str) -> float:
        """Get confidence score for a classified intent."""
        user_input_lower = user_input.lower()
        keywords = self.intent_patterns.get(intent, [])
        
        matches = sum(1 for keyword in keywords if keyword in user_input_lower)
        return min(matches / len(keywords), 1.0) if keywords else 0.0

    def suggest_intent_examples(self) -> Dict[str, List[str]]:
        """Provide example phrases for each intent."""
        return {
            'booking': [
                "I'd like to book an appointment",
                "When are you available next week?",
                "Schedule me for a cleaning"
            ],
            'faq': [
                "What are your office hours?",
                "Do you accept my insurance?",
                "How much does a cleaning cost?"
            ],
            'knowledge': [
                "What is a root canal?",
                "How do I care for my teeth after surgery?",
                "Tell me about teeth whitening options"
            ]
        }