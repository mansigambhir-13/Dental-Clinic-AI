#!/usr/bin/env python3
"""
Quick setup script for the Dental Clinic AI Assistant
Run this to verify your installation and test the system.
"""

import os
import sys
import json
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists and print status."""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - NOT FOUND")
        return False

def check_dependencies():
    """Check if required packages are installed."""
    print("\n🔍 Checking Dependencies...")
    
    required_packages = [
        'streamlit', 'google-generativeai', 'sentence_transformers', 
        'numpy', 'pandas', 'scikit-learn', 'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def check_project_structure():
    """Check if all required files exist."""
    print("\n📁 Checking Project Structure...")
    
    required_files = [
        ('app.py', 'Main application'),
        ('requirements.txt', 'Dependencies'),
        ('config.py', 'Configuration'),
        ('data/faqs.json', 'FAQ data'),
        ('data/knowledge_base.txt', 'Knowledge base'),
        ('data/appointments.json', 'Appointment data'),
        ('modules/__init__.py', 'Modules package'),
        ('modules/chatbot.py', 'Chatbot module'),
        ('modules/rag_system.py', 'RAG system'),
        ('modules/booking_system.py', 'Booking system'),
        ('modules/intent_classifier.py', 'Intent classifier'),
        ('utils/__init__.py', 'Utils package'),
        ('utils/helpers.py', 'Helper functions')
    ]
    
    all_exist = True
    for file_path, description in required_files:
        if not check_file_exists(file_path, description):
            all_exist = False
    
    return all_exist

def check_environment():
    """Check environment configuration."""
    print("\n🔑 Checking Environment...")
    
    env_file = '.env'
    if os.path.exists(env_file):
        print(f"✅ Environment file: {env_file}")
        
        # Check if API key is set
        with open(env_file, 'r') as f:
            content = f.read()
            if 'GEMINI_API_KEY=' in content and 'your_gemini_api_key_here' not in content:
                print("✅ Gemini API key appears to be configured")
                return True
            else:
                print("⚠️  Gemini API key not properly configured")
                print("Please add your actual API key to .env file")
                return False
    else:
        print(f"❌ Environment file: {env_file} - NOT FOUND")
        print("Create .env file with: GEMINI_API_KEY=your_api_key_here")
        return False

def test_data_files():
    """Test if data files are valid."""
    print("\n📊 Testing Data Files...")
    
    # Test FAQ JSON
    try:
        with open('data/faqs.json', 'r') as f:
            faq_data = json.load(f)
            if 'faqs' in faq_data and len(faq_data['faqs']) > 0:
                print(f"✅ FAQ data: {len(faq_data['faqs'])} entries")
            else:
                print("⚠️  FAQ data seems empty")
    except Exception as e:
        print(f"❌ FAQ data error: {e}")
    
    # Test knowledge base
    try:
        with open('data/knowledge_base.txt', 'r') as f:
            kb_content = f.read()
            if len(kb_content.strip()) > 100:
                print(f"✅ Knowledge base: {len(kb_content)} characters")
            else:
                print("⚠️  Knowledge base seems too short")
    except Exception as e:
        print(f"❌ Knowledge base error: {e}")
    
    # Test appointments
    try:
        with open('data/appointments.json', 'r') as f:
            apt_data = json.load(f)
            available = len([s for s in apt_data.get('available_slots', []) if s.get('available')])
            print(f"✅ Appointments: {available} available slots")
    except Exception as e:
        print(f"❌ Appointments error: {e}")

def run_system_test():
    """Run a basic system test."""
    print("\n🧪 Running System Test...")
    
    try:
        # Import and test basic functionality
        from modules.intent_classifier import IntentClassifier
        from modules.rag_system import RAGSystem
        from modules.booking_system import BookingSystem
        
        # Test intent classifier
        classifier = IntentClassifier()
        intent = classifier.classify_intent("What are your hours?")
        print(f"✅ Intent classification: '{intent}' for 'What are your hours?'")
        
        # Test RAG system
        rag = RAGSystem()
        if len(rag.knowledge_chunks) > 0:
            print(f"✅ RAG system: {len(rag.knowledge_chunks)} knowledge chunks loaded")
        else:
            print("⚠️  RAG system: No knowledge chunks loaded")
        
        # Test booking system
        booking = BookingSystem()
        available = len(booking.get_available_slots())
        print(f"✅ Booking system: {available} available slots")
        
        return True
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
        return False

def main():
    """Run all checks."""
    print("🦷 Dental Clinic AI Assistant - Setup Verification")
    print("=" * 50)
    
    checks = [
        check_project_structure(),
        check_dependencies(),
        check_environment(),
        test_data_files(),
        run_system_test()
    ]
    
    print("\n" + "=" * 50)
    
    if all(checks):
        print("🎉 ALL CHECKS PASSED!")
        print("\nYou're ready to run the application:")
        print("streamlit run app.py")
    else:
        print("⚠️  SOME CHECKS FAILED")
        print("\nPlease fix the issues above before running the application.")
        print("Refer to README.md for troubleshooting.")
    
    print("\n📚 Next steps:")
    print("1. Fix any failed checks")
    print("2. Run: streamlit run app.py")
    print("3. Test the chatbot functionality")
    print("4. Record your demo video")

if __name__ == "__main__":
    main()