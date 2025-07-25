import json
import google.generativeai as genai
from typing import Dict, List, Optional
from .rag_system import RAGSystem
from config import Config

class DentalAssistantBot:
    def __init__(self):
        # Configure Gemini
        if Config.GEMINI_API_KEY:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
        else:
            self.model = None
        
        # Initialize RAG system with proper knowledge base file path
        try:
            self.rag_system = RAGSystem(
                knowledge_base_file=Config.KNOWLEDGE_BASE_FILE,
                embedding_model=getattr(Config, 'EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
            )
        except Exception as e:
            print(f"Failed to initialize RAG system: {e}")
            self.rag_system = None
        
        # Load FAQs and appointments
        self.faqs = self._load_json_file(Config.FAQS_FILE)
        self.appointments = self._load_json_file(Config.APPOINTMENTS_FILE)
        
        # System prompt
        self.system_prompt = f"""
        You are a helpful dental clinic assistant for {Config.CLINIC_NAME}.
        
        Clinic Information:
        - Name: {Config.CLINIC_NAME}
        - Address: {Config.CLINIC_ADDRESS}
        - Phone: {Config.CLINIC_PHONE}
        
        Your role:
        1. Answer frequently asked questions about dental procedures and clinic policies
        2. Help with appointment scheduling and availability
        3. Provide general dental health information
        4. Be friendly, professional, and empathetic
        
        Always prioritize patient safety and recommend professional consultation for serious concerns.
        """
    
    def _load_json_file(self, file_path: str) -> Dict:
        """Load JSON data from file with error handling"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return {}
        except json.JSONDecodeError:
            print(f"Invalid JSON in file: {file_path}")
            return {}
    
    def _search_faqs(self, query: str) -> Optional[str]:
        """Search for relevant FAQ"""
        if not self.faqs or 'faqs' not in self.faqs:
            return None
        
        query_lower = query.lower()
        
        for faq in self.faqs['faqs']:
            question = faq.get('question', '').lower()
            keywords = faq.get('keywords', [])
            
            # Check if query matches question or keywords
            if any(keyword.lower() in query_lower for keyword in keywords):
                return faq.get('answer', '')
            
            if any(word in question for word in query_lower.split()):
                return faq.get('answer', '')
        
        return None
    
    def _search_appointments(self, query: str) -> Optional[str]:
        """Search for appointment information"""
        if not self.appointments:
            return None
        
        query_lower = query.lower()
        appointment_keywords = ['appointment', 'booking', 'schedule', 'available', 'time', 'slot']
        
        if any(keyword in query_lower for keyword in appointment_keywords):
            # Return available appointments
            if 'available_slots' in self.appointments:
                slots = self.appointments['available_slots']
                if slots:
                    response = "Here are our available appointment slots:\n\n"
                    for slot in slots[:5]:  # Show first 5 slots
                        response += f"📅 {slot.get('date', 'N/A')} at {slot.get('time', 'N/A')}\n"
                    response += f"\nTo book an appointment, please call us at {Config.CLINIC_PHONE}"
                    return response
        
        return None
    
    def _get_rag_context(self, query: str) -> Optional[str]:
        """Get relevant context from knowledge base"""
        if not self.rag_system:
            return None
        
        try:
            context = self.rag_system.get_context(query, max_chunks=3)
            return context if context and context != "No relevant information found in knowledge base." else None
        except Exception as e:
            print(f"RAG search error: {e}")
            return None
    
    def _generate_ai_response(self, query: str, context: str = "") -> str:
        """Generate AI response using Gemini"""
        if not self.model:
            return "I'm sorry, but I'm unable to process your request right now. Please contact our clinic directly for assistance."
        
        try:
            # Combine system prompt, context, and query
            full_prompt = f"""
            {self.system_prompt}
            
            Context from knowledge base:
            {context}
            
            Patient question: {query}
            
            Please provide a helpful, accurate response based on the context and your knowledge of dental care.
            """
            
            response = self.model.generate_content(full_prompt)
            return response.text
            
        except Exception as e:
            print(f"AI generation error: {e}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again or contact our clinic directly."
    
    def process_query(self, query: str) -> str:
        """Process user query and return appropriate response"""
        if not query.strip():
            return "Hello! How can I help you today? You can ask about appointments, dental procedures, or general oral health questions."
        
        # Step 1: Check FAQs
        faq_response = self._search_faqs(query)
        if faq_response:
            return f"**FAQ:** {faq_response}"
        
        # Step 2: Check appointments
        appointment_response = self._search_appointments(query)
        if appointment_response:
            return appointment_response
        
        # Step 3: Get context from knowledge base
        rag_context = self._get_rag_context(query)
        
        # Step 4: Generate AI response
        if rag_context:
            return f"**Based on our knowledge base:**\n\n{self._generate_ai_response(query, rag_context)}"
        else:
            return self._generate_ai_response(query)
    
    def get_welcome_message(self) -> str:
        """Get welcome message for the chatbot"""
        return f"""
        👋 Welcome to {Config.CLINIC_NAME}!
        
        I'm your AI dental assistant. I can help you with:
        
        🦷 **Dental procedure information**
        📅 **Appointment scheduling**  
        ❓ **Frequently asked questions**
        💡 **General oral health advice**
        
        How can I assist you today?
        """