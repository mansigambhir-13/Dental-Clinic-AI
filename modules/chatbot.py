import google.generativeai as genai
import json
from typing import Dict, List, Optional
from utils.helpers import load_json_file, find_keywords_in_text
from modules.intent_classifier import IntentClassifier
from modules.booking_system import BookingSystem
from modules.rag_system import RAGSystem
from config import Config

class DentalAssistantBot:
    def __init__(self):
        # Initialize Gemini
        if Config.GEMINI_API_KEY:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
        else:
            self.model = None
        
        # Initialize components
        self.intent_classifier = IntentClassifier()
        self.booking_system = BookingSystem()
        self.rag_system = RAGSystem()
        
        # Load FAQ data
        self.faqs_data = load_json_file(Config.FAQS_FILE)
        self.faqs = self.faqs_data.get('faqs', [])
        
        # Conversation context
        self.conversation_history = []
        self.user_context = {}

    def process_message(self, user_input: str) -> Dict:
        """
        Main method to process user input and return appropriate response.
        """
        if not user_input.strip():
            return {
                'response': "I didn't receive any message. How can I help you today?",
                'intent': 'general',
                'additional_data': None
            }

        # Classify intent
        intent = self.intent_classifier.classify_intent(user_input)
        
        # Route to appropriate handler
        if intent == 'faq':
            return self._handle_faq(user_input)
        elif intent == 'booking':
            return self._handle_booking(user_input)
        elif intent == 'knowledge':
            return self._handle_knowledge_query(user_input)
        else:
            return self._handle_general_query(user_input)

    def _handle_faq(self, user_input: str) -> Dict:
        """Handle FAQ-related queries."""
        best_match = None
        best_score = 0
        
        for faq in self.faqs:
            # Check keywords in question
            keywords = faq.get('keywords', [])
            score = find_keywords_in_text(user_input, keywords)
            
            # Also check similarity to the question itself
            question_words = faq['question'].lower().split()
            question_score = find_keywords_in_text(user_input, question_words)
            
            total_score = score + question_score * 0.5
            
            if total_score > best_score:
                best_score = total_score
                best_match = faq

        if best_match and best_score > 0:
            response = f"**{best_match['question']}**\n\n{best_match['answer']}"
            
            return {
                'response': response,
                'intent': 'faq',
                'additional_data': {
                    'matched_faq': best_match,
                    'confidence': min(best_score / 3, 1.0)
                }
            }
        else:
            # If no FAQ match, try knowledge base
            return self._handle_knowledge_query(user_input)

    def _handle_booking(self, user_input: str) -> Dict:
        """Handle appointment booking queries."""
        # Check if user is asking for available slots
        if any(word in user_input.lower() for word in ['available', 'slots', 'times', 'when']):
            available_slots = self.booking_system.get_available_slots(5)
            
            if available_slots:
                response = "Here are our available appointment slots:\n\n"
                for i, slot in enumerate(available_slots, 1):
                    response += f"**{i}. {self.booking_system.format_slot_display(slot)}**\n\n"
                
                response += "\n💡 To book an appointment, please tell me:\n"
                response += "- Your preferred slot ID\n"
                response += "- Your name and phone number\n"
                response += "- Type of appointment needed"
                
                return {
                    'response': response,
                    'intent': 'booking',
                    'additional_data': {
                        'available_slots': available_slots,
                        'action': 'show_slots'
                    }
                }
            else:
                return {
                    'response': "I'm sorry, but there are no available appointment slots at the moment. Please call us at " + Config.CLINIC_PHONE + " for assistance.",
                    'intent': 'booking',
                    'additional_data': None
                }
        
        # Generic booking response
        response = f"""I'd be happy to help you book an appointment! 

Here's what I can help you with:
- 📅 Show available appointment slots
- 🕐 Find specific times or dates
- 🦷 Schedule different types of appointments

To get started, you can say:
- "Show me available appointments"
- "I need a cleaning appointment"
- "What times are available next week?"

Or call us directly at {Config.CLINIC_PHONE}."""

        return {
            'response': response,
            'intent': 'booking',
            'additional_data': {
                'action': 'booking_info'
            }
        }

    def _handle_knowledge_query(self, user_input: str) -> Dict:
        """Handle knowledge-based queries using RAG."""
        rag_result = self.rag_system.answer_question_with_context(user_input)
        
        if rag_result['has_context']:
            # Use Gemini to generate response with context
            try:
                response = self._generate_ai_response(user_input, rag_result['context'])
                return {
                    'response': response,
                    'intent': 'knowledge',
                    'additional_data': {
                        'context_used': True,
                        'relevant_chunks': len(rag_result['relevant_chunks'])
                    }
                }
            except Exception as e:
                print(f"Error generating AI response: {e}")
                # Fallback to context only
                return {
                    'response': f"Based on our dental knowledge:\n\n{rag_result['context'][:500]}...",
                    'intent': 'knowledge',
                    'additional_data': {
                        'context_used': True,
                        'ai_error': str(e)
                    }
                }
        else:
            return self._handle_general_query(user_input)

    def _handle_general_query(self, user_input: str) -> Dict:
        """Handle general queries with AI assistance."""
        try:
            system_prompt = f"""You are a helpful dental clinic assistant for {Config.CLINIC_NAME}. 
            Provide helpful, professional, and friendly responses about dental care and services. 
            If you don't know something specific about our clinic, suggest they call {Config.CLINIC_PHONE} for more information.
            Keep responses concise but informative."""
            
            response = self._generate_ai_response(user_input, "", system_prompt)
            
            return {
                'response': response,
                'intent': 'general',
                'additional_data': {
                    'ai_generated': True
                }
            }
        except Exception as e:
            print(f"Error with AI response: {e}")
            return {
                'response': f"I'm here to help with your dental questions! You can ask me about:\n\n• Our services and procedures\n• Appointment booking\n• General dental care\n• Office hours and location\n\nWhat would you like to know?",
                'intent': 'general',
                'additional_data': {
                    'ai_error': str(e)
                }
            }

    def _generate_ai_response(self, user_input: str, context: str = "", system_prompt: str = "") -> str:
        """Generate response using Gemini API."""
        if not self.model:
            raise Exception("Gemini API key not configured")

        # Construct the prompt
        prompt_parts = []
        
        # Add system prompt
        if system_prompt:
            prompt_parts.append(f"Instructions: {system_prompt}")
        else:
            prompt_parts.append(f"You are a helpful dental clinic assistant for {Config.CLINIC_NAME}. Provide professional and friendly dental advice.")
        
        # Add context if available
        if context:
            prompt_parts.append(f"Context from our knowledge base:\n{context}")
        
        # Add user question
        prompt_parts.append(f"User question: {user_input}")
        prompt_parts.append("Please provide a helpful response:")
        
        full_prompt = "\n\n".join(prompt_parts)

        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=300,
                    temperature=0.7,
                )
            )
            
            return response.text.strip()
            
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

    def get_clinic_info(self) -> Dict:
        """Get basic clinic information."""
        return {
            'name': Config.CLINIC_NAME,
            'address': Config.CLINIC_ADDRESS,
            'phone': Config.CLINIC_PHONE,
            'available_slots': len(self.booking_system.get_available_slots()),
            'knowledge_chunks': len(self.rag_system.knowledge_chunks),
            'faqs_available': len(self.faqs)
        }

    def add_to_conversation_history(self, user_input: str, bot_response: str, intent: str):
        """Add exchange to conversation history."""
        self.conversation_history.append({
            'user_input': user_input,
            'bot_response': bot_response,
            'intent': intent,
            'timestamp': Config.get_current_timestamp() if hasattr(Config, 'get_current_timestamp') else 'N/A'
        })
        
        # Keep only last 10 exchanges
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]

    def set_user_context(self, key: str, value: str):
        """Set user context information."""
        self.user_context[key] = value

    def get_user_context(self, key: str) -> Optional[str]:
        """Get user context information."""
        return self.user_context.get(key)