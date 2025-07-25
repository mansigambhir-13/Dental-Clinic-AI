# 🦷 Dental Clinic AI Assistant

A comprehensive AI-powered chatbot for dental clinics that handles FAQs, appointment booking, and provides dental knowledge using RAG (Retrieval-Augmented Generation).

## 🌟 Features

- **💬 Smart FAQ System**: Answers common dental clinic questions
- **📅 Appointment Booking**: Browse and book available appointment slots
- **🧠 Knowledge Base**: Uses RAG to answer dental procedure questions
- **🤖 AI-Powered Responses**: Leverages Google Gemini for natural conversations
- **🎨 User-Friendly Interface**: Clean Streamlit web interface
- **📊 Real-Time Updates**: Live appointment availability

## 🚀 Quick Start

## Loom Video 
https://www.loom.com/share/d57da945afa649dd85d70471c89985bc

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key
- Internet connection

### Installation

1. **Clone or create the project structure:**
```bash
mkdir dental-clinic-assistant
cd dental-clinic-assistant
```

2. **Create the project files** (copy all files from the implementation)

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
# Create .env file
echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env
```

5. **Run the application:**
```bash
streamlit run app.py
```

## 📁 Project Structure

```
dental-clinic-assistant/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── config.py             # Configuration settings
├── .env                  # Environment variables
├── data/
│   ├── faqs.json         # FAQ database
│   ├── knowledge_base.txt # Dental knowledge content
│   └── appointments.json  # Mock appointment data
├── modules/
│   ├── chatbot.py        # Main chatbot logic
│   ├── rag_system.py     # RAG implementation
│   ├── booking_system.py # Appointment management
│   └── intent_classifier.py # Intent recognition
└── utils/
    └── helpers.py        # Utility functions
```

## 🔧 Configuration

### Gemini API Key

1. Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Add it to the `.env` file:
```bash
GEMINI_API_KEY=AIzaSyABC123_your-actual-api-key-here
```

### Customization

Edit `config.py` to customize:
- Clinic information (name, address, phone)
- AI model settings
- RAG parameters
- File paths

## 💡 Usage Examples

### FAQ Questions
- "What are your office hours?"
- "Do you accept insurance?"
- "How much does a cleaning cost?"

### Appointment Booking
- "I'd like to book an appointment"
- "Show me available times"
- "Schedule me for next week"

### Dental Knowledge
- "What is a root canal?"
- "How do I care for my teeth after surgery?"
- "Tell me about teeth whitening"

## 🧪 Testing the System

1. **Start the application:**
```bash
streamlit run app.py
```

2. **Test each component:**
   - Ask an FAQ question
   - Request appointment booking
   - Ask about a dental procedure

3. **Check the logs** for any errors in the terminal

## 🔍 System Components

### Intent Classification
The system automatically determines if users want:
- **FAQ**: Quick answers to common questions
- **Booking**: Appointment scheduling
- **Knowledge**: Detailed dental information

### RAG System
- Chunks dental knowledge into searchable segments
- Uses sentence transformers for semantic search
- Provides relevant context to the AI model

### Booking System
- Displays available appointment slots
- Handles booking confirmations
- Manages appointment data in JSON format

## 🛠️ Troubleshooting

### Common Issues

1. **"Gemini API key not configured"**
   - Ensure your `.env` file exists with the correct API key
   - Check that the key starts with `AIzaSy`

2. **"Error loading embedding model"**
   - Make sure you have internet connection
   - Try running: `pip install sentence-transformers --upgrade`

3. **"File not found" errors**
   - Ensure all data files exist in the `data/` directory
   - Check file permissions

4. **Application won't start**
   - Verify Python version: `python --version`
   - Install requirements: `pip install -r requirements.txt`

### Debug Mode

Add this to see detailed logs:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Adding Your Own Data

### Custom FAQs
Edit `data/faqs.json`:
```json
{
  "question": "Your question here?",
  "answer": "Your answer here.",
  "keywords": ["keyword1", "keyword2"]
}
```

### Knowledge Base
Add content to `data/knowledge_base.txt`:
```text
Your dental procedure information here.
Each paragraph will be processed separately.
```

### Appointment Slots
Modify `data/appointments.json` to reflect your actual availability.

## 🎥 Demo Video

Record a demo showing:
1. Starting the application
2. Asking an FAQ question
3. Booking an appointment
4. Getting dental knowledge

## 🔮 Future Enhancements

- **Voice Input/Output**: Add speech recognition and text-to-speech
- **Database Integration**: Replace JSON with proper database
- **Real-time Calendar**: Integrate with actual scheduling systems
- **Multi-language Support**: Add language options
- **Analytics Dashboard**: Track usage and popular questions

## 📝 Development Notes

### Key Dependencies
- **Streamlit**: Web interface framework
- **google-generativeai**: Google Gemini API for AI responses
- **sentence-transformers**: Text embeddings for RAG
- **scikit-learn**: Similarity calculations

### Architecture
- Modular design for easy maintenance
- Separation of concerns (intent, booking, knowledge)
- JSON-based data storage for simplicity
- Error handling and fallback mechanisms

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Test thoroughly
4. Submit a pull request

## 📄 License

This project is for educational purposes. Modify as needed for your use case.

## 📞 Support

For questions or issues:
1. Check the troubleshooting section
2. Review the code comments
3. Test with simple inputs first
4. Verify all dependencies are installed

---

**Built with ❤️ for dental professionals and their patients**
