# Utility functions
import json
import os
from datetime import datetime
from typing import List, Dict, Any

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load data from a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Invalid JSON in file: {file_path}")
        return {}

def save_json_file(file_path: str, data: Dict[str, Any]) -> bool:
    """Save data to a JSON file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving file {file_path}: {e}")
        return False

def load_text_file(file_path: str) -> str:
    """Load content from a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return ""

def chunk_text(text: str, chunk_size: int = 200, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks."""
    if not text:
        return []
    
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
        
        if i + chunk_size >= len(words):
            break
    
    return chunks

def format_date(date_str: str) -> str:
    """Format date string for display."""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%B %d, %Y")
    except ValueError:
        return date_str

def clean_text(text: str) -> str:
    """Clean and normalize text."""
    return text.strip().lower()

def find_keywords_in_text(text: str, keywords: List[str]) -> int:
    """Count keyword matches in text."""
    text_lower = text.lower()
    matches = 0
    for keyword in keywords:
        if keyword.lower() in text_lower:
            matches += 1
    return matches

def validate_file_exists(file_path: str) -> bool:
    """Check if a file exists."""
    return os.path.exists(file_path) and os.path.isfile(file_path)

def get_current_timestamp() -> str:
    """Get current timestamp as string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")