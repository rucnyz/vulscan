import re
from html import unescape

script_pattern = re.compile(r'<script.*?>.*?</script>', re.IGNORECASE | re.DOTALL)
on_event_pattern = re.compile(r'\s+on\w+\s*=', re.IGNORECASE)
def sanitize_html(html_content: str) -> str:
    # First, decode HTML entities
    decoded_content = unescape(html_content)
    
    # Then, apply sanitization
    # Remove script tags
    sanitized = script_pattern.sub('', decoded_content)
    # Remove on* event attributes
    sanitized = on_event_pattern.sub(' ', sanitized)
    
    # Additional safety measures
    # Remove data: and javascript: URLs
    sanitized = re.sub(r'(data|javascript):', '', sanitized, flags=re.IGNORECASE)
    
    # Remove potentially dangerous attributes
    sanitized = re.sub(r'\s+(href|src|style)\s*=\s*".*?"', '', sanitized, flags=re.IGNORECASE)
    return sanitized