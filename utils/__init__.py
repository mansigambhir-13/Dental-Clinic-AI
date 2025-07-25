# Dental Clinic AI Assistant - Utils Package
"""
Utility functions for the dental clinic AI assistant.
"""

from .helpers import (
    load_json_file,
    save_json_file,
    load_text_file,
    chunk_text,
    format_date,
    clean_text,
    find_keywords_in_text,
    validate_file_exists,
    get_current_timestamp
)

__all__ = [
    'load_json_file',
    'save_json_file', 
    'load_text_file',
    'chunk_text',
    'format_date',
    'clean_text',
    'find_keywords_in_text',
    'validate_file_exists',
    'get_current_timestamp'
]